
from typing import Any

# Simple in-memory store for now
_current_health_state = {
    "score": 100.0,
    "status": "HEALTHY",
    "timestamp": None
}

def update_health_resource(data: dict[str, Any]):
    global _current_health_state
    _current_health_state.update(data)

def get_health_resource() -> str:
    import json
    return json.dumps(_current_health_state, indent=2)
