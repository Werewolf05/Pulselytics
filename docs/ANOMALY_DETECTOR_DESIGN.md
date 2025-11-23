# Anomaly Detector: Model Choice and Design Rationale

This note explains why we use IsolationForest for anomaly detection in social media metrics, how features are prepared, what the outputs mean, and how to tune or extend the system.

## Problem framing

- Goal: flag posts or periods with unusual engagement (likes, comments, views) so analysts can investigate wins and drops.
- Constraints:
  - No ground-truth labels for anomalies (unsupervised setting)
  - Heterogeneous scales (views often >> likes, comments)
  - Messy data (NaNs, missing views, outliers are expected)
  - Need for interpretable fallbacks when data volume is small

## Model choice: IsolationForest (unsupervised)

We chose IsolationForest because it:
- Requires no labels; learns “normal” structure from historical data and isolates outliers.
- Works on multi-dimensional feature space and captures combinations (e.g., high views + low engagement rate) that single-metric z-scores miss.
- Has few hyperparameters with sensible defaults and good runtime characteristics.
- Is widely used, stable, and easy to persist/reload with joblib.

Key hyperparameters:
- contamination: expected proportion of anomalies in data (domain-tunable). Set via `ANOMALY_CONTAMINATION`.
- n_estimators: number of trees (speed vs. stability). Set via `ANOMALY_ESTIMATORS`.

Alternatives considered:
- One-Class SVM: sensitive to scaling, kernel choice, and C/nu tuning; less robust on varied scales and larger datasets.
- Local Outlier Factor (LOF): powerful but not directly suitable for global scoring on new points without careful handling; heavier for large N.
- Simple z-score thresholds: fast and interpretable but limited to univariate checks; misses multi-feature interactions.

## Features and preprocessing

We detect anomalies using these features per post:
- likes
- comments
- views
- engagement_rate = (likes + comments) / max(views, 1)

Preprocessing:
- Standardize with StandardScaler so each feature contributes comparably (preventing views from dominating).
- NaN/None-safe conversions and replaces: missing values are treated as zeros where appropriate.

## Baselines and messaging

We compute dataset baselines to inform:
- Deviations: how far a post is from typical values (e.g., +120% likes vs baseline)
- Type classification: viral_spike, low_performance, controversial, low_engagement, unusual_pattern
- Human-readable alerts: contextual messages tied to the anomaly type

## Fallback for small data

If there’s not enough data to train an ML model (fewer than `MIN_TRAIN_SAMPLES_DETECTOR` rows), the system switches to a rule-based detector:
- 3-sigma thresholds around the mean for likes and comments
- Transparent and stable for low-data regimes

## Outputs and semantics

Per anomaly (post-level):
- type: high-level category (viral_spike, low_performance, etc.)
- severity: low / medium / high based on IsolationForest score thresholds
- metric_values: likes, comments, views (NaN-safe ints)
- deviation: percentage differences vs baselines (likes/comments)
- alert_message: human-readable summary for dashboards and notifications

Contextual signals:
- detect_trends: rolling 7-post averages for likes/comments with trend labels and alerts
- detect_engagement_drop: compares last 5 vs previous 5 posts to flag significant declines

## Tuning guidance

- contamination: increase slightly if you routinely see many spikes (e.g., frequent campaigns); decrease if too many false positives.
- n_estimators: raise for stability on larger datasets; lower for faster training on small sets.
- severity thresholds: `_calculate_severity` uses simple score cutoffs; calibrate using your score distribution (e.g., 25th/10th percentiles of negative scores).
- MIN_TRAIN_SAMPLES_DETECTOR: raise if you want to ensure more stable training; lower if your datasets are typically small.

## Edge cases and safeguards

- No or few posts: use the rule-based fallback; return `insufficient_data` where useful.
- Zero views: engagement_rate denominator uses max(views, 1) to avoid div-by-zero.
- NaNs / non-numeric values: safe conversion paths prevent crashes and default to 0 where applicable.

## Extending the detector

- Add features: time-of-day, day-of-week, caption length, hashtag count. Standardize before training.
- Per-segment models: train per platform or per content type if you have enough samples.
- Seasonality-aware baselines: compute rolling seasonal baselines (e.g., weekly patterns) to improve deviation accuracy.
- Ensemble signals: combine IsolationForest with rule scores and trend signals for a composite risk score.

## Contract (inputs/outputs)

Inputs: Pandas DataFrame with columns
- upload_date (parseable timestamp)
- likes (int), comments (int), views (int; optional but recommended)
- Optional: platform, post_url, caption (used for messages only)

Outputs:
- `detect_anomalies(df)` -> List[Dict]: post-level anomalies with type, severity, metrics, deviations, alert_message
- `detect_trends(df)` -> Dict: overall trend, percentage changes, recent averages, alert and recommendation
- `detect_engagement_drop(df, threshold)` -> Dict: drop_detected flag, change percent, averages, severity, and possible causes

## Limitations and next steps

- Unsupervised anomalies are generic by design; calibrate thresholds per account/vertical for best precision.
- IsolationForest does not inherently explain “why”; we supply derived types and deviations, but SHAP or counterfactuals could add depth.
- With richer history, consider seasonal decomposition or Bayesian change-point detection for trend shifts.

See `backend/ml_models/anomaly_detector.py` for implementation details and docstrings.