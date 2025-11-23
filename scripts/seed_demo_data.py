"""
Seed small, clearly-labeled demo rows for clients/platforms that lack data.
This is safe for demos and keeps the dashboard populated when APIs or scrapers are unavailable.

Usage (Windows PowerShell):
  # Optional: run inside venv
  # .\\venv\\Scripts\\Activate.ps1
  python seed_demo_data.py --clients all --platforms instagram facebook twitter --per-client 2

It will only add rows for (client, platform, username) combinations that have zero rows currently.
"""
import argparse
import json
import os
from datetime import datetime, timedelta, timezone
import random
from typing import Dict, List

import pandas as pd

from common import DATA_DIR, save_csv

BACKEND_DATA = os.path.join(os.path.dirname(__file__), 'backend', 'data')

CSV_FILES = {
    'instagram': 'instagram_data.csv',
    'facebook': 'facebook_data.csv',
    'twitter': 'twitter_data.csv',
}

MEDIA_PLACEHOLDER = 'https://via.placeholder.com/800'


def list_clients() -> List[Dict]:
    clients = []
    if not os.path.isdir(BACKEND_DATA):
        return clients
    for name in os.listdir(BACKEND_DATA):
        if not name.endswith('.json'):
            continue
        cid = name[:-5]
        try:
            with open(os.path.join(BACKEND_DATA, name), 'r', encoding='utf-8') as f:
                data = json.load(f)
            clients.append({'id': cid, **data})
        except Exception:
            continue
    return clients


def load_csv(filename: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except Exception:
            pass
    return pd.DataFrame(columns=[
        'platform','username','post_url','caption','media_url','likes','comments','views','upload_date'
    ])


def clean_placeholders(platforms: List[str]) -> int:
    """Remove generic placeholder rows to make the demo look professional."""
    removed = 0
    for plat in platforms:
        csv_name = CSV_FILES.get(plat)
        if not csv_name:
            continue
        path = os.path.join(DATA_DIR, csv_name)
        if not os.path.exists(path):
            continue
        try:
            df = pd.read_csv(path)
        except Exception:
            continue
        if df.empty:
            continue
        mask_remove = (
            df['username'].astype(str).str.lower().eq('your_account') |
            df['caption'].astype(str).str.contains('No data - check access token', case=False, na=False) |
            df['caption'].astype(str).str.contains('Sample tweet placeholder', case=False, na=False)
        )
        before = len(df)
        df = df[~mask_remove]
        after = len(df)
        if after < before:
            removed += (before - after)
            df.to_csv(path, index=False, encoding='utf-8')
    return removed


def fix_missing_dates(platforms: List[str], days_window: int = 5) -> int:
    """Fill missing upload_date for demo rows (example.com URLs) so date filters work.
    Returns number of rows updated across all specified platform CSVs.
    """
    updated = 0
    now = datetime.now(timezone.utc)
    for plat in platforms:
        csv_name = CSV_FILES.get(plat)
        if not csv_name:
            continue
        path = os.path.join(DATA_DIR, csv_name)
        if not os.path.exists(path):
            continue
        try:
            df = pd.read_csv(path)
        except Exception:
            continue
        if df.empty or 'post_url' not in df.columns:
            continue
        # Identify demo rows with missing upload_date
        demo_mask = df['post_url'].astype(str).str.contains(f'https://example.com/{plat}/', na=False)
        date_missing = df['upload_date'].isna() | (df['upload_date'].astype(str).str.strip() == '')
        mask = demo_mask & date_missing
        if not mask.any():
            continue
        # Assign recent dates distributed over last `days_window` days
        idxs = df.index[mask].tolist()
        for i, idx in enumerate(idxs):
            dt = (now - timedelta(days=(i % days_window) + 1)).isoformat()
            df.at[idx, 'upload_date'] = dt
        try:
            df.to_csv(path, index=False, encoding='utf-8')
            updated += len(idxs)
        except Exception:
            # best-effort
            pass
    return updated


def ensure_demo_rows(client_id: str, platforms: Dict[str, str], per_client: int = 2, with_engagement: bool = False, refresh_dates: bool = False) -> int:
    added = 0
    now = datetime.now(timezone.utc)

    for plat, handle in platforms.items():
        if plat not in CSV_FILES or not handle:
            continue
        csv_name = CSV_FILES[plat]
        df = load_csv(csv_name)
        # Count existing rows for this handle+platform
        existing = 0
        if not df.empty:
            mask = (df['platform'].astype(str).str.lower() == plat) & (
                df['username'].astype(str).str.lower() == handle.lower()
            )
            existing = int(mask.sum())
        # Create only as many rows as needed to reach per_client
        to_add = max(0, per_client - existing)

        # Optionally refresh dates for existing demo rows so recent filters show data
        # We'll (re)write up to `per_client` demo rows with current dates. Dedup keeps last.
        if refresh_dates:
            refresh_rows = []
            for i in range(per_client):
                dt = (now - timedelta(days=i+1)).isoformat()
                if with_engagement:
                    likes = random.randint(25, 500)
                    comments = random.randint(0, 50)
                    views = random.randint(200, 5000)
                else:
                    likes = 0
                    comments = 0
                    views = 0
                # Use stable demo URLs 1..per_client so we overwrite prior placeholders
                refresh_rows.append({
                    'platform': plat,
                    'username': handle,
                    'post_url': f'https://example.com/{plat}/{handle}/demo-{i + 1}',
                    'caption': f'Highlights for {handle} on {plat} — demo post {i + 1}',
                    'media_url': MEDIA_PLACEHOLDER,
                    'likes': likes,
                    'comments': comments,
                    'views': views,
                    'upload_date': dt,
                })
            save_csv(pd.DataFrame(refresh_rows), csv_name)
            added += len(refresh_rows)

        if to_add > 0:
            rows = []
            # Start numbering after existing to avoid clashes for brand-new handles
            for i in range(to_add):
                dt = (now - timedelta(days=i+1)).isoformat()
                if with_engagement:
                    likes = random.randint(25, 500)
                    comments = random.randint(0, 50)
                    views = random.randint(200, 5000)
                else:
                    likes = 0
                    comments = 0
                    views = 0
                rows.append({
                    'platform': plat,
                    'username': handle,
                    'post_url': f'https://example.com/{plat}/{handle}/demo-{existing + i + 1}',
                    'caption': f'Highlights for {handle} on {plat} — demo post {existing + i + 1}',
                    'media_url': MEDIA_PLACEHOLDER,
                    'likes': likes,
                    'comments': comments,
                    'views': views,
                    'upload_date': dt,
                })
            save_csv(pd.DataFrame(rows), csv_name)
            added += len(rows)
    return added


def main():
    ap = argparse.ArgumentParser(description='Seed demo rows for missing client/platform data')
    ap.add_argument('--clients', default='all', help='Comma-separated client ids or "all"')
    ap.add_argument('--platforms', nargs='*', default=['instagram','facebook','twitter'])
    ap.add_argument('--per-client', type=int, default=2)
    ap.add_argument('--clean-placeholders', action='store_true', help='Remove generic placeholder rows')
    ap.add_argument('--with-engagement', action='store_true', help='Add small engagement numbers to demo rows')
    ap.add_argument('--refresh-dates', action='store_true', help='Refresh upload_date for existing demo rows so date filters show data')
    ap.add_argument('--fix-missing-dates', action='store_true', help='Fill missing upload_date for demo rows already in CSVs')
    args = ap.parse_args()

    platforms_filter = set([p.lower() for p in args.platforms])

    all_clients = list_clients()
    if args.clients != 'all':
        want = set([c.strip() for c in args.clients.split(',') if c.strip()])
        all_clients = [c for c in all_clients if c.get('id') in want]

    # Optional cleanup pass
    if args.clean_placeholders:
        removed = clean_placeholders(list(platforms_filter))
        print(f"Removed placeholder rows: {removed}")

    total_added = 0
    for c in all_clients:
        plats = c.get('platforms', {}) or {}
        filt_plats = {k: v for k, v in plats.items() if k.lower() in platforms_filter and v}
        total_added += ensure_demo_rows(
            c['id'],
            filt_plats,
            args.per_client,
            args.with_engagement,
            args.refresh_dates,
        )

    print(f"Demo rows added: {total_added}")

    if args.fix_missing_dates:
        fixed = fix_missing_dates(list(platforms_filter))
        print(f"Missing dates fixed: {fixed}")


if __name__ == '__main__':
    main()
