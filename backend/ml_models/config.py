"""
Central configuration for ML models in Pulselytics.

This file centralizes thresholds, versioning, and tunables so that
production changes are controlled in one place.
"""

# Semantic model versions. Bump minor when feature set changes,
# bump major when model class/hyperparameters materially change.
PREDICTOR_VERSION = "1.1"
ANOMALY_VERSION = "1.0"

# Training data requirements
MIN_TRAIN_SAMPLES_PREDICTOR = 50
MIN_TRAIN_SAMPLES_DETECTOR = 30

# Anomaly detector parameters
ANOMALY_CONTAMINATION = 0.1
ANOMALY_ESTIMATORS = 100

# Persistence
STORE_DIRNAME = "store"
REGISTRY_FILENAME = "model_registry.json"
