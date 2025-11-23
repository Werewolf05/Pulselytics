"""
Model persistence helpers (save/load + registry management).
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

from .config import STORE_DIRNAME, REGISTRY_FILENAME


def _store_dir() -> str:
    base = os.path.dirname(__file__)
    path = os.path.join(base, STORE_DIRNAME)
    os.makedirs(path, exist_ok=True)
    return path


def registry_path() -> str:
    return os.path.join(_store_dir(), REGISTRY_FILENAME)


def load_registry() -> Dict[str, Any]:
    path = registry_path()
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_registry(reg: Dict[str, Any]) -> None:
    path = registry_path()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(reg, f, indent=2, ensure_ascii=False)


def model_filepath(name: str, version: str) -> str:
    return os.path.join(_store_dir(), f"{name}_v{version}.joblib")


def _features_path() -> str:
    return os.path.join(_store_dir(), "predictor_features.json")


def save_model(name: str, version: str, model: Any, metadata: Dict[str, Any]) -> bool:
    if not JOBLIB_AVAILABLE:
        return False
    try:
        joblib.dump(model, model_filepath(name, version))
        reg = load_registry()
        reg[name] = {
            'version': version,
            **metadata
        }
        save_registry(reg)
        return True
    except Exception:
        return False


def save_feature_names(feature_names: List[str]) -> None:
    """Persist predictor feature names for alignment after reload."""
    try:
        with open(_features_path(), 'w', encoding='utf-8') as f:
            json.dump({'feature_names': feature_names}, f)
    except Exception:
        # best-effort only
        pass


def load_feature_names() -> List[str]:
    """Load persisted feature names if available."""
    try:
        path = _features_path()
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                names = data.get('feature_names')
                if isinstance(names, list):
                    return names
    except Exception:
        return []
    return []


def load_model(name: str) -> Any:
    reg = load_registry()
    entry = reg.get(name)
    if not entry or not JOBLIB_AVAILABLE:
        return None
    version = entry.get('version')
    path = model_filepath(name, version)
    if not os.path.exists(path):
        return None
    try:
        return joblib.load(path)
    except Exception:
        return None
