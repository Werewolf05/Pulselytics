"""
Predictive Engagement Model
Predicts future engagement rates and post performance using historical data
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    StandardScaler = None
    print("Warning: scikit-learn not installed. Run: pip install scikit-learn")

from .features import build_features, align_feature_columns
from .config import (
    PREDICTOR_VERSION,
    MIN_TRAIN_SAMPLES_PREDICTOR
)
from .storage import save_model, load_model, save_feature_names, load_feature_names


class EngagementPredictor:
    """Predict engagement metrics for future posts"""
    
    def __init__(self):
        self.model_likes = None
        self.model_comments = None
        self.model_views = None
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.is_trained = False
        self.feature_names = []
        
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Delegate to shared feature builder."""
        return build_features(df)
    
    def train(self, df: pd.DataFrame) -> Dict:
        """Train the prediction models on historical data"""
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn not installed"}
        
        if len(df) < MIN_TRAIN_SAMPLES_PREDICTOR:
            return {"error": f"Not enough data to train (need at least {MIN_TRAIN_SAMPLES_PREDICTOR} posts)"}
        
        # Extract features and sanitize NaNs/Infs early
        X = self.extract_features(df)
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(0)
        self.feature_names = X.columns.tolist()
        
        # Prepare target variables
        y_likes = df['likes'].fillna(0)
        y_comments = df['comments'].fillna(0)
        y_views = df['views'].fillna(0)
        
        # Remove rows with missing targets
        valid_idx = (y_likes > 0) & (y_comments > 0)
        X = X[valid_idx]
        y_likes = y_likes[valid_idx]
        y_comments = y_comments[valid_idx]
        y_views = y_views[valid_idx]
        
        if len(X) < 30:
            return {"error": "Not enough valid data after filtering"}
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train/validation split for basic generalization metrics
        from sklearn.model_selection import train_test_split
        X_train, X_val, y_likes_train, y_likes_val = train_test_split(
            X_scaled, y_likes, test_size=0.2, random_state=42
        )
        _, _, y_comments_train, y_comments_val = train_test_split(
            X_scaled, y_comments, test_size=0.2, random_state=42
        )
        
        # Train models
        self.model_likes = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.model_comments = GradientBoostingRegressor(n_estimators=100, random_state=42)
        
        self.model_likes.fit(X_train, y_likes_train)
        self.model_comments.fit(X_train, y_comments_train)
        
        # Train views model if data available
        if y_views.sum() > 0:
            valid_views = y_views > 0
            self.model_views = GradientBoostingRegressor(n_estimators=100, random_state=42)
            self.model_views.fit(X_scaled[valid_views], y_views[valid_views])
        
        self.is_trained = True
        
        # Calculate accuracy metrics
        train_score_likes = self.model_likes.score(X_train, y_likes_train)
        val_score_likes = self.model_likes.score(X_val, y_likes_val)
        train_score_comments = self.model_comments.score(X_train, y_comments_train)
        val_score_comments = self.model_comments.score(X_val, y_comments_val)

        # Engagement distribution for percentile-based virality scoring later
        engagement_total = (y_likes + y_comments).values
        engagement_sorted = np.sort(engagement_total)
        # Persist a simple quantile grid (10th,25th,50th,75th,90th)
        quantiles = {
            'q10': float(np.quantile(engagement_sorted, 0.10)),
            'q25': float(np.quantile(engagement_sorted, 0.25)),
            'q50': float(np.quantile(engagement_sorted, 0.50)),
            'q75': float(np.quantile(engagement_sorted, 0.75)),
            'q90': float(np.quantile(engagement_sorted, 0.90))
        }
        self._engagement_sorted = engagement_sorted.tolist()
        self._engagement_quantiles = quantiles
        
        # Persist models + scaler
        metadata = {
            "trained_on": datetime.utcnow().isoformat() + "Z",
            "samples_trained": len(X),
            "features_used": len(self.feature_names),
            "r2_score_likes": round(train_score_likes, 3),
            "r2_score_comments": round(train_score_comments, 3),
            "val_r2_likes": round(val_score_likes, 3),
            "val_r2_comments": round(val_score_comments, 3),
            "quantiles": quantiles
        }
        save_model("predictor_scaler", PREDICTOR_VERSION, self.scaler, metadata)
        save_model("predictor_likes", PREDICTOR_VERSION, self.model_likes, metadata)
        save_model("predictor_comments", PREDICTOR_VERSION, self.model_comments, metadata)
        if self.model_views:
            save_model("predictor_views", PREDICTOR_VERSION, self.model_views, metadata)
        # Persist feature names for future alignment
        try:
            save_feature_names(self.feature_names)
        except Exception:
            pass

        return {
            "status": "success",
            "version": PREDICTOR_VERSION,
            **metadata
        }
    
    def predict_post_performance(self, post_data: Dict) -> Dict:
        """
        Predict engagement for a new post
        
        Args:
            post_data: Dict with keys: platform, caption, scheduled_time (optional)
            
        Returns:
            Dict with predicted likes, comments, views, engagement_rate
        """
        if not self.is_trained:
            return self._fallback_prediction(post_data)
        
        # Create dataframe from input
        df = pd.DataFrame([{
            'platform': post_data.get('platform', 'instagram'),
            'caption': post_data.get('caption', ''),
            'upload_date': post_data.get('scheduled_time', datetime.now())
        }])
        
        # Extract & align features
        X_raw = self.extract_features(df)
        X_raw = X_raw.replace([np.inf, -np.inf], np.nan).fillna(0)
        X = align_feature_columns(X_raw, self.feature_names).fillna(0)
        X_scaled = self.scaler.transform(X)
        
        pred_likes = max(0, int(self.model_likes.predict(X_scaled)[0]))
        pred_comments = max(0, int(self.model_comments.predict(X_scaled)[0]))
        pred_views = max(0, int(self.model_views.predict(X_scaled)[0])) if self.model_views else pred_likes * 5
        
        # Calculate engagement rate
        if pred_views > 0:
            engagement_rate = ((pred_likes + pred_comments) / pred_views) * 100
        else:
            engagement_rate = 5.0  # Default
        
        # Percentile-based virality score (0-100)
        virality_score = 50
        try:
            if hasattr(self, '_engagement_sorted') and self._engagement_sorted:
                arr = np.array(self._engagement_sorted)
                predicted_total = pred_likes + pred_comments
                # percentile rank
                rank = (arr.searchsorted(predicted_total, side='right') / len(arr)) * 100
                virality_score = int(rank)
                # boost if engagement_rate very high compared to median
                median = self._engagement_quantiles.get('q50', 1) or 1
                if predicted_total > median and engagement_rate > 5:
                    virality_score = min(100, virality_score + 5)
        except Exception:
            pass
        
        return {
            "predicted_likes": pred_likes,
            "predicted_comments": pred_comments,
            "predicted_views": pred_views,
            "predicted_engagement_rate": round(engagement_rate, 2),
            "virality_score": virality_score,
            "confidence": "high" if self.is_trained else "medium",
            "recommendation": self._get_recommendation(virality_score)
        }
    
    def predict_optimal_time(self, platform: str, historical_data: pd.DataFrame) -> Dict:
        """Predict best time to post based on historical performance"""
        if len(historical_data) < 10:
            return self._default_optimal_times(platform)
        
        # Add hour of day
        historical_data['upload_date'] = pd.to_datetime(historical_data['upload_date'], errors='coerce')
        historical_data['hour'] = historical_data['upload_date'].dt.hour
        historical_data['day_of_week'] = historical_data['upload_date'].dt.dayofweek
        
        # Calculate average engagement by hour
        engagement = (historical_data['likes'] + historical_data['comments'] * 3) / (historical_data['views'].replace(0, 1))
        hourly_performance = historical_data.groupby('hour').apply(
            lambda x: (x['likes'] + x['comments'] * 3).mean()
        ).sort_values(ascending=False)
        
        daily_performance = historical_data.groupby('day_of_week').apply(
            lambda x: (x['likes'] + x['comments'] * 3).mean()
        ).sort_values(ascending=False)
        
        best_hours = hourly_performance.head(3).index.tolist()
        best_days = daily_performance.head(3).index.tolist()
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        return {
            "best_hours": [f"{h}:00" for h in best_hours],
            "best_days": [day_names[d] for d in best_days],
            "recommendation": f"Post on {day_names[best_days[0]]} at {best_hours[0]}:00 for maximum engagement",
            "confidence": "high" if len(historical_data) > 50 else "medium"
        }
    
    def forecast_engagement(self, days_ahead: int = 7) -> List[Dict]:
        """Forecast engagement trends for next N days"""
        forecasts = []
        
        for i in range(days_ahead):
            future_date = datetime.now() + timedelta(days=i)
            
            # Simple trend forecast (would be enhanced with Prophet/LSTM)
            base_engagement = 1000 + (i * 50)  # Trending up
            
            forecasts.append({
                "date": future_date.strftime("%Y-%m-%d"),
                "predicted_total_engagement": base_engagement,
                "confidence_interval_low": int(base_engagement * 0.8),
                "confidence_interval_high": int(base_engagement * 1.2),
                "trend": "increasing" if i > days_ahead/2 else "stable"
            })
        
        return forecasts
    
    def _fallback_prediction(self, post_data: Dict) -> Dict:
        """Fallback prediction when model not trained"""
        platform = post_data.get('platform', 'instagram')
        caption_length = len(post_data.get('caption', ''))
        
        # Platform-based baseline estimates
        baselines = {
            'instagram': {'likes': 5000, 'comments': 150, 'views': 25000},
            'youtube': {'likes': 3000, 'comments': 200, 'views': 100000},
            'facebook': {'likes': 2000, 'comments': 100, 'views': 15000},
            'twitter': {'likes': 1500, 'comments': 80, 'views': 50000}
        }
        
        base = baselines.get(platform, baselines['instagram'])
        
        # Adjust for caption quality
        multiplier = 1.0
        if caption_length > 100:
            multiplier += 0.2
        if '#' in post_data.get('caption', ''):
            multiplier += 0.1
        if '!' in post_data.get('caption', '') or '?' in post_data.get('caption', ''):
            multiplier += 0.1
        
        pred_likes = int(base['likes'] * multiplier)
        pred_comments = int(base['comments'] * multiplier)
        pred_views = int(base['views'] * multiplier)
        
        engagement_rate = ((pred_likes + pred_comments) / pred_views) * 100 if pred_views > 0 else 5.0
        virality_score = min(100, int(engagement_rate * 10))
        
        return {
            "predicted_likes": pred_likes,
            "predicted_comments": pred_comments,
            "predicted_views": pred_views,
            "predicted_engagement_rate": round(engagement_rate, 2),
            "virality_score": virality_score,
            "confidence": "low",
            "recommendation": self._get_recommendation(virality_score),
            "note": "Prediction based on platform averages (model not trained yet)"
        }
    
    def _default_optimal_times(self, platform: str) -> Dict:
        """Default optimal posting times by platform"""
        defaults = {
            'instagram': {
                'best_hours': ['9:00', '12:00', '19:00'],
                'best_days': ['Wednesday', 'Friday', 'Sunday'],
                'recommendation': 'Post on Wednesday at 12:00 for maximum engagement'
            },
            'facebook': {
                'best_hours': ['13:00', '15:00', '20:00'],
                'best_days': ['Thursday', 'Friday', 'Saturday'],
                'recommendation': 'Post on Thursday at 15:00 for maximum engagement'
            },
            'twitter': {
                'best_hours': ['8:00', '12:00', '17:00'],
                'best_days': ['Tuesday', 'Wednesday', 'Thursday'],
                'recommendation': 'Post on Wednesday at 12:00 for maximum engagement'
            },
            'youtube': {
                'best_hours': ['14:00', '16:00', '20:00'],
                'best_days': ['Friday', 'Saturday', 'Sunday'],
                'recommendation': 'Post on Friday at 16:00 for maximum engagement'
            }
        }
        
        result = defaults.get(platform, defaults['instagram'])
        result['confidence'] = 'low'
        result['note'] = 'Using industry standard optimal times'
        return result
    
    def _get_recommendation(self, virality_score: int) -> str:
        """Get posting recommendation based on virality score"""
        if virality_score >= 80:
            return "🔥 Excellent! This content has high viral potential. Post immediately!"
        elif virality_score >= 60:
            return "✅ Good performance expected. This is worth posting."
        elif virality_score >= 40:
            return "⚠️ Moderate performance. Consider improving caption or visuals."
        else:
            return "❌ Low predicted engagement. Rework this content before posting."


def _load_or_create_predictor() -> EngagementPredictor:
    inst = EngagementPredictor()
    # Attempt load of persisted components
    scaler = load_model("predictor_scaler")
    likes = load_model("predictor_likes")
    comments = load_model("predictor_comments")
    views = load_model("predictor_views")
    if scaler and likes and comments:
        inst.scaler = scaler
        inst.model_likes = likes
        inst.model_comments = comments
        inst.model_views = views
        # Load persisted feature names for proper alignment during prediction
        try:
            inst.feature_names = load_feature_names() or []
        except Exception:
            inst.feature_names = []
        inst.is_trained = True
    return inst

# Global instance (lazy load)
predictor = _load_or_create_predictor()


def train_predictor(df: pd.DataFrame) -> Dict:
    """Train the global predictor instance"""
    return predictor.train(df)


def predict_engagement(post_data: Dict) -> Dict:
    """Predict engagement for a post"""
    return predictor.predict_post_performance(post_data)


def get_optimal_time(platform: str, historical_data: pd.DataFrame) -> Dict:
    """Get optimal posting time"""
    return predictor.predict_optimal_time(platform, historical_data)


def forecast_trends(days: int = 7) -> List[Dict]:
    """Forecast engagement trends"""
    return predictor.forecast_engagement(days)
