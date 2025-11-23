"""
Pulselytics Backend API Server
Flask REST API for social media analytics dashboard
"""
import os
import time
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import sys

# Add parent and scripts directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scripts_dir = os.path.join(parent_dir, 'scripts')
sys.path.insert(0, parent_dir)
sys.path.insert(0, scripts_dir)

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from pydantic import BaseModel, ValidationError, field_validator
from typing import Literal

from common import DATA_DIR
from analyze_data import load_all, compute_summary, extract_hashtags
from ml_models import predictor as _predictor_inst, detector as _detector_inst
from ml_models.storage import load_registry

# Lightweight structured logging for ML routes
def ml_log(name: str):
    """Decorator to log ML endpoint execution duration and success state."""
    def _decorator(fn):
        def _wrapped(*args, **kwargs):
            t0 = time.perf_counter()
            ok = True
            try:
                resp = fn(*args, **kwargs)
                return resp
            except Exception as e:
                ok = False
                raise
            finally:
                duration_ms = int((time.perf_counter() - t0) * 1000)
                logger.info({
                    'event': 'ml_route',
                    'path': request.path,
                    'name': name,
                    'duration_ms': duration_ms,
                    'ok': ok,
                    'predictor_loaded': getattr(_predictor_inst, 'is_trained', False),
                    'anomaly_loaded': getattr(_detector_inst, 'is_trained', False)
                })
        _wrapped.__name__ = fn.__name__
        return _wrapped
    return _decorator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database functions
try:
    from database import (
        init_database, get_api_key, save_api_key, get_all_api_keys, 
        delete_api_key, log_scrape, get_scrape_history,
        create_client as db_create_client,
        get_client as db_get_client,
        get_all_clients as db_get_all_clients,
        update_client as db_update_client,
        delete_client as db_delete_client
    )
    DATABASE_ENABLED = True
    # Initialize database on startup
    init_database()
except ImportError as e:
    logger.warning(f"Database not available: {e}. Using JSON file storage.")
    DATABASE_ENABLED = False

app = Flask(__name__)
# Allow any localhost port for dev (e.g., Vite may use 5173, 5174, etc.)
CORS(app, resources={
    r"/*": {
        "origins": [r"http://localhost:\d+", r"http://127.0.0.1:\d+"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# Data directory for clients
CLIENT_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(CLIENT_DATA_DIR, exist_ok=True)


# ----------------------------------------------------------------------------
# Request/Response logging and basic error handling
# ----------------------------------------------------------------------------
@app.before_request
def _log_request():
    try:
        logger.info(f"REQ {request.method} {request.path}")
    except Exception:
        # best-effort logging only
        pass


@app.after_request
def _after_request(response):
    """Add CORS headers to all responses"""
    origin = request.headers.get('Origin')
    try:
        # Permit any localhost/127.0.0.1 origin in dev
        if origin and (origin.startswith('http://localhost:') or origin.startswith('http://127.0.0.1:')):
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
    except Exception:
        # best-effort only
        pass
    return response


@app.errorhandler(404)
def _not_found(e):
    logger.warning(f"404 NOT FOUND: {request.method} {request.path}")
    return jsonify({'success': False, 'error': 'Not Found', 'path': request.path}), 404


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

@app.route('/favicon.ico', methods=['GET'])
def _favicon():
    """Return empty favicon to avoid noisy 404s when browsers request /favicon.ico.
    Using 204 No Content keeps logs clean without adding a static asset.
    """
    from flask import Response
    return Response(status=204, mimetype='image/x-icon')

def get_scraper_mode() -> str:
    """Detect scraper mode from environment or default to lightweight"""
    return os.getenv('SCRAPER_MODE', 'lightweight')


def load_client_data(client_id: str) -> Optional[Dict]:
    """Load client data from JSON file"""
    filepath = os.path.join(CLIENT_DATA_DIR, f'{client_id}.json')
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_client_data(client_id: str, data: Dict) -> bool:
    """Save client data to JSON file"""
    try:
        filepath = os.path.join(CLIENT_DATA_DIR, f'{client_id}.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving client data: {e}")
        return False


def list_all_clients() -> List[Dict]:
    """List all client files in data directory"""
    clients = []
    for filename in os.listdir(CLIENT_DATA_DIR):
        if filename.endswith('.json'):
            client_id = filename[:-5]
            data = load_client_data(client_id)
            if data:
                clients.append({
                    'id': client_id,
                    'name': data.get('name', client_id),
                    'platforms': data.get('platforms', {}),
                    'last_updated': data.get('last_updated', None)
                })
    return clients


def filter_data_by_date(df: pd.DataFrame, date_range: str) -> pd.DataFrame:
    """Filter DataFrame by date range (handles tz-aware vs naive datetime)"""
    if df.empty or 'upload_date' not in df.columns:
        return df

    # Ensure upload_date is timezone-aware in UTC for consistent comparisons
    df['upload_date'] = pd.to_datetime(df['upload_date'], errors='coerce', utc=True)
    now = datetime.now(timezone.utc)

    if date_range == '7days':
        cutoff = now - timedelta(days=7)
    elif date_range == '30days':
        cutoff = now - timedelta(days=30)
    elif date_range == '90days':
        cutoff = now - timedelta(days=90)
    else:
        return df

    return df[df['upload_date'] >= cutoff]


def compute_engagement_trend(df: pd.DataFrame) -> List[Dict]:
    """Compute daily engagement metrics"""
    if df.empty or 'upload_date' not in df.columns:
        return []

    df = df.copy()
    # Normalize to UTC to avoid tz comparison issues
    df['upload_date'] = pd.to_datetime(df['upload_date'], errors='coerce', utc=True)
    df = df.dropna(subset=['upload_date'])

    # Use UTC date for grouping
    df['date'] = df['upload_date'].dt.date
    df['engagement'] = df['likes'].fillna(0) + df['comments'].fillna(0)

    trend = df.groupby('date')['engagement'].mean().reset_index()
    trend['date'] = trend['date'].astype(str)

    return trend.to_dict('records')


def get_platform_distribution(df: pd.DataFrame) -> List[Dict]:
    """Get post count by platform"""
    if df.empty or 'platform' not in df.columns:
        return []
    
    dist = df.groupby('platform').size().reset_index(name='posts')
    return dist.to_dict('records')


def get_top_posts(df: pd.DataFrame, n: int = 10) -> List[Dict]:
    """Get top performing posts by engagement"""
    if df.empty:
        return []
    
    df = df.copy()
    df['engagement'] = df['likes'].fillna(0) + df['comments'].fillna(0) * 2
    top = df.nlargest(n, 'engagement')
    
    return top.to_dict('records')


def get_hashtag_stats(df: pd.DataFrame) -> List[Dict]:
    """Extract and count hashtags"""
    if df.empty or 'caption' not in df.columns:
        return []
    
    hashtags = []
    for caption in df['caption'].dropna():
        hashtags.extend(extract_hashtags(caption))
    
    from collections import Counter
    counts = Counter(hashtags)
    
    return [{'hashtag': tag, 'count': count} for tag, count in counts.most_common(20)]


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'scraper_mode': get_scraper_mode()
    })


@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({'pong': True, 'ts': datetime.now().isoformat()})


@app.route('/api/clients', methods=['GET'])
def get_clients():
    """Get all clients"""
    try:
        clients = list_all_clients()
        return jsonify({
            'success': True,
            'clients': clients,
            'count': len(clients)
        })
    except Exception as e:
        logger.error(f"Error fetching clients: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Alias routes without /api prefix (fallback for environments where /api is proxied)
@app.route('/clients', methods=['GET'])
def get_clients_alias():
    return get_clients()


@app.route('/api/clients/<client_id>', methods=['GET'])
def get_client(client_id: str):
    """Get specific client data"""
    try:
        data = load_client_data(client_id)
        if not data:
            return jsonify({'success': False, 'error': 'Client not found'}), 404
        
        return jsonify({
            'success': True,
            'client': data
        })
    except Exception as e:
        logger.error(f"Error fetching client {client_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/clients/<client_id>', methods=['GET'])
def get_client_alias(client_id: str):
    return get_client(client_id)


@app.route('/api/clients', methods=['POST'])
def create_client():
    """Create new client"""
    try:
        data = request.get_json()
        
        if not data or 'id' not in data or 'name' not in data:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        client_id = data['id']
        
        # Check if client already exists
        if load_client_data(client_id):
            return jsonify({'success': False, 'error': 'Client already exists'}), 409
        
        # Add timestamp
        data['created_at'] = datetime.now().isoformat()
        data['last_updated'] = datetime.now().isoformat()
        
        # Save client data
        if save_client_data(client_id, data):
            return jsonify({
                'success': True,
                'client': data
            }), 201
        else:
            return jsonify({'success': False, 'error': 'Failed to save client'}), 500
            
    except Exception as e:
        logger.error(f"Error creating client: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/clients', methods=['POST'])
def create_client_alias():
    return create_client()


@app.route('/api/clients/<client_id>', methods=['PUT'])
def update_client(client_id: str):
    """Update client data"""
    try:
        existing = load_client_data(client_id)
        if not existing:
            return jsonify({'success': False, 'error': 'Client not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Merge with existing data
        existing.update(data)
        existing['last_updated'] = datetime.now().isoformat()
        
        if save_client_data(client_id, existing):
            return jsonify({
                'success': True,
                'client': existing
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to update client'}), 500
            
    except Exception as e:
        logger.error(f"Error updating client {client_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/clients/<client_id>', methods=['PUT'])
def update_client_alias(client_id: str):
    return update_client(client_id)


@app.route('/api/clients/<client_id>', methods=['DELETE'])
def delete_client(client_id: str):
    """Delete client"""
    try:
        filepath = os.path.join(CLIENT_DATA_DIR, f'{client_id}.json')
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Client not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting client {client_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/clients/<client_id>', methods=['DELETE'])
def delete_client_alias(client_id: str):
    return delete_client(client_id)


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data with optional filtering"""
    try:
        # Get query parameters
        client = request.args.get('client', '')
        date_range = request.args.get('range', 'all')
        platform = request.args.get('platform', 'all')
        search = request.args.get('search', '')  # Search/username filter
        
        # Load all data
        df = load_all()
        
        if df.empty:
            return jsonify({
                'success': True,
                'data': {
                    'total_posts': 0,
                    'avg_likes': 0,
                    'avg_comments': 0,
                    'avg_views': 0,
                    'trend': [],
                    'platforms': [],
                    'top_posts': [],
                    'hashtags': []
                }
            })
        
        # Filter by client if provided
        if client and 'username' in df.columns:
            # Try to treat `client` as a client id from our registry first
            client_data = load_client_data(client)
            if client_data and isinstance(client_data, dict):
                platforms = client_data.get('platforms', {}) or {}
                # Collect configured platform usernames/handles (non-empty)
                usernames = [str(v) for v in platforms.values() if v]
                if usernames:
                    # Normalize both sides to compare handles like "@MrBeast" with "mrbeast"
                    import pandas as _pd
                    norm_list = [u.lower().lstrip('@').strip() for u in usernames]
                    tmp = df.copy()
                    tmp['_norm_user'] = (
                        tmp['username']
                        .astype(str)
                        .str.lower()
                        .str.replace('@', '', regex=False)
                        .str.strip()
                    )
                    # Also restrict to only the platforms explicitly configured for this client
                    allowed_platforms = [k for k, v in platforms.items() if v]
                    if 'platform' in tmp.columns and allowed_platforms:
                        tmp = tmp[tmp['platform'].isin(allowed_platforms)]

                    df = tmp[tmp['_norm_user'].isin(norm_list)].drop(columns=['_norm_user'])
                else:
                    # Fall back to substring match if no usernames configured
                    df = df[df['username'].str.contains(client, case=False, na=False)]
            else:
                # Fall back to substring search for ad-hoc text input
                df = df[df['username'].str.contains(client, case=False, na=False)]
        
        # Filter by search query (username, content, hashtags)
        if search:
            search_mask = False
            if 'username' in df.columns:
                search_mask |= df['username'].str.contains(search, case=False, na=False)
            if 'content' in df.columns:
                search_mask |= df['content'].str.contains(search, case=False, na=False)
            if 'caption' in df.columns:
                search_mask |= df['caption'].str.contains(search, case=False, na=False)
            if 'title' in df.columns:
                search_mask |= df['title'].str.contains(search, case=False, na=False)
            if 'hashtags' in df.columns:
                search_mask |= df['hashtags'].str.contains(search, case=False, na=False)
            
            df = df[search_mask]
        
        # Filter by platform
        if platform != 'all' and 'platform' in df.columns:
            df = df[df['platform'] == platform]
        
        # Filter by date range
        if date_range != 'all':
            df = filter_data_by_date(df, date_range)
        
        # Compute metrics
        summary = compute_summary(df)
        trend = compute_engagement_trend(df)
        platforms = get_platform_distribution(df)
        top_posts = get_top_posts(df, 10)
        hashtags = get_hashtag_stats(df)
        
        return jsonify({
            'success': True,
            'data': {
                **summary,
                'trend': trend,
                'platforms': platforms,
                'top_posts': top_posts,
                'hashtags': hashtags
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching analytics: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/clients/<client_id>/posts', methods=['GET'])
def get_client_posts(client_id: str):
    """Get posts for specific client"""
    try:
        client_data = load_client_data(client_id)
        if not client_data:
            return jsonify({'success': False, 'error': 'Client not found'}), 404
        
        # Load all data
        df = load_all()
        
        if df.empty:
            return jsonify({
                'success': True,
                'posts': []
            })
        
        # Filter by client platforms
        platforms = client_data.get('platforms', {})
        usernames = [v for k, v in platforms.items() if v]
        
        if 'username' in df.columns and usernames:
            df = df[df['username'].isin(usernames)]
        
        # Get query parameters
        limit = int(request.args.get('limit', 50))
        sort_by = request.args.get('sort', 'upload_date')
        
        # Sort and limit
        if sort_by in df.columns:
            df = df.sort_values(sort_by, ascending=False)
        
        posts = df.head(limit).to_dict('records')
        
        return jsonify({
            'success': True,
            'posts': posts,
            'count': len(posts)
        })
        
    except Exception as e:
        logger.error(f"Error fetching posts for client {client_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/clients/<client_id>/posts', methods=['GET'])
def get_client_posts_alias(client_id: str):
    return get_client_posts(client_id)


@app.route('/api/scrape', methods=['POST'])
def trigger_scrape():
    """Trigger scraping for specific client/platform"""
    import subprocess
    import threading
    
    try:
        data = request.get_json()
        
        if not data or 'client_id' not in data:
            return jsonify({'success': False, 'error': 'Missing client_id'}), 400
        
        client_id = data['client_id']
        platforms_to_scrape = data.get('platforms', ['all'])
        
        client_data = load_client_data(client_id)
        if not client_data:
            return jsonify({'success': False, 'error': 'Client not found'}), 404
        
        # Get platform usernames
        platforms = client_data.get('platforms', {})
        
        # Function to run scrapers in background
        def run_scrapers():
            import os
            root_dir = os.path.dirname(os.path.dirname(__file__))
            python_exe = os.path.join(root_dir, 'venv', 'Scripts', 'python.exe')
            
            results = {}
            
            # Check if API keys are available
            youtube_api_key = None
            facebook_api_key = None
            instagram_api_key = None
            
            if DATABASE_ENABLED:
                try:
                    yt_key_data = get_api_key('youtube')
                    if yt_key_data:
                        youtube_api_key = yt_key_data['api_key']
                        logger.info("✅ Using saved YouTube API key")
                    
                    fb_key_data = get_api_key('facebook')
                    if fb_key_data:
                        facebook_api_key = fb_key_data.get('access_token') or fb_key_data.get('api_key')
                        logger.info("✅ Using saved Facebook API key")
                    
                    ig_key_data = get_api_key('instagram')
                    if ig_key_data:
                        instagram_api_key = ig_key_data.get('access_token') or ig_key_data.get('api_key')
                        logger.info("✅ Using saved Instagram API key")
                except Exception as e:
                    logger.warning(f"Could not load API keys: {e}")
            
            # Instagram
            if ('all' in platforms_to_scrape or 'instagram' in platforms_to_scrape) and platforms.get('instagram'):
                try:
                    logger.info(f"Scraping Instagram: @{platforms['instagram']}")
                    
                    # Use API if key available, otherwise fallback to web scraping
                    if instagram_api_key:
                        logger.info("Using Instagram Graph API")
                        script = 'scrape_instagram_api.py'
                        env = os.environ.copy()
                        env['INSTAGRAM_ACCESS_TOKEN'] = instagram_api_key
                        subprocess.run([
                            python_exe,
                            os.path.join(root_dir, script),
                            '--max-posts', '20'
                        ], cwd=root_dir, timeout=120, env=env)
                    else:
                        logger.info("Using web scraping (no API key)")
                        subprocess.run([
                            python_exe,
                            os.path.join(root_dir, 'scrape_instagram.py'),
                            '--username', platforms['instagram'],
                            '--max-posts', '10'
                        ], cwd=root_dir, timeout=120)
                    
                    results['instagram'] = 'success'
                    if DATABASE_ENABLED:
                        log_scrape(client_id, 'instagram', 'success', 
                                 scrape_method='api' if instagram_api_key else 'web')
                except Exception as e:
                    logger.error(f"Instagram scrape failed: {e}")
                    results['instagram'] = 'failed'
                    if DATABASE_ENABLED:
                        log_scrape(client_id, 'instagram', 'failed', error_message=str(e))
            
            # YouTube
            if ('all' in platforms_to_scrape or 'youtube' in platforms_to_scrape) and platforms.get('youtube'):
                try:
                    logger.info(f"Scraping YouTube: @{platforms['youtube']}")
                    
                    # Use API if key available, otherwise fallback to yt-dlp
                    if youtube_api_key:
                        logger.info("Using YouTube Data API v3")
                        script = 'scrape_youtube_api.py'
                        env = os.environ.copy()
                        env['YOUTUBE_API_KEY'] = youtube_api_key
                        subprocess.run([
                            python_exe,
                            os.path.join(root_dir, script),
                            '--channel', platforms['youtube'],
                            '--max-videos', '50'
                        ], cwd=root_dir, timeout=180, env=env)
                    else:
                        logger.info("Using yt-dlp (no API key)")
                        subprocess.run([
                            python_exe,
                            os.path.join(root_dir, 'scrape_youtube.py'),
                            '--channel', platforms['youtube'],
                            '--max-videos', '20'
                        ], cwd=root_dir, timeout=180)
                    
                    results['youtube'] = 'success'
                    if DATABASE_ENABLED:
                        log_scrape(client_id, 'youtube', 'success',
                                 scrape_method='api' if youtube_api_key else 'web')
                except Exception as e:
                    logger.error(f"YouTube scrape failed: {e}")
                    results['youtube'] = 'failed'
                    if DATABASE_ENABLED:
                        log_scrape(client_id, 'youtube', 'failed', error_message=str(e))
            
            # Twitter
            if ('all' in platforms_to_scrape or 'twitter' in platforms_to_scrape) and platforms.get('twitter'):
                try:
                    logger.info(f"Scraping Twitter: @{platforms['twitter']}")

                    # Prefer official API if bearer token is available; otherwise fallback to snscrape/web
                    twitter_bearer = None
                    if DATABASE_ENABLED:
                        try:
                            tw_key_data = get_api_key('twitter')
                            if tw_key_data:
                                # Allow token in access_token or api_key for flexibility
                                twitter_bearer = tw_key_data.get('access_token') or tw_key_data.get('api_key')
                                if twitter_bearer:
                                    logger.info("✅ Using saved Twitter API bearer token")
                        except Exception as e:
                            logger.warning(f"Could not load Twitter API key: {e}")

                    if twitter_bearer:
                        logger.info("Using Twitter API v2")
                        env = os.environ.copy()
                        env['TWITTER_BEARER_TOKEN'] = twitter_bearer
                        subprocess.run([
                            python_exe,
                            os.path.join(root_dir, 'scrape_twitter_api.py'),
                            '--username', platforms['twitter'],
                            '--max-posts', '50'
                        ], cwd=root_dir, timeout=180, env=env)
                        results['twitter'] = 'success'
                        if DATABASE_ENABLED:
                            log_scrape(client_id, 'twitter', 'success', scrape_method='api')
                    else:
                        logger.info("Using public scraper (no API token)")
                        subprocess.run([
                            python_exe,
                            os.path.join(root_dir, 'scrape_twitter.py'),
                            '--username', platforms['twitter'],
                            '--max-posts', '30'
                        ], cwd=root_dir, timeout=180)
                        results['twitter'] = 'success'
                        if DATABASE_ENABLED:
                            log_scrape(client_id, 'twitter', 'success', scrape_method='web')
                except Exception as e:
                    logger.error(f"Twitter scrape failed: {e}")
                    results['twitter'] = 'failed'
                    if DATABASE_ENABLED:
                        log_scrape(client_id, 'twitter', 'failed', error_message=str(e))
            
            # Facebook
            if ('all' in platforms_to_scrape or 'facebook' in platforms_to_scrape) and platforms.get('facebook'):
                try:
                    logger.info(f"Scraping Facebook: {platforms['facebook']}")
                    
                    # Use API if key available, otherwise fallback to web scraping
                    if facebook_api_key:
                        logger.info("Using Facebook Graph API")
                        script = 'scrape_facebook_api.py'
                        env = os.environ.copy()
                        env['FACEBOOK_ACCESS_TOKEN'] = facebook_api_key
                        subprocess.run([
                            python_exe,
                            os.path.join(root_dir, script),
                            '--page', platforms['facebook'],
                            '--max-posts', '30'
                        ], cwd=root_dir, timeout=180, env=env)
                    else:
                        logger.info("Using web scraping (no API key)")
                        subprocess.run([
                            python_exe,
                            os.path.join(root_dir, 'scrape_facebook.py'),
                            '--page', platforms['facebook'],
                            '--max-posts', '15'
                        ], cwd=root_dir, timeout=180)
                    
                    results['facebook'] = 'success'
                    if DATABASE_ENABLED:
                        log_scrape(client_id, 'facebook', 'success',
                                 scrape_method='api' if facebook_api_key else 'web')
                except Exception as e:
                    logger.error(f"Facebook scrape failed: {e}")
                    results['facebook'] = 'failed'
                    if DATABASE_ENABLED:
                        log_scrape(client_id, 'facebook', 'failed', error_message=str(e))
            
            logger.info(f"Scraping completed for {client_id}: {results}")
        
        # Start scraping in background thread
        thread = threading.Thread(target=run_scrapers, daemon=True)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': f'Scraping started for {client_id}',
            'platforms': platforms_to_scrape,
            'status': 'in_progress'
        })
        
    except Exception as e:
        logger.error(f"Error triggering scrape: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/scrape', methods=['POST'])
def trigger_scrape_alias():
    return trigger_scrape()


@app.route('/api/schedule/status', methods=['GET'])
def get_schedule_status():
    """Get scraper mode and schedule information"""
    mode = get_scraper_mode()
    
    platform_info = {
        'lightweight': {
            'instagram': {'method': 'instaloader', 'speed': '3-5s'},
            'youtube': {'method': 'yt-dlp', 'speed': '5-10s'},
            'facebook': {'method': 'facebook-scraper', 'speed': '10-15s'},
            'twitter': {'method': 'nitter', 'speed': '8-12s'}
        },
        'playwright': {
            'instagram': {'method': 'browser', 'speed': '15-25s'},
            'youtube': {'method': 'browser', 'speed': '20-30s'},
            'facebook': {'method': 'browser', 'speed': '20-30s'},
            'twitter': {'method': 'browser', 'speed': '15-20s'}
        }
    }
    
    return jsonify({
        'success': True,
        'scraper_mode': mode,
        'platforms': platform_info.get(mode, {}),
        'interval_minutes': int(os.getenv('SCRAPE_INTERVAL_MINUTES', 360))
    })


@app.route('/schedule/status', methods=['GET'])
def get_schedule_status_alias():
    return get_schedule_status()


@app.route('/api/stats/summary', methods=['GET'])
def get_summary_stats():
    """Get overall summary statistics"""
    try:
        df = load_all()
        
        if df.empty:
            return jsonify({
                'success': True,
                'stats': {
                    'total_posts': 0,
                    'total_platforms': 0,
                    'total_clients': 0,
                    'date_range': None
                }
            })
        
        # Compute stats
        total_posts = len(df)
        total_platforms = df['platform'].nunique() if 'platform' in df.columns else 0
        total_clients = len(list_all_clients())
        
        date_range = None
        if 'upload_date' in df.columns:
            df['upload_date'] = pd.to_datetime(df['upload_date'], errors='coerce')
            dates = df['upload_date'].dropna()
            if not dates.empty:
                date_range = {
                    'earliest': dates.min().isoformat(),
                    'latest': dates.max().isoformat()
                }
        
        return jsonify({
            'success': True,
            'stats': {
                'total_posts': total_posts,
                'total_platforms': total_platforms,
                'total_clients': total_clients,
                'date_range': date_range
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching summary stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# API KEY MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/api-keys', methods=['GET'])
def get_api_keys_endpoint():
    """Get all saved API keys (masked for security)"""
    if not DATABASE_ENABLED:
        return jsonify({
            'success': False,
            'error': 'Database not available',
            'keys': {}
        }), 503
    
    try:
        keys = get_all_api_keys()
        return jsonify({
            'success': True,
            'keys': keys
        })
    except Exception as e:
        logger.error(f"Error getting API keys: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/api-keys/<platform>', methods=['POST'])
def save_api_key_endpoint(platform: str):
    """Save an API key for a specific platform"""
    if not DATABASE_ENABLED:
        return jsonify({
            'success': False,
            'error': 'Database not available'
        }), 503
    
    try:
        # Safely parse JSON body
        data = request.get_json(silent=True)
        logger.info(f"Received API key save request for {platform}. Headers: {dict(request.headers)} Body: {data}")

        if not isinstance(data, dict):
            return jsonify({
                'success': False,
                'error': 'Invalid JSON payload'
            }), 400

        # Safely extract and strip values, handling None
        api_key = (data.get('api_key') or '').strip()
        api_secret = (data.get('api_secret') or '').strip() or None
        access_token = (data.get('access_token') or '').strip() or None
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key is required'
            }), 400
        
        # Validate platform
        valid_platforms = ['youtube', 'facebook', 'instagram', 'twitter']
        if platform.lower() not in valid_platforms:
            return jsonify({
                'success': False,
                'error': f'Invalid platform. Must be one of: {", ".join(valid_platforms)}'
            }), 400
        
        logger.info(f"Saving API key for {platform}...")
        success = save_api_key(
            platform=platform.lower(),
            api_key=api_key,
            api_secret=api_secret,
            access_token=access_token
        )
        
        if success:
            logger.info(f"✅ API key saved successfully for {platform}")
            return jsonify({
                'success': True,
                'message': f'{platform.title()} API key saved successfully'
            })
        else:
            logger.error(f"Failed to save API key for {platform}")
            return jsonify({
                'success': False,
                'error': 'Failed to save API key'
            }), 500
    except Exception as e:
        import traceback
        logger.error(f"Error saving API key for {platform}: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/api-keys/<platform>/validate', methods=['POST'])
def validate_api_key_endpoint(platform: str):
    """Validate an API key by making a test request"""
    if not DATABASE_ENABLED:
        return jsonify({
            'success': False,
            'error': 'Database not available'
        }), 503
    
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            'success': False,
            'error': 'Invalid JSON payload'
        }), 400
    api_key = data.get('api_key', '').strip()
    
    if not api_key:
        return jsonify({
            'success': False,
            'error': 'API key is required'
        }), 400
    
    try:
        # Platform-specific validation
        if platform.lower() == 'youtube':
            # Test YouTube API key
            try:
                from googleapiclient.discovery import build
                youtube = build('youtube', 'v3', developerKey=api_key)
                # Simple test request
                request_obj = youtube.channels().list(part='id', id='UCK8sQmJBp8GCxrOtXWBpyEA')  # Google Developers channel
                response = request_obj.execute()
                if response:
                    return jsonify({'success': True, 'valid': True, 'message': 'YouTube API key is valid'})
            except Exception as e:
                return jsonify({'success': True, 'valid': False, 'message': f'Invalid YouTube API key: {str(e)}'})

        elif platform.lower() == 'facebook':
            # Test Facebook API key
            import requests
            test_url = f'https://graph.facebook.com/v19.0/me?access_token={api_key}'
            response = requests.get(test_url, timeout=5)
            if response.status_code == 200:
                return jsonify({'success': True, 'valid': True, 'message': 'Facebook API key is valid'})
            else:
                return jsonify({'success': True, 'valid': False, 'message': f'Invalid Facebook API key: {response.json().get("error", {}).get("message", "Unknown error")}'})

        elif platform.lower() == 'instagram':
            # Test Instagram API key
            import requests
            test_url = f'https://graph.instagram.com/me?fields=id,username&access_token={api_key}'
            response = requests.get(test_url, timeout=5)
            if response.status_code == 200:
                return jsonify({'success': True, 'valid': True, 'message': 'Instagram API key is valid'})
            else:
                return jsonify({'success': True, 'valid': False, 'message': f'Invalid Instagram API key: {response.json().get("error", {}).get("message", "Unknown error")}'})

        elif platform.lower() == 'twitter':
            # Test Twitter API bearer token by resolving a known account
            import requests
            resp = requests.get(
                'https://api.twitter.com/2/users/by/username/TwitterDev',
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=5
            )
            if resp.status_code == 200 and resp.json().get('data', {}).get('id'):
                return jsonify({'success': True, 'valid': True, 'message': 'Twitter API bearer token is valid'})
            else:
                return jsonify({'success': True, 'valid': False, 'message': f'Invalid Twitter bearer token: HTTP {resp.status_code}'})

        else:
            # For other platforms, just return success (validation not implemented)
            return jsonify({'success': True, 'valid': True, 'message': f'{platform.title()} API key validation not implemented - key saved'})

    except Exception as e:
        logger.error(f"Error validating API key: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/api-keys/<platform>', methods=['DELETE'])
def delete_api_key_endpoint(platform: str):
    """Delete an API key for a specific platform"""
    if not DATABASE_ENABLED:
        return jsonify({
            'success': False,
            'error': 'Database not available'
        }), 503
    
    try:
        success = delete_api_key(platform=platform.lower())
        
        if success:
            return jsonify({
                'success': True,
                'message': f'{platform.title()} API key deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'API key not found'
            }), 404
    except Exception as e:
        logger.error(f"Error deleting API key: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Alias routes without /api prefix for API key management
@app.route('/api-keys', methods=['GET'])
def get_api_keys_alias():
    return get_api_keys_endpoint()


@app.route('/api-keys/<platform>', methods=['POST'])
def save_api_key_alias(platform: str):
    return save_api_key_endpoint(platform)


@app.route('/api-keys/<platform>/validate', methods=['POST'])
def validate_api_key_alias(platform: str):
    return validate_api_key_endpoint(platform)


@app.route('/api-keys/<platform>', methods=['DELETE'])
def delete_api_key_alias(platform: str):
    return delete_api_key_endpoint(platform)


@app.route('/api/profiles/suggest', methods=['GET'])
def suggest_profiles():
    """
    Suggest verified public profiles for a given platform and search query.
    Returns a curated list of known accessible public accounts.
    """
    platform = request.args.get('platform', '').lower()
    query = request.args.get('query', '').lower()
    
    # Curated list of verified public accounts with accessible data
    suggestions = {
        'instagram': [
            {'username': 'virat.kohli', 'name': 'Virat Kohli', 'verified': True, 'category': 'Sports'},
            {'username': 'cristiano', 'name': 'Cristiano Ronaldo', 'verified': True, 'category': 'Sports'},
            {'username': 'leomessi', 'name': 'Lionel Messi', 'verified': True, 'category': 'Sports'},
            {'username': 'nike', 'name': 'Nike', 'verified': True, 'category': 'Brand'},
            {'username': 'adidas', 'name': 'Adidas', 'verified': True, 'category': 'Brand'},
            {'username': 'redbull', 'name': 'Red Bull', 'verified': True, 'category': 'Brand'},
            {'username': 'natgeo', 'name': 'National Geographic', 'verified': True, 'category': 'Media'},
            {'username': 'nasa', 'name': 'NASA', 'verified': True, 'category': 'Organization'},
        ],
        'youtube': [
            {'username': '@NASA', 'name': 'NASA', 'verified': True, 'category': 'Science'},
            {'username': '@RCBVideos', 'name': 'Royal Challengers Bengaluru', 'verified': True, 'category': 'Sports'},
            {'username': '@CricketAustralia', 'name': 'Cricket Australia', 'verified': True, 'category': 'Sports'},
            {'username': '@FCBarcelona', 'name': 'FC Barcelona', 'verified': True, 'category': 'Sports'},
            {'username': '@realmadrid', 'name': 'Real Madrid', 'verified': True, 'category': 'Sports'},
            {'username': '@Nike', 'name': 'Nike', 'verified': True, 'category': 'Brand'},
            {'username': '@NatGeo', 'name': 'National Geographic', 'verified': True, 'category': 'Media'},
            {'username': '@TED', 'name': 'TED', 'verified': True, 'category': 'Education'},
        ],
        'twitter': [
            {'username': 'imVkohli', 'name': 'Virat Kohli', 'verified': True, 'category': 'Sports'},
            {'username': 'Cristiano', 'name': 'Cristiano Ronaldo', 'verified': True, 'category': 'Sports'},
            {'username': 'TeamMessi', 'name': 'Lionel Messi', 'verified': True, 'category': 'Sports'},
            {'username': 'Nike', 'name': 'Nike', 'verified': True, 'category': 'Brand'},
            {'username': 'adidas', 'name': 'Adidas', 'verified': True, 'category': 'Brand'},
            {'username': 'NASA', 'name': 'NASA', 'verified': True, 'category': 'Organization'},
            {'username': 'NatGeo', 'name': 'National Geographic', 'verified': True, 'category': 'Media'},
        ],
        'facebook': [
            {'username': 'virat.kohli', 'name': 'Virat Kohli', 'verified': True, 'category': 'Sports'},
            {'username': 'Cristiano', 'name': 'Cristiano Ronaldo', 'verified': True, 'category': 'Sports'},
            {'username': 'leomessi', 'name': 'Lionel Messi', 'verified': True, 'category': 'Sports'},
            {'username': 'Nike', 'name': 'Nike', 'verified': True, 'category': 'Brand'},
            {'username': 'NASA', 'name': 'NASA', 'verified': True, 'category': 'Organization'},
        ]
    }
    
    platform_suggestions = suggestions.get(platform, [])
    
    # Filter by query if provided
    if query:
        filtered = [
            s for s in platform_suggestions
            if query in s['username'].lower() or query in s['name'].lower() or query in s['category'].lower()
        ]
    else:
        filtered = platform_suggestions
    
    return jsonify({
        'success': True,
        'suggestions': filtered[:10],  # Limit to top 10
        'platform': platform
    })


@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """Generate PDF report for a client"""
    try:
        from report_generator import generate_pdf_report
        
        data = request.get_json()
        client_id = data.get('client_id')
        date_range = data.get('range', '30days')
        
        if not client_id:
            return jsonify({'success': False, 'error': 'Missing client_id'}), 400
        
        # Get client data
        client_data = load_client_data(client_id)
        if not client_data:
            return jsonify({'success': False, 'error': 'Client not found'}), 404
        
        client_name = client_data.get('name', client_id)
        
        # Get analytics data
        df = load_all()
        if not df.empty and 'username' in df.columns:
            platforms = client_data.get('platforms', {})
            usernames = [v for k, v in platforms.items() if v]
            if usernames:
                df = df[df['username'].isin(usernames)]
        
        # Filter by date range
        if date_range != 'all':
            df = filter_data_by_date(df, date_range)
        
        # Compute analytics
        analytics_data = {
            **compute_summary(df),
            'trend': compute_engagement_trend(df),
            'platforms': get_platform_distribution(df),
            'top_posts': get_top_posts(df, 5),
            'hashtags': get_hashtag_stats(df)
        }
        
        # Generate PDF
        reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{client_id}_report_{timestamp}.pdf"
        output_path = os.path.join(reports_dir, filename)
        
        success = generate_pdf_report(client_name, date_range, analytics_data, output_path)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Report generated successfully',
                'filename': filename,
                'download_url': f'/api/reports/download/{filename}'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to generate report'}), 500
            
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reports/download/<filename>', methods=['GET'])
def download_report(filename: str):
    """Download a generated PDF report"""
    try:
        from flask import send_file
        
        reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
        filepath = os.path.join(reports_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'Report not found'}), 404
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        logger.error(f"Error downloading report: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/insights/generate', methods=['POST'])
def generate_ai_insights():
    """Generate AI-powered insights for analytics data"""
    try:
        from ai_insights import generate_quick_insights
        
        data = request.get_json()
        client_id = data.get('client_id')
        date_range = data.get('range', '30days')
        
        # Get analytics data
        df = load_all()
        
        if client_id:
            client_data = load_client_data(client_id)
            if client_data and 'username' in df.columns:
                platforms = client_data.get('platforms', {})
                usernames = [v for k, v in platforms.items() if v]
                if usernames:
                    df = df[df['username'].isin(usernames)]
        
        # Filter by date range
        if date_range != 'all':
            df = filter_data_by_date(df, date_range)
        
        # Prepare analytics data
        analytics_data = {
            **compute_summary(df),
            'trend': compute_engagement_trend(df),
            'platforms': get_platform_distribution(df),
            'top_posts': get_top_posts(df, 10),
            'hashtags': get_hashtag_stats(df)
        }
        
        # Generate insights (uses fallback if OpenAI not available)
        insights = generate_quick_insights(analytics_data, use_fallback=True)
        
        return jsonify(insights)
        
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/insights/content-recommendations', methods=['POST'])
def get_content_recommendations():
    """Get AI content recommendations based on top posts"""
    try:
        from ai_insights import AIInsightsGenerator
        
        data = request.get_json()
        client_id = data.get('client_id')
        
        # Get analytics data
        df = load_all()
        
        if client_id:
            client_data = load_client_data(client_id)
            if client_data and 'username' in df.columns:
                platforms = client_data.get('platforms', {})
                usernames = [v for k, v in platforms.items() if v]
                if usernames:
                    df = df[df['username'].isin(usernames)]
        
        top_posts = get_top_posts(df, 5)
        platforms = get_platform_distribution(df)
        
        # Try AI recommendations
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            try:
                generator = AIInsightsGenerator(api_key)
                result = generator.generate_content_recommendations(top_posts, platforms)
                return jsonify(result)
            except Exception as e:
                logger.warning(f"AI recommendations failed: {e}")
        
        # Fallback recommendations
        return jsonify({
            'success': True,
            'recommendations': """Content Recommendations:

1. **Post Timing**: Schedule posts during peak hours (7-9 AM, 12-1 PM, 7-9 PM)
2. **Visual Content**: Focus on high-quality images and videos - they drive 2-3x more engagement
3. **Hashtag Strategy**: Use 5-10 relevant hashtags per post, mix popular and niche tags
4. **Engagement**: Respond to comments within the first hour to boost visibility
5. **Consistency**: Post 3-5 times per week on each platform for optimal reach

Platform-Specific Tips:
- Instagram: Stories and Reels perform exceptionally well
- YouTube: Thumbnails and titles are critical - invest time in optimization
- Twitter: Short, punchy tweets with images get more retweets
- Facebook: Video content and questions drive higher engagement""",
            'source': 'rule-based'
        })
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ML & ADVANCED ANALYTICS ENDPOINTS
# ============================================================================

class TrainRequest(BaseModel):
    client_id: str

class PredictRequest(BaseModel):
    caption: str
    platform: Literal['instagram','youtube','twitter','facebook'] = 'instagram'
    scheduled_time: Optional[str] = None

    @field_validator('caption')
    def validate_caption(cls, v: str) -> str:
        v = (v or '').strip()
        if len(v) == 0:
            raise ValueError('caption required')
        if len(v) > 5000:
            raise ValueError('caption too long (max 5000)')
        return v

@app.route('/api/ml/test', methods=['GET', 'OPTIONS'])
@ml_log('ml_test')
def test_ml_endpoint():
    """Test endpoint to verify ML routes are loaded"""
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify({'success': True, 'message': 'ML endpoints are working'})


@app.route('/api/ml/train', methods=['POST', 'OPTIONS'])
@ml_log('train_models')
def train_ml_models():
    """Train ML models on historical data"""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        try:
            payload = TrainRequest.model_validate(request.json or {})
        except ValidationError as ve:
            return jsonify({'success': False, 'error': 'validation_error', 'detail': ve.errors()}), 400
        client_id = payload.client_id
        
        if not client_id:
            return jsonify({'success': False, 'error': 'client_id required'}), 400
        
        # Load client's data mapped to configured platform handles
        all_data = load_all()
        client_data = pd.DataFrame()
        registry = load_client_data(client_id)
        if registry and 'username' in all_data:
            platforms = registry.get('platforms', {}) or {}
            usernames = [str(v) for v in platforms.values() if v]
            if usernames:
                tmp = all_data.copy()
                tmp['_norm_user'] = (
                    tmp['username']
                    .astype(str)
                    .str.lower()
                    .str.replace('@', '', regex=False)
                    .str.strip()
                )
                norm_list = [u.lower().lstrip('@').strip() for u in usernames]
                client_data = tmp[tmp['_norm_user'].isin(norm_list)].drop(columns=['_norm_user'])
        if client_data.empty and 'username' in all_data:
            # Fallback to simple equality (legacy behavior)
            client_data = all_data[all_data['username'] == client_id]
        
        if len(client_data) < 30:
            return jsonify({
                'success': False,
                'error': 'Not enough data to train models (minimum 30 posts required)'
            }), 400
        
        # Import ML models
        try:
            from ml_models import train_predictor, train_detector
        except ImportError:
            return jsonify({
                'success': False,
                'error': 'ML models not available. Install scikit-learn: pip install scikit-learn'
            }), 500
        
        # Train predictor & anomaly detector
        predictor_result = train_predictor(client_data)
        detector_result = train_detector(client_data)

        return jsonify({
            'success': True,
            'models': {
                'predictor': predictor_result,
                'anomaly_detector': detector_result
            },
            'message': 'ML models trained successfully'
        })
        
    except Exception as e:
        logger.error(f"Error training models: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ml/predict/engagement', methods=['POST', 'OPTIONS'])
@ml_log('predict_engagement')
def predict_post_engagement():
    """Predict engagement for a new post"""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        try:
            payload = PredictRequest.model_validate(request.json or {})
        except ValidationError as ve:
            return jsonify({'success': False, 'error': 'validation_error', 'detail': ve.errors()}), 400
        
        # Import predictor
        try:
            from ml_models import predict_engagement
        except ImportError:
            return jsonify({
                'success': False,
                'error': 'ML models not available'
            }), 500
        
        # Predict
        prediction = predict_engagement(payload.model_dump())
        
        return jsonify({
            'success': True,
            'prediction': prediction
        })
        
    except Exception as e:
        logger.error(f"Error predicting engagement: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ml/optimal-time', methods=['GET', 'OPTIONS'])
@ml_log('optimal_time')
def get_optimal_posting_time():
    """Get optimal posting time for a platform"""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        client_id = request.args.get('client_id')
        platform = request.args.get('platform', 'instagram')
        
        if not client_id:
            return jsonify({'success': False, 'error': 'client_id required'}), 400
        
        # Load data mapped to configured usernames for client
        all_data = load_all()
        platform_data = pd.DataFrame()
        registry = load_client_data(client_id)
        if registry and 'username' in all_data and 'platform' in all_data:
            platforms = registry.get('platforms', {}) or {}
            wanted_handle = platforms.get(platform)
            if wanted_handle:
                tmp = all_data.copy()
                tmp['_norm_user'] = (
                    tmp['username']
                    .astype(str)
                    .str.lower()
                    .str.replace('@', '', regex=False)
                    .str.strip()
                )
                norm = wanted_handle.lower().lstrip('@').strip()
                platform_data = tmp[(tmp['_norm_user'] == norm) & (tmp['platform'] == platform)].drop(columns=['_norm_user'])
        if platform_data.empty and 'username' in all_data and 'platform' in all_data:
            # Fallback
            platform_data = all_data[all_data['platform'] == platform]
        
        # Import predictor
        try:
            from ml_models import get_optimal_time
        except ImportError:
            return jsonify({
                'success': False,
                'error': 'ML models not available'
            }), 500
        
        # Get optimal time
        optimal_time = get_optimal_time(platform, platform_data)
        
        return jsonify({
            'success': True,
            'platform': platform,
            'optimal_time': optimal_time
        })
        
    except Exception as e:
        logger.error(f"Error getting optimal time: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ml/detect/anomalies', methods=['GET', 'OPTIONS'])
@ml_log('detect_anomalies')
def detect_anomalies_endpoint():
    """Detect anomalies in client data"""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        client_id = request.args.get('client_id')
        
        if not client_id:
            return jsonify({'success': False, 'error': 'client_id required'}), 400
        
        # Load data with normalized mapping against client registry (consistent with training)
        all_data = load_all()
        client_data = pd.DataFrame()
        if 'username' in all_data:
            registry = load_client_data(client_id)
            if registry:
                platforms = registry.get('platforms', {}) or {}
                usernames = [str(v) for v in platforms.values() if v]
                if usernames:
                    tmp = all_data.copy()
                    tmp['_norm_user'] = (
                        tmp['username']
                        .astype(str)
                        .str.lower()
                        .str.replace('@', '', regex=False)
                        .str.strip()
                    )
                    norm_list = [u.lower().lstrip('@').strip() for u in usernames]
                    client_data = tmp[tmp['_norm_user'].isin(norm_list)].drop(columns=['_norm_user'])
        if client_data.empty and 'username' in all_data:
            client_data = all_data[all_data['username'] == client_id]

        if client_data.empty or len(client_data) < 10:
            # Return graceful empty payload instead of an error so frontend can show a friendly message
            return jsonify({
                'success': True,
                'anomalies': [],
                'trend_analysis': None,
                'engagement_drop': None,
                'total_anomalies_found': 0,
                'message': 'Insufficient data for anomaly detection (need >=10 posts)'
            })
        
        # Import detector
        try:
            from ml_models import find_anomalies, analyze_trends, check_engagement_drop
        except ImportError:
            return jsonify({
                'success': False,
                'error': 'ML models not available'
            }), 500
        
        # Compute results with safety nets to avoid 500s in prototype
        try:
            anomalies = find_anomalies(client_data)
        except Exception as e:
            logger.warning(f"find_anomalies failed: {e}")
            anomalies = []
        try:
            trends = analyze_trends(client_data)
        except Exception as e:
            logger.warning(f"analyze_trends failed: {e}")
            trends = {"overall_trend": "stable", "alert": "✅ Engagement is stable", "recommendation": "Monitor metrics closely"}
        try:
            drop_check = check_engagement_drop(client_data)
        except Exception as e:
            logger.warning(f"check_engagement_drop failed: {e}")
            drop_check = {"status": "unknown"}
        
        return jsonify({
            'success': True,
            'anomalies': anomalies[:10],  # Top 10 anomalies
            'trend_analysis': trends,
            'engagement_drop': drop_check,
            'total_anomalies_found': len(anomalies)
        })
        
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ml/forecast', methods=['GET', 'OPTIONS'])
@ml_log('forecast_trends')
def forecast_engagement():
    """Forecast engagement trends"""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        days = int(request.args.get('days', 7))
        
        # Import predictor
        try:
            from ml_models import forecast_trends
        except ImportError:
            return jsonify({
                'success': False,
                'error': 'ML models not available'
            }), 500
        
        # Forecast
        forecast = forecast_trends(days)
        
        return jsonify({
            'success': True,
            'forecast': forecast,
            'days_ahead': days
        })
        
    except Exception as e:
        logger.error(f"Error forecasting: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ---------------------------------------------------------------------------
# MODEL STATUS & DIAGNOSTICS
# ---------------------------------------------------------------------------
@app.route('/api/ml/models/status', methods=['GET'])
def ml_models_status():
    """Return current persisted model metadata and load status."""
    reg = load_registry()
    predictor_meta = reg.get('predictor_likes') or reg.get('predictor_scaler') or {}
    anomaly_meta = reg.get('anomaly_model') or {}
    return jsonify({
        'success': True,
        'predictor': {
            'loaded': getattr(_predictor_inst, 'is_trained', False),
            'version': predictor_meta.get('version'),
            'trained_on': predictor_meta.get('trained_on'),
            'samples_trained': predictor_meta.get('samples_trained'),
            'features_used': predictor_meta.get('features_used')
        },
        'anomaly_detector': {
            'loaded': getattr(_detector_inst, 'is_trained', False),
            'version': anomaly_meta.get('version'),
            'trained_on': anomaly_meta.get('trained_on'),
            'samples_trained': anomaly_meta.get('samples_trained')
        }
    })

@app.route('/ml/models/status', methods=['GET'])
def ml_models_status_alias():
    """Alias route without /api prefix to support proxy configurations."""
    return ml_models_status()


@app.route('/api/ml/diagnostics', methods=['GET'])
def ml_diagnostics():
    """Lightweight diagnostics for debugging ML stack locally."""
    reg = load_registry()
    issues = []
    if getattr(_predictor_inst, 'is_trained', False) and not reg.get('predictor_likes'):
        issues.append('predictor trained but registry missing predictor_likes entry')
    if getattr(_detector_inst, 'is_trained', False) and not reg.get('anomaly_model'):
        issues.append('anomaly detector loaded but registry missing anomaly_model entry')
    return jsonify({
        'success': True,
        'predictor_loaded': getattr(_predictor_inst, 'is_trained', False),
        'anomaly_loaded': getattr(_detector_inst, 'is_trained', False),
        'registry_keys': list(reg.keys()),
        'issues': issues
    })

@app.route('/ml/diagnostics', methods=['GET'])
def ml_diagnostics_alias():
    """Alias route without /api prefix to support proxy configurations."""
    return ml_diagnostics()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    # Force single-process mode to avoid Windows watchdog/reloader oddities while debugging 404s
    debug = False
    
    logger.info(f"Starting Pulselytics API Server")
    logger.info(f"Scraper Mode: {get_scraper_mode()}")
    logger.info(f"Data Directory: {DATA_DIR}")
    logger.info(f"Client Data Directory: {CLIENT_DATA_DIR}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
