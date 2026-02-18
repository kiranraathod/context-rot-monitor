
from typing import List, Dict, Any
import datetime

# In-memory alerts store
_active_alerts: List[Dict[str, Any]] = []

def add_alert(alert_type: str, message: str, severity: str):
    """
    Add a new alert to the active list.
    Severity: INFO, WARNING, CRITICAL
    """
    global _active_alerts
    alert = {
        "type": alert_type,
        "message": message,
        "severity": severity,
        "timestamp": datetime.datetime.now().isoformat()
    }
    _active_alerts.append(alert)
    # Keep list manageable
    if len(_active_alerts) > 50:
        _active_alerts.pop(0)

def get_active_alerts() -> str:
    import json
    return json.dumps({"active_alerts": _active_alerts}, indent=2)

def clear_alerts():
    global _active_alerts
    _active_alerts = []
