
from mcp.server.fastmcp import FastMCP
from src.core.tokenizer import Tokenizer
from src.core.scorer import ContextHealthScorer, HealthScoreInput
from src.core.detector import ContextRotDetector
from src.resources.health import get_health_resource, update_health_resource
from src.resources.alerts import get_active_alerts, add_alert, clear_alerts
import datetime
import json

# Initialize Server
mcp = FastMCP("context-rot-monitor")

# Initialize core components
tokenizer = Tokenizer()
scorer = ContextHealthScorer()
# Lazily initialized detector to speed up startup if not used
_detector = None 

def get_detector():
    global _detector
    if _detector is None:
        _detector = ContextRotDetector()
    return _detector

@mcp.tool()
def get_token_metrics(context_text: str, max_window_size: int = 128000) -> dict:
    """
    Get token counts and utilization metrics for the given context.
    """
    current_tokens = tokenizer.count_tokens(context_text)
    utilization_ratio = current_tokens / max_window_size if max_window_size > 0 else 0.0

    return {
        "current_tokens": current_tokens,
        "max_window_size": max_window_size,
        "utilization_ratio": round(utilization_ratio, 4),
        "utilization_percentage": round(utilization_ratio * 100, 2),
        "is_warning": utilization_ratio > 0.8,
        "is_critical": utilization_ratio > 0.9,
    }

@mcp.tool()
def analyze_context_health(
    context_text: str, step_number: int = 1, model_name: str = "gpt-4o",
    goal: str = ""
) -> dict:
    """
    Compute composite Context Health Score (0-100).
    Now includes relevance and redundancy checks if 'goal' is provided.
    """
    token_count = tokenizer.count_tokens(context_text)
    max_window = 128000
    utilization = token_count / max_window

    # Phase 2: Real values
    relevance_score = 1.0
    redundancy_ratio = 0.0
    
    if goal and len(context_text) > 500: # Only run heavy analysis on substantial context
        detector = get_detector()
        # Simple chunking
        chunk_size = 1000
        chunks = [context_text[i:i+chunk_size] for i in range(0, len(context_text), chunk_size)]
        
        relevance_score = detector.compute_relevance_score(chunks, goal)
        redundancy_ratio, _ = detector.check_redundancy(chunks)
        
        # Add alerts if needed
        if relevance_score < 0.5:
            add_alert("ROT_DRIFT", f"Relevance dropped to {relevance_score:.2f}", "WARNING")
        if redundancy_ratio > 0.3:
            add_alert("ROT_REDUNDANCY", f"Redundancy is high: {redundancy_ratio:.1%}", "WARNING")

    health_input = HealthScoreInput(
        utilization_ratio=utilization,
        relevance_score=relevance_score,
        redundancy_ratio=redundancy_ratio,
        coherence_score=1.0,   # Placeholder — Phase 3
    )

    score = scorer.calculate_score(health_input)
    status = scorer.get_status_label(score)

    result = {
        "health_score": round(score, 1),
        "status": status,
        "metrics": {
            "token_count": token_count,
            "utilization_ratio": round(utilization, 4),
            "relevance_score": round(relevance_score, 2),
            "redundancy_ratio": round(redundancy_ratio, 2)
        },
        "step_number": step_number,
        "model": model_name,
    }

    update_health_resource({
        "score": result["health_score"],
        "status": result["status"],
        "timestamp": datetime.datetime.now().isoformat(),
        "latest_analysis": result,
    })

    return result

@mcp.tool()
def detect_context_rot(context_text: str, goal: str, chunk_size: int = 1000) -> dict:
    """
    Deep dive rot detection: relevance drift, redundancy clusters, positional risks.
    """
    if not context_text: 
        return {"error": "Empty context"}
    
    detector = get_detector()
    chunks = [context_text[i:i+chunk_size] for i in range(0, len(context_text), chunk_size)]
    
    relevance = detector.compute_relevance_score(chunks, goal)
    redundancy, snippets = detector.check_redundancy(chunks)
    pos_risk = detector.analyze_positional_risk(len(context_text)/4, 128000)
    
    return {
        "relevance_score": round(relevance, 2),
        "redundancy_ratio": round(redundancy, 2),
        "redundant_snippets": snippets[:3], # Limit output size
        "positional_risk_level": pos_risk
    }

@mcp.resource("rot://health/current")
def current_health() -> str:
    return get_health_resource()

@mcp.resource("rot://alerts/active")
def active_alerts() -> str:
    """List active context rot alerts."""
    return get_active_alerts()

def main():
    mcp.run()

if __name__ == "__main__":
    main()
