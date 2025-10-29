"""
model.py

Large example of business logic for a Flask app.
- In-memory storage (dicts) for quick demo.
- Many repeated resource handlers to simulate a larger codebase.
"""

import json
import math
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# ---------------------------------------------------------------------
# Basic utilities and scaffolding (shared across the file)
# ---------------------------------------------------------------------

_GLOBAL_ID_COUNTER = 0

def _next_id() -> int:
    global _GLOBAL_ID_COUNTER
    _GLOBAL_ID_COUNTER += 1
    return _GLOBAL_ID_COUNTER

def ping() -> str:
    """Simple health-check helper."""
    return "pong"

def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

def _validate_string_field(data: dict, field: str, required: bool = True):
    if required and field not in data:
        raise ValueError(f"'{field}' is required")
    if field in data and not isinstance(data[field], str):
        raise ValueError(f"'{field}' must be a string")
    return True

def _validate_integer_field(data: dict, field: str, required: bool = False):
    if required and field not in data:
        raise ValueError(f"'{field}' is required")
    if field in data:
        try:
            int(data[field])
        except Exception:
            raise ValueError(f"'{field}' must be an integer")
    return True

def _safe_get(d: dict, k: str, default=None):
    return d.get(k, default)

# ---------------------------------------------------------------------
# Global "resources" list + helper methods for the demonstration
# ---------------------------------------------------------------------

# Single canonical store used by the controller endpoints:
_RESOURCES_STORE: Dict[int, dict] = {}

def list_all_resources() -> List[dict]:
    """Return a list of all resources in the store (shallow copy)."""
    return list(_RESOURCES_STORE.values())

def bulk_create_resources(items: List[dict]) -> List[dict]:
    """Create multiple resources in a single call."""
    created = []
    for data in items:
        created.append(create_resource(data))
    return created
