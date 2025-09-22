"""
Application configuration loader and accessors.

Provides a minimal API to read the JSON config and expose typed helpers used
by UI and engine modules. Designed to avoid heavy dependencies and keep fast
startup.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

_APP_CONFIG: Optional[Dict[str, Any]] = None


def _config_path() -> Path:
    """Resolve the app_config.json path relative to project root.

    Assumes this file is located under src/common/; project root is two levels up.
    """
    root = Path(__file__).resolve().parents[2]
    return root / "config" / "app_config.json"


def get_app_config() -> Dict[str, Any]:
    """Return the application configuration as a dictionary (cached)."""
    global _APP_CONFIG
    if _APP_CONFIG is not None:
        return _APP_CONFIG

    cfg: Dict[str, Any] = {}
    try:
        with _config_path().open("r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        # Fallback to minimal defaults if config is missing or invalid
        cfg = {
            "nodes": {
                "strict_unique_id": False,
            }
        }

    _APP_CONFIG = cfg
    return _APP_CONFIG


def is_strict_unique_id() -> bool:
    """Whether to enforce strict unique_id-only property resolution.

    When True, the PropertyPanel will NOT fall back to name/alias-based
    resolution. This removes ambiguity and enforces contract compliance.
    """
    return get_app_config().get("nodes", {}).get("strict_unique_id", False)
