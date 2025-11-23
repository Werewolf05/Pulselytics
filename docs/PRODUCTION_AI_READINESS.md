# Production AI Readiness Guide

This document summarizes what’s needed to run Pulselytics’ AI features reliably in production.

## Components
- Predictor (engagement): GradientBoostingRegressor for likes/comments (+ optional views)
- Anomaly detector: IsolationForest with rule-based fallback
- Feature store: Lightweight JSON of feature names for alignment
- Model registry: JSON with versions, metadata, and artifact paths (joblib)

## Operational checklist
- Versioning: Predictor v1.1, Anomaly v1.0 (see `backend/ml_models/config.py`)
- Persistence: Ensure `backend/ml_models/store/` is writable and backed up
- CORS/ports: Backend allows localhost dynamic ports for dev; restrict in prod
- Health: `/api/ml/diagnostics` and `/api/ml/models/status` expose load status and registry keys

## Retraining cadence
- Trigger when: +50 new posts or once per week, whichever comes first
- Per-client: Train with client-filtered historical posts (minimums: predictor 50, anomaly 30)
- Store artifacts: scaler + model(s) + metadata under `store/` with registry update

## Data quality guardrails
- NaNs/Infs: Imputed to 0 for features; zero-safe rate calculations
- Targets: Filter out rows with 0 likes/comments for supervised training
- Alignment: Persist feature_names and align at predict time

## Monitoring
- Validation metrics: `val_r2_likes`, `val_r2_comments` persisted in registry
- Drift indicators: Track moving averages of engagement vs quantiles (q10..q90)
- Service SLOs: p95 latency < 300ms for predict endpoint, error rate < 1%
- Alarms: Spike in anomaly count or negative R² trend across retrains

## Rollback
- Keep at least two prior model versions (joblib + registry entries)
- Rollback by setting registry version keys to previous artifacts and restarting app

## Security & privacy
- API keys: Use database-assisted encryption in `backend/database.py`
- Logs: Structured logging for ML endpoints; avoid logging PII/content unnecessarily
- CORS: In prod, set explicit origins (no wildcard localhost regex)

## Deployment notes
- Python 3.10+ recommended; pin scikit-learn and scipy versions
- Warm start: Load models at app start; retrain offline and hot-swap registry
- Containers: Mount `backend/ml_models/store/` as a persistent volume

## Testing
- Run `backend/test_ml_models.py` in CI to catch regressions
- Add smoke tests: call `/api/ml/diagnostics` and `/api/ml/test` after deploy

## Limitations and roadmap
- Forecast endpoint uses a simplified trend model; consider Holt‑Winters or Prophet
- Comments prediction is inherently noisier; expect lower R² than likes
- Future: add per-platform feature enrichments (followers, media type) when available
