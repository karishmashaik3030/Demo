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

def compute_global_stats() -> dict:
    """Compute simple stats across the resource store."""
    count = len(_RESOURCES_STORE)
    if count == 0:
        return {"count": 0, "avg_score": None}
    scores = [item.get("score", 0) for item in _RESOURCES_STORE.values() if isinstance(item.get("score", 0), (int, float))]
    avg = sum(scores) / len(scores) if scores else 0
    return {"count": count, "avg_score": avg, "as_of": _now_iso()}

# ---------------------------------------------------------------------
# Primary business CRUD functions (core resource)
# ---------------------------------------------------------------------

def validate_base_resource(data: dict):
    """Validate required fields for the base resource."""
    _validate_string_field(data, "name", True)
    _validate_string_field(data, "type", True)
    _validate_integer_field(data, "score", False)
    return True

def create_resource(data: dict) -> dict:
    """Create a resource with some default fields."""
    validate_base_resource(data)
    item_id = _next_id()
    now = _now_iso()
    item = {
        "id": item_id,
        "name": data["name"],
        "type": data["type"],
        "score": int(data.get("score", 0)) if data.get("score") is not None else 0,
        "metadata": data.get("metadata", {}),
        "created_at": now,
        "updated_at": now
    }
    # business rule: auto-tag high-score items
    if item["score"] >= 80:
        item.setdefault("tags", []).append("high-score")
    _RESOURCES_STORE[item_id] = item
    return item

def get_resource(item_id: int) -> Optional[dict]:
    """Return the resource or None."""
    return _RESOURCES_STORE.get(item_id)

def update_resource(item_id: int, data: dict) -> dict:
    """Update an existing resource, return the updated item."""
    if item_id not in _RESOURCES_STORE:
        raise KeyError("resource not found")
    existing = _RESOURCES_STORE[item_id]
    # allowed updates: name, type, score, metadata
    if "name" in data:
        _validate_string_field(data, "name", True)
        existing["name"] = data["name"]
    if "type" in data:
        _validate_string_field(data, "type", True)
        existing["type"] = data["type"]
    if "score" in data:
        _validate_integer_field(data, "score")
        existing["score"] = int(data["score"])
    if "metadata" in data:
        # merge metadata heuristically
        if not isinstance(data["metadata"], dict):
            raise ValueError("metadata must be an object")
        existing.setdefault("metadata", {}).update(data["metadata"])
    existing["updated_at"] = _now_iso()
    # business rule: ensure tags reflect score
    tags = existing.setdefault("tags", [])
    if existing["score"] >= 80 and "high-score" not in tags:
        tags.append("high-score")
    if existing["score"] < 80 and "high-score" in tags:
        tags.remove("high-score")
    _RESOURCES_STORE[item_id] = existing
    return existing

def delete_resource(item_id: int) -> Optional[dict]:
    """Delete resource and return it if existed."""
    return _RESOURCES_STORE.pop(item_id, None)

# ---------------------------------------------------------------------
# Additional rich business logic helpers and simulation functions
# ---------------------------------------------------------------------

def compute_resource_risk(item: dict) -> float:
    """Sample business logic computing a risk metric."""
    # risk ranges 0..1
    score = float(item.get("score", 0))
    risk = max(0.0, min(1.0, (100.0 - score) / 100.0))
    # boost risk for missing metadata
    if not item.get("metadata"):
        risk = min(1.0, risk + 0.1)
    return risk

def enrich_resource_with_insights(item: dict) -> dict:
    """Return a copy of item enriched with derived insights."""
    enriched = dict(item)
    enriched["risk"] = compute_resource_risk(item)
    enriched["insights"] = {
        "recommended_action": "review" if enriched["risk"] > 0.5 else "monitor",
        "score_bucket": "high" if enriched["score"] >= 80 else "low"
    }
    return enriched

def find_resources_by_tag(tag: str) -> List[dict]:
    """Return resources that have a given tag."""
    return [r for r in _RESOURCES_STORE.values() if tag in r.get("tags", [])]

# ---------------------------------------------------------------------
# Now we create many repeated resource-specific handlers to mimic a large file.
# Each block below is a self-contained mini-subsystem (e.g., Resource A, B, ...).
# In a real codebase these would be separate modules; here they are repeated to
# model a file with many responsibilities.
# ---------------------------------------------------------------------

# -------------------- Resource Subsystem 1 --------------------
_RESOURCE_A_STORE = {}

def validate_resource_a(data: dict):
    if "name" not in data:
        raise ValueError("name required for resource A")
    return True

def create_resource_a(data: dict):
    validate_resource_a(data)
    _id = _next_id()
    item = {"id": _id, "name": data["name"], "created_at": _now_iso(), "payload": data.get("payload", {})}
    _RESOURCE_A_STORE[_id] = item
    return item

def get_resource_a(item_id: int):
    return _RESOURCE_A_STORE.get(item_id)

def update_resource_a(item_id: int, data: dict):
    if item_id not in _RESOURCE_A_STORE:
        raise KeyError("not found")
    _RESOURCE_A_STORE[item_id].update(data)
    _RESOURCE_A_STORE[item_id]["updated_at"] = _now_iso()
    return _RESOURCE_A_STORE[item_id]

def delete_resource_a(item_id: int):
    return _RESOURCE_A_STORE.pop(item_id, None)

def list_resource_a(limit: int = 50):
    return list(_RESOURCE_A_STORE.values())[:limit]

# -------------------- Resource Subsystem 2 --------------------
_RESOURCE_B_STORE = {}

def validate_resource_b(data: dict):
    if "title" not in data:
        raise ValueError("title required for resource B")
    return True

def create_resource_b(data: dict):
    validate_resource_b(data)
    _id = _next_id()
    item = {"id": _id, "title": data["title"], "score": int(data.get("score", 0))}
    _RESOURCE_B_STORE[_id] = item
    return item

def get_resource_b(item_id: int):
    return _RESOURCE_B_STORE.get(item_id)

def update_resource_b(item_id: int, data: dict):
    if item_id not in _RESOURCE_B_STORE:
        raise KeyError("not found")
    _RESOURCE_B_STORE[item_id].update(data)
    return _RESOURCE_B_STORE[item_id]

def delete_resource_b(item_id: int):
    return _RESOURCE_B_STORE.pop(item_id, None)

def search_resource_b(term: str):
    term_lower = term.lower()
    return [v for v in _RESOURCE_B_STORE.values() if term_lower in v.get("title", "").lower()]

# -------------------- Resource Subsystem 3 --------------------
_RESOURCE_C_STORE = {}

def validate_resource_c(data: dict):
    if "username" not in data:
        raise ValueError("username required for resource C")
    return True

def create_resource_c(data: dict):
    validate_resource_c(data)
    _id = _next_id()
    item = {
        "id": _id,
        "username": data["username"],
        "email": data.get("email"),
        "joined": _now_iso()
    }
    _RESOURCE_C_STORE[_id] = item
    return item

def get_resource_c(item_id: int):
    return _RESOURCE_C_STORE.get(item_id)

def update_resource_c(item_id: int, data: dict):
    if item_id not in _RESOURCE_C_STORE:
        raise KeyError("not found")
    _RESOURCE_C_STORE[item_id].update(data)
    return _RESOURCE_C_STORE[item_id]

def delete_resource_c(item_id: int):
    return _RESOURCE_C_STORE.pop(item_id, None)

def list_recent_resource_c(days: int = 7):
    cutoff = datetime.utcnow() - timedelta(days=days)
    results = []
    for v in _RESOURCE_C_STORE.values():
        joined = v.get("joined")
        if joined:
            try:
                dt = datetime.fromisoformat(joined.replace("Z", ""))
                if dt >= cutoff:
                    results.append(v)
            except Exception:
                continue
    return results

# -------------------- Resource Subsystem 4 --------------------
_RESOURCE_D_STORE = {}

def validate_resource_d(data: dict):
    if "identifier" not in data:
        raise ValueError("identifier required for resource D")
    return True

def create_resource_d(data: dict):
    validate_resource_d(data)
    _id = _next_id()
    item = {"id": _id, "identifier": data["identifier"], "meta": data.get("meta", {})}
    _RESOURCE_D_STORE[_id] = item
    return item

def get_resource_d(item_id: int):
    return _RESOURCE_D_STORE.get(item_id)

def update_resource_d(item_id: int, data: dict):
    if item_id not in _RESOURCE_D_STORE:
        raise KeyError("not found")
    _RESOURCE_D_STORE[item_id].update(data)
    return _RESOURCE_D_STORE[item_id]

def delete_resource_d(item_id: int):
    return _RESOURCE_D_STORE.pop(item_id, None)

def aggregate_resource_d():
    return {"count": len(_RESOURCE_D_STORE)}

# -------------------- Resource Subsystem 5 --------------------
_RESOURCE_E_STORE = {}

def validate_resource_e(data: dict):
    if "key" not in data:
        raise ValueError("key required for resource E")
    return True

def create_resource_e(data: dict):
    validate_resource_e(data)
    _id = _next_id()
    item = {"id": _id, "key": data["key"], "value": data.get("value")}
    _RESOURCE_E_STORE[_id] = item
    return item

def get_resource_e(item_id: int):
    return _RESOURCE_E_STORE.get(item_id)

def update_resource_e(item_id: int, data: dict):
    if item_id not in _RESOURCE_E_STORE:
        raise KeyError("not found")
    _RESOURCE_E_STORE[item_id].update(data)
    return _RESOURCE_E_STORE[item_id]

def delete_resource_e(item_id: int):
    return _RESOURCE_E_STORE.pop(item_id, None)

def find_by_key_e(key: str):
    for v in _RESOURCE_E_STORE.values():
        if v.get("key") == key:
            return v
    return None

# -------------------- Resource Subsystem 6 --------------------
_RESOURCE_F_STORE = {}

def validate_resource_f(data: dict):
    if "label" not in data:
        raise ValueError("label required for resource F")
    return True

def create_resource_f(data: dict):
    validate_resource_f(data)
    _id = _next_id()
    item = {"id": _id, "label": data["label"], "active": bool(data.get("active", True))}
    _RESOURCE_F_STORE[_id] = item
    return item

def get_resource_f(item_id: int):
    return _RESOURCE_F_STORE.get(item_id)

def update_resource_f(item_id: int, data: dict):
    if item_id not in _RESOURCE_F_STORE:
        raise KeyError("not found")
    _RESOURCE_F_STORE[item_id].update(data)
    return _RESOURCE_F_STORE[item_id]

def delete_resource_f(item_id: int):
    return _RESOURCE_F_STORE.pop(item_id, None)

def list_active_f():
    return [v for v in _RESOURCE_F_STORE.values() if v.get("active")]

# -------------------- Resource Subsystem 7 --------------------
_RESOURCE_G_STORE = {}

def validate_resource_g(data: dict):
    if "slug" not in data:
        raise ValueError("slug required for resource G")
    return True

def create_resource_g(data: dict):
    validate_resource_g(data)
    _id = _next_id()
    item = {"id": _id, "slug": data["slug"], "content": data.get("content", "")}
    _RESOURCE_G_STORE[_id] = item
    return item

def get_resource_g(item_id: int):
    return _RESOURCE_G_STORE.get(item_id)

def update_resource_g(item_id: int, data: dict):
    if item_id not in _RESOURCE_G_STORE:
        raise KeyError("not found")
    _RESOURCE_G_STORE[item_id].update(data)
    return _RESOURCE_G_STORE[item_id]

def delete_resource_g(item_id: int):
    return _RESOURCE_G_STORE.pop(item_id, None)

def find_by_slug_g(slug: str):
    for v in _RESOURCE_G_STORE.values():
        if v.get("slug") == slug:
            return v
    return None

# -------------------- Resource Subsystem 8 --------------------
_RESOURCE_H_STORE = {}

def validate_resource_h(data: dict):
    if "owner" not in data:
        raise ValueError("owner required for resource H")
    return True

def create_resource_h(data: dict):
    validate_resource_h(data)
    _id = _next_id()
    item = {"id": _id, "owner": data["owner"], "config": data.get("config", {})}
    _RESOURCE_H_STORE[_id] = item
    return item

def get_resource_h(item_id: int):
    return _RESOURCE_H_STORE.get(item_id)

def update_resource_h(item_id: int, data: dict):
    if item_id not in _RESOURCE_H_STORE:
        raise KeyError("not found")
    _RESOURCE_H_STORE[item_id].update(data)
    return _RESOURCE_H_STORE[item_id]

def delete_resource_h(item_id: int):
    return _RESOURCE_H_STORE.pop(item_id, None)

def owner_stats_h(owner: str):
    return [v for v in _RESOURCE_H_STORE.values() if v.get("owner") == owner]

# -------------------- Resource Subsystem 9 --------------------
_RESOURCE_I_STORE = {}

def validate_resource_i(data: dict):
    if "identifier" not in data:
        raise ValueError("identifier required for I")
    return True

def create_resource_i(data: dict):
    validate_resource_i(data)
    _id = _next_id()
    item = {"id": _id, "identifier": data["identifier"], "meta": data.get("meta", {})}
    _RESOURCE_I_STORE[_id] = item
    return item

def get_resource_i(item_id: int):
    return _RESOURCE_I_STORE.get(item_id)

def update_resource_i(item_id: int, data: dict):
    if item_id not in _RESOURCE_I_STORE:
        raise KeyError("not found")
    _RESOURCE_I_STORE[item_id].update(data)
    return _RESOURCE_I_STORE[item_id]

def delete_resource_i(item_id: int):
    return _RESOURCE_I_STORE.pop(item_id, None)

def export_i():
    return json.dumps(list(_RESOURCE_I_STORE.values()))

# -------------------- Resource Subsystem 10 --------------------
_RESOURCE_J_STORE = {}

def validate_resource_j(data: dict):
    if "key" not in data:
        raise ValueError("key required for J")
    return True

def create_resource_j(data: dict):
    validate_resource_j(data)
    _id = _next_id()
    item = {"id": _id, "key": data["key"], "value": data.get("value")}
    _RESOURCE_J_STORE[_id] = item
    return item

def get_resource_j(item_id: int):
    return _RESOURCE_J_STORE.get(item_id)

def update_resource_j(item_id: int, data: dict):
    if item_id not in _RESOURCE_J_STORE:
        raise KeyError("not found")
    _RESOURCE_J_STORE[item_id].update(data)
    return _RESOURCE_J_STORE[item_id]

def delete_resource_j(item_id: int):
    return _RESOURCE_J_STORE.pop(item_id, None)

def find_j_by_value(value):
    return [v for v in _RESOURCE_J_STORE.values() if v.get("value") == value]

# -------------------- Resource Subsystem 11 --------------------
_RESOURCE_K_STORE = {}

def validate_resource_k(data: dict):
    if "identifier" not in data:
        raise ValueError("identifier required for K")
    return True

def create_resource_k(data: dict):
    validate_resource_k(data)
    _id = _next_id()
    item = {"id": _id, "identifier": data["identifier"], "active": bool(data.get("active", True))}
    _RESOURCE_K_STORE[_id] = item
    return item

def get_resource_k(item_id: int):
    return _RESOURCE_K_STORE.get(item_id)

def update_resource_k(item_id: int, data: dict):
    if item_id not in _RESOURCE_K_STORE:
        raise KeyError("not found")
    _RESOURCE_K_STORE[item_id].update(data)
    return _RESOURCE_K_STORE[item_id]

def delete_resource_k(item_id: int):
    return _RESOURCE_K_STORE.pop(item_id, None)

def count_active_k():
    return sum(1 for v in _RESOURCE_K_STORE.values() if v.get("active"))

# -------------------- Resource Subsystem 12 --------------------
_RESOURCE_L_STORE = {}

def validate_resource_l(data: dict):
    if "name" not in data:
        raise ValueError("name required for L")
    return True

def create_resource_l(data: dict):
    validate_resource_l(data)
    _id = _next_id()
    item = {"id": _id, "name": data["name"], "tags": data.get("tags", [])}
    _RESOURCE_L_STORE[_id] = item
    return item

def get_resource_l(item_id: int):
    return _RESOURCE_L_STORE.get(item_id)

def update_resource_l(item_id: int, data: dict):
    if item_id not in _RESOURCE_L_STORE:
        raise KeyError("not found")
    _RESOURCE_L_STORE[item_id].update(data)
    return _RESOURCE_L_STORE[item_id]

def delete_resource_l(item_id: int):
    return _RESOURCE_L_STORE.pop(item_id, None)

def list_by_tag_l(tag: str):
    return [v for v in _RESOURCE_L_STORE.values() if tag in v.get("tags", [])]

# -------------------- Resource Subsystem 13 --------------------
_RESOURCE_M_STORE = {}

def validate_resource_m(data: dict):
    if "identifier" not in data:
        raise ValueError("identifier required for M")
    return True

def create_resource_m(data: dict):
    validate_resource_m(data)
    _id = _next_id()
    item = {"id": _id, "identifier": data["identifier"], "meta": data.get("meta", {})}
    _RESOURCE_M_STORE[_id] = item
    return item

def get_resource_m(item_id: int):
    return _RESOURCE_M_STORE.get(item_id)

def update_resource_m(item_id: int, data: dict):
    if item_id not in _RESOURCE_M_STORE:
        raise KeyError("not found")
    _RESOURCE_M_STORE[item_id].update(data)
    return _RESOURCE_M_STORE[item_id]

def delete_resource_m(item_id: int):
    return _RESOURCE_M_STORE.pop(item_id, None)

def dump_m():
    return list(_RESOURCE_M_STORE.values())

# -------------------- Resource Subsystem 14 --------------------
_RESOURCE_N_STORE = {}

def validate_resource_n(data: dict):
    if "title" not in data:
        raise ValueError("title required for N")
    return True

def create_resource_n(data: dict):
    validate_resource_n(data)
    _id = _next_id()
    item = {"id": _id, "title": data["title"], "description": data.get("description", "")}
    _RESOURCE_N_STORE[_id] = item
    return item

def get_resource_n(item_id: int):
    return _RESOURCE_N_STORE.get(item_id)

def update_resource_n(item_id: int, data: dict):
    if item_id not in _RESOURCE_N_STORE:
        raise KeyError("not found")
    _RESOURCE_N_STORE[item_id].update(data)
    return _RESOURCE_N_STORE[item_id]

def delete_resource_n(item_id: int):
    return _RESOURCE_N_STORE.pop(item_id, None)
