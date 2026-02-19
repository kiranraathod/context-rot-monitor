
from src.storage.metrics_store import MetricsStore
import json

_store = MetricsStore()

def get_metrics_history(limit: int = 50) -> str:
    """
    Retrieve historical health metrics.
    """
    history = _store.get_history(limit)
    return json.dumps({"history": history}, indent=2)

def save_metrics(data: dict):
    """
    Save current analysis to history.
    """
    _store.add_record(data)
