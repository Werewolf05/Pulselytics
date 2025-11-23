"""
Anomaly Detection System
------------------------

Purpose
    Detect unusual patterns, spikes, and drops in social media engagement metrics
    (likes, comments, views) so analysts can react quickly.

Why this model?
    We use Isolation Forest (unsupervised) because:
    - No labels required: Historical data rarely comes with ground-truth anomaly tags.
    - Robust to multi-dimensional data: It considers likes, comments, views, and their
        derived engagement rate together, catching combinations that simple z-scores miss.
    - Scales reasonably and is stable with sensible defaults (n_estimators, contamination).
    - Well-supported in scikit-learn and easy to persist and reload.

Fallback behavior
    When insufficient data or the model is not trained, we use a rule-based detector
    (3-sigma thresholds) to provide a safe, interpretable fallback.

Preprocessing
    We standardize features using StandardScaler to give each metric comparable influence
    and to avoid one large-scale metric (e.g., views) dominating the detector.

Outputs
    - Anomaly list with type, severity, metric values, deviations vs baseline, and a
        human-readable alert message.
    - Trend and engagement drop analyses for contextual signals beyond point anomalies.

Notes
    - Baseline statistics are cached to drive classification, severity, and messaging.
    - All numeric conversions are NaN/None safe to avoid runtime failures from messy data.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')
import math

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    StandardScaler = None
    IsolationForest = None
    print("Warning: scikit-learn not installed. Run: pip install scikit-learn")

from .config import (
    ANOMALY_VERSION,
    MIN_TRAIN_SAMPLES_DETECTOR,
    ANOMALY_CONTAMINATION,
    ANOMALY_ESTIMATORS,
)
from .storage import save_model, load_model


class AnomalyDetector:
    """Detect anomalies in social media engagement metrics.

        The detector supports two modes:
        - ML-based (IsolationForest): preferred when enough data exists and a model has been
            trained and persisted.
        - Rule-based (3-sigma thresholds): fallback when there is not enough data for ML or
            on first run prior to training.

        Feature set used for detection:
            likes, comments, views, engagement_rate ((likes + comments) / max(views, 1)).
    """

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.is_trained = False
        self.baseline_metrics = {}
    
    @staticmethod
    def _safe_int_value(val: float) -> int:
        """Convert to int safely, returning 0 for None/NaN/invalid.

        This method ensures downstream reporting is robust to missing or non-numeric
        values encountered in raw data.
        """
        try:
            if val is None:
                return 0
            if isinstance(val, float) and (math.isnan(val) or np.isnan(val)):
                return 0
            return int(val)
        except Exception:
            return 0
        
    def calculate_baseline(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate baseline metrics used by anomaly detection and messaging.

        Baseline metrics (means and stds) are used to:
        - Provide human-readable deviations (e.g., +120% likes vs baseline)
        - Classify anomaly types (viral spike, low performance, controversial)
        - Support rule-based fallback thresholds

        Returns
        -------
        Dict[str, float]
            Dictionary with avg/std metrics and average engagement rate.
        """
        metrics = {
            'avg_likes': df['likes'].mean(),
            'std_likes': df['likes'].std(),
            'avg_comments': df['comments'].mean(),
            'std_comments': df['comments'].std(),
            'avg_views': df['views'].mean() if 'views' in df else 0,
            'std_views': df['views'].std() if 'views' in df else 0,
            'avg_engagement_rate': ((df['likes'] + df['comments']) / df['views'].replace(0, 1)).mean() if 'views' in df else 0
        }
        # Replace NaNs with zeros for stability
        for k, v in metrics.items():
            try:
                if v is None or (isinstance(v, float) and math.isnan(v)):
                    metrics[k] = 0.0
                else:
                    metrics[k] = float(v)
            except Exception:
                metrics[k] = 0.0
        
        self.baseline_metrics = metrics
        return metrics
    
    def train(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train the IsolationForest anomaly detection model on historical data.

        Requirements
        -----------
        - scikit-learn must be available
        - At least MIN_TRAIN_SAMPLES_DETECTOR rows are required to avoid overfitting

        Modeling rationale
        ------------------
        - Features are standardized so each contributes comparably.
        - `contamination` controls the expected proportion of anomalies (domain-tunable).
        - `n_estimators` balances accuracy and speed; defaults are adequate for typical
          social datasets and can be tuned later.

        Returns
        -------
        Dict[str, Any]
            Training metadata including timestamp, sample count, and baselines.
        """
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn not installed"}
        
        if len(df) < MIN_TRAIN_SAMPLES_DETECTOR:
            return {"error": f"Not enough data to train (need at least {MIN_TRAIN_SAMPLES_DETECTOR} posts)"}
        
        # Calculate baseline
        self.calculate_baseline(df)
        
        # Prepare features for anomaly detection
        features = pd.DataFrame({
            'likes': df['likes'].fillna(0),
            'comments': df['comments'].fillna(0),
            'views': df['views'].fillna(0),
            'engagement_rate': (df['likes'] + df['comments']) / df['views'].replace(0, 1)
        })
        
        # Scale features
        X_scaled = self.scaler.fit_transform(features)
        
        # Train Isolation Forest
        self.model = IsolationForest(
            contamination=ANOMALY_CONTAMINATION,
            random_state=42,
            n_estimators=ANOMALY_ESTIMATORS
        )
        self.model.fit(X_scaled)
        self.is_trained = True
        
        meta = {
            "trained_on": datetime.utcnow().isoformat() + "Z",
            "samples_trained": len(df),
            "baseline_avg_likes": int(self.baseline_metrics['avg_likes']),
            "baseline_avg_comments": int(self.baseline_metrics['avg_comments'])
        }
        save_model("anomaly_scaler", ANOMALY_VERSION, self.scaler, meta)
        save_model("anomaly_model", ANOMALY_VERSION, self.model, meta)
        
        return {
            "status": "success",
            "version": ANOMALY_VERSION,
            **meta
        }
    
    def detect_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies in the dataset.

        Behavior
        --------
        - If an ML model is trained and loaded, use IsolationForest.
        - Otherwise, use rule-based detection derived from baseline statistics.

        Returns
        -------
        List[Dict[str, Any]]
            A list of anomalies including:
              post_url, platform, date, type, severity, metric_values, deviation,
              alert_message.
        """
        if not self.is_trained and not self.baseline_metrics:
            # Use rule-based detection
            return self._rule_based_detection(df)
        
        anomalies = []
        
        # Calculate derived parameters
        # Audience Responsiveness Index: measures how actively audience engages (normalized by followers)
        # Higher values = more engaged/loyal audience
        followers = df['followers'].fillna(1000) if 'followers' in df.columns else pd.Series([1000] * len(df))
        df['responsiveness_index'] = ((df['comments'] + df.get('shares', 0)) / followers) * 10000
        
        # Peak Performance Indicator: compares each post to best-ever performance
        # Shows what % of your peak this post achieved (0-100+)
        max_engagement = (df['likes'] + df['comments']).max()
        df['peak_performance'] = ((df['likes'] + df['comments']) / max_engagement * 100) if max_engagement > 0 else 0
        
        # Prepare features
        features = pd.DataFrame({
            'likes': df['likes'].fillna(0),
            'comments': df['comments'].fillna(0),
            'views': df['views'].fillna(0),
            'engagement_rate': (df['likes'] + df['comments']) / df['views'].replace(0, 1),
            'responsiveness_index': df['responsiveness_index'].fillna(0),
            'peak_performance': df['peak_performance'].fillna(0)
        })
        
        if self.is_trained:
            # ML-based detection
            X_scaled = self.scaler.transform(features)
            predictions = self.model.predict(X_scaled)
            anomaly_scores = self.model.score_samples(X_scaled)
            
            # Find anomalies (prediction == -1)
            anomaly_indices = np.where(predictions == -1)[0]
            
            def _safe_int(val):
                try:
                    if val is None:
                        return 0
                    if isinstance(val, float) and math.isnan(val):
                        return 0
                    return int(val)
                except Exception:
                    return 0

            for idx in anomaly_indices:
                row = df.iloc[idx]
                anomalies.append({
                    'post_url': row.get('post_url', 'N/A'),
                    'platform': row.get('platform', 'N/A'),
                    'date': row.get('upload_date', 'N/A'),
                    'type': self._classify_anomaly_type(row, features.iloc[idx]),
                    'severity': self._calculate_severity(anomaly_scores[idx]),
                    'metric_values': {
                        'likes': _safe_int(row.get('likes', 0)),
                        'comments': _safe_int(row.get('comments', 0)),
                        'views': _safe_int(row.get('views', 0)),
                        'responsiveness_index': round(row.get('responsiveness_index', 0), 2),
                        'peak_performance': round(row.get('peak_performance', 0), 1)
                    },
                    'deviation': {
                        'likes': f"{self._calc_deviation(row.get('likes', 0), self.baseline_metrics['avg_likes'])}%",
                        'comments': f"{self._calc_deviation(row.get('comments', 0), self.baseline_metrics['avg_comments'])}%"
                    },
                    'alert_message': self._generate_alert_message(row, features.iloc[idx])
                })
        else:
            # Rule-based detection
            anomalies = self._rule_based_detection(df)
        
        return anomalies
    
    def detect_trends(self, df: pd.DataFrame, window_days: int = 7) -> Dict[str, Any]:
        """Detect short-term engagement trends using rolling averages.

        Parameters
        ----------
        window_days : int
            Size of the rolling window (in posts or days depending on sampling) used to
            compute moving averages. Defaults to 7.

        Returns
        -------
        Dict[str, Any]
            Trend labels, percentage changes, recent averages, and recommendations.
        """
        df['upload_date'] = pd.to_datetime(df['upload_date'], errors='coerce')
        df = df.sort_values('upload_date')
        
        # Calculate rolling averages
        df['likes_ma'] = df['likes'].rolling(window=window_days, min_periods=1).mean()
        df['comments_ma'] = df['comments'].rolling(window=window_days, min_periods=1).mean()
        
        # Calculate trend
        recent_avg_likes = df['likes'].tail(window_days).mean()
        older_avg_likes = df['likes'].head(window_days).mean()
        
        recent_avg_comments = df['comments'].tail(window_days).mean()
        older_avg_comments = df['comments'].head(window_days).mean()
        
        likes_change = ((recent_avg_likes - older_avg_likes) / older_avg_likes * 100) if older_avg_likes > 0 else 0
        comments_change = ((recent_avg_comments - older_avg_comments) / older_avg_comments * 100) if older_avg_comments > 0 else 0
        
        # Determine trend
        trend = "stable"
        if likes_change > 20:
            trend = "strongly_increasing"
        elif likes_change > 10:
            trend = "increasing"
        elif likes_change < -20:
            trend = "strongly_decreasing"
        elif likes_change < -10:
            trend = "decreasing"
        
        return {
            "overall_trend": trend,
            "likes_change_percent": round(likes_change, 2) if not (isinstance(likes_change, float) and math.isnan(likes_change)) else 0.0,
            "comments_change_percent": round(comments_change, 2) if not (isinstance(comments_change, float) and math.isnan(comments_change)) else 0.0,
            "recent_avg_likes": self._safe_int_value(recent_avg_likes),
            "recent_avg_comments": self._safe_int_value(recent_avg_comments),
            "alert": self._get_trend_alert(trend, likes_change if likes_change == likes_change else 0.0),
            "recommendation": self._get_trend_recommendation(trend)
        }
    
    def detect_engagement_drop(self, df: pd.DataFrame, threshold: float = 0.3) -> Dict[str, Any]:
        """Detect significant drops in engagement by comparing recent vs prior posts.

        Logic
        -----
        - Compare last 5 posts to the previous 5 posts.
        - Signal a drop if mean engagement decreases beyond the threshold percentage.

        Returns
        -------
        Dict[str, Any]
            Drop flag, change percent, averages, severity, alert, and possible causes.
        """
        df['upload_date'] = pd.to_datetime(df['upload_date'], errors='coerce')
        df = df.sort_values('upload_date')
        
        if len(df) < 10:
            return {"status": "insufficient_data"}
        
        # Compare last 5 posts to previous 5 posts
        recent_posts = df.tail(5)
        previous_posts = df.tail(10).head(5)
        
        recent_engagement = (recent_posts['likes'] + recent_posts['comments']).mean()
        previous_engagement = (previous_posts['likes'] + previous_posts['comments']).mean()
        
        if previous_engagement == 0:
            return {"status": "no_baseline"}
        
        change_percent = ((recent_engagement - previous_engagement) / previous_engagement) * 100
        
        drop_detected = change_percent < -(threshold * 100)
        
        # NaN-safe handling
        safe_change = (0.0 if (isinstance(change_percent, float) and math.isnan(change_percent)) else change_percent)
        return {
            "drop_detected": drop_detected if not (isinstance(drop_detected, float) and math.isnan(drop_detected)) else False,
            "change_percent": round(safe_change, 2),
            "recent_avg_engagement": self._safe_int_value(recent_engagement),
            "previous_avg_engagement": self._safe_int_value(previous_engagement),
            "severity": "high" if safe_change < -50 else "medium" if safe_change < -30 else "low",
            "alert_message": f"⚠️ Engagement dropped by {abs(safe_change):.1f}%! Investigate recent content quality." if safe_change < -(threshold * 100) else "✅ Engagement is stable or improving",
            "possible_causes": self._suggest_drop_causes() if safe_change < -(threshold * 100) else []
        }
    
    def _rule_based_detection(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Rule-based anomaly detection when ML model is unavailable.

        Uses 3 standard deviation thresholds around the mean of likes/comments. This
        method is simple, transparent, and provides a safety net for low-data regimes.
        """
        anomalies = []
        
        # Calculate derived parameters for rule-based detection too
        followers = df['followers'].fillna(1000) if 'followers' in df.columns else pd.Series([1000] * len(df))
        df['responsiveness_index'] = ((df['comments'] + df.get('shares', 0)) / followers) * 10000
        
        max_engagement = (df['likes'] + df['comments']).max()
        df['peak_performance'] = ((df['likes'] + df['comments']) / max_engagement * 100) if max_engagement > 0 else 0
        
        # Calculate basic statistics
        avg_likes = df['likes'].mean()
        std_likes = df['likes'].std()
        avg_comments = df['comments'].mean()
        std_comments = df['comments'].std()
        
        # Define thresholds (3 standard deviations)
        likes_upper = avg_likes + (3 * std_likes)
        likes_lower = max(0, avg_likes - (3 * std_likes))
        comments_upper = avg_comments + (3 * std_comments)
        comments_lower = max(0, avg_comments - (3 * std_comments))
        
        def _safe_int(val):
            try:
                if val is None:
                    return 0
                if isinstance(val, float) and math.isnan(val):
                    return 0
                return int(val)
            except Exception:
                return 0

        for idx, row in df.iterrows():
            is_anomaly = False
            anomaly_type = []
            
            # Check for likes anomalies
            if row['likes'] > likes_upper:
                is_anomaly = True
                anomaly_type.append("viral_spike")
            elif row['likes'] < likes_lower:
                is_anomaly = True
                anomaly_type.append("low_likes")
            
            # Check for comments anomalies
            if row['comments'] > comments_upper:
                is_anomaly = True
                anomaly_type.append("high_engagement")
            elif row['comments'] < comments_lower:
                is_anomaly = True
                anomaly_type.append("low_engagement")
            
            if is_anomaly:
                deviation_likes = self._calc_deviation(row['likes'], avg_likes)
                deviation_comments = self._calc_deviation(row['comments'], avg_comments)
                
                anomalies.append({
                    'post_url': row.get('post_url', 'N/A'),
                    'platform': row.get('platform', 'N/A'),
                    'date': str(row.get('upload_date', 'N/A')),
                    'type': ', '.join(anomaly_type),
                    'severity': 'high' if abs(deviation_likes) > 200 else 'medium',
                    'metric_values': {
                        'likes': _safe_int(row.get('likes', 0)),
                        'comments': _safe_int(row.get('comments', 0)),
                        'views': _safe_int(row.get('views', 0)),
                        'responsiveness_index': round(row.get('responsiveness_index', 0), 2),
                        'peak_performance': round(row.get('peak_performance', 0), 1)
                    },
                    'deviation': {
                        'likes': f"{deviation_likes}%",
                        'comments': f"{deviation_comments}%"
                    },
                    'alert_message': f"{'🔥 Viral content!' if 'viral_spike' in anomaly_type else '⚠️ Underperforming content'}"
                })
        
        return sorted(anomalies, key=lambda x: abs(float(x['deviation']['likes'].strip('%'))), reverse=True)[:10]
    
    def _classify_anomaly_type(self, row: pd.Series, features: pd.Series) -> str:
        """Classify the type of anomaly based on baselines and engagement ratios."""
        likes = row.get('likes', 0)
        comments = row.get('comments', 0)
        views = row.get('views', 0)
        
        avg_likes = self.baseline_metrics['avg_likes']
        avg_comments = self.baseline_metrics['avg_comments']
        
        if likes > avg_likes * 2:
            return "viral_spike"
        elif likes < avg_likes * 0.3:
            return "low_performance"
        elif comments > avg_comments * 3:
            return "controversial"
        elif views > 0 and (likes + comments) / views < 0.01:
            return "low_engagement"
        else:
            return "unusual_pattern"
    
    def _calculate_severity(self, anomaly_score: float) -> str:
        """Calculate severity based on IsolationForest anomaly score.

        Scores are typically negative; more negative implies more anomalous.
        Thresholds can be tuned with real data distributions.
        """
        # Isolation Forest scores are negative, more negative = more anomalous
        if anomaly_score < -0.5:
            return "high"
        elif anomaly_score < -0.3:
            return "medium"
        else:
            return "low"
    
    def _calc_deviation(self, value: float, baseline: float) -> float:
        """Calculate percentage deviation from baseline, NaN-safe for baseline=0."""
        if baseline == 0:
            return 0
        return round(((value - baseline) / baseline) * 100, 1)
    
    def _generate_alert_message(self, row: pd.Series, features: pd.Series) -> str:
        """Generate human-readable alert message contextualized by anomaly type."""
        anomaly_type = self._classify_anomaly_type(row, features)
        
        messages = {
            "viral_spike": f"🔥 Viral content detected! {self._safe_int_value(row.get('likes', 0)):,} likes - {row.get('caption', '')[:50]}...",
            "low_performance": f"⚠️ Underperforming post: only {self._safe_int_value(row.get('likes', 0)):,} likes",
            "controversial": f"💬 High engagement: {self._safe_int_value(row.get('comments', 0)):,} comments - may be controversial",
            "low_engagement": f"📉 Low engagement rate detected",
            "unusual_pattern": f"🔍 Unusual engagement pattern detected"
        }
        
        return messages.get(anomaly_type, "Anomaly detected")
    
    def _get_trend_alert(self, trend: str, change: float) -> str:
        """Generate alert messaging based on trend and magnitude of change."""
        if trend == "strongly_decreasing":
            return f"🚨 ALERT: Engagement dropping rapidly (-{abs(change):.1f}%)"
        elif trend == "decreasing":
            return f"⚠️ Warning: Engagement declining (-{abs(change):.1f}%)"
        elif trend == "strongly_increasing":
            return f"🚀 Excellent: Engagement surging (+{change:.1f}%)"
        elif trend == "increasing":
            return f"📈 Good: Engagement improving (+{change:.1f}%)"
        else:
            return "✅ Engagement is stable"
    
    def _get_trend_recommendation(self, trend: str) -> str:
        """Get actionable recommendation based on the detected trend label."""
        recommendations = {
            "strongly_decreasing": "Urgent action needed: Review recent content strategy, analyze competitor activity, and consider A/B testing new approaches",
            "decreasing": "Review content quality and posting times. Consider refreshing your content strategy",
            "stable": "Maintain current strategy but look for opportunities to innovate and grow",
            "increasing": "Great work! Double down on what's working and document successful patterns",
            "strongly_increasing": "Capitalize on this momentum! Increase posting frequency and engage with your growing audience"
        }
        return recommendations.get(trend, "Monitor metrics closely")
    
    def _suggest_drop_causes(self) -> List[str]:
        """Suggest possible causes for engagement drops for analyst follow-up."""
        return [
            "Algorithm changes on the platform",
            "Content quality or relevance decreased",
            "Posting at non-optimal times",
            "Increased competition in your niche",
            "Audience fatigue or changing interests",
            "Technical issues (hashtags, reach limits)",
            "Seasonal trends or external events"
        ]


# Global instance
def _load_or_create_detector() -> AnomalyDetector:
    inst = AnomalyDetector()
    scaler = load_model("anomaly_scaler")
    model = load_model("anomaly_model")
    if scaler is not None and model is not None:
        inst.scaler = scaler
        inst.model = model
        inst.is_trained = True
    return inst

detector = _load_or_create_detector()


def train_detector(df: pd.DataFrame) -> Dict[str, Any]:
    """Train the global detector instance and return training metadata."""
    return detector.train(df)


def find_anomalies(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Find anomalies in data using the global detector instance."""
    return detector.detect_anomalies(df)


def analyze_trends(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze engagement trends using rolling averages and thresholding."""
    return detector.detect_trends(df)


def check_engagement_drop(df: pd.DataFrame) -> Dict[str, Any]:
    """Check for engagement drops by comparing contiguous 5-post windows."""
    return detector.detect_engagement_drop(df)
