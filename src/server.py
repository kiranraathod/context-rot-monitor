
from mcp.server.fastmcp import FastMCP
from src.core.tokenizer import Tokenizer
from src.core.scorer import ContextHealthScorer, HealthScoreInput
from src.core.detector import ContextRotDetector
from src.core.remediator import ContextRemediator
from src.resources.health import get_health_resource, update_health_resource
from src.resources.alerts import get_active_alerts, add_alert, clear_alerts
from src.resources.history import get_metrics_history, save_metrics
import datetime
import json
import os

# Initialize Server
mcp = FastMCP("context-rot-monitor")

# Initialize core components
tokenizer = Tokenizer()
scorer = ContextHealthScorer()
_detector = None 
_remediator = None

def get_detector():
    global _detector
    if _detector is None:
        _detector = ContextRotDetector()
    return _detector

def get_remediator():
    global _remediator
    if _remediator is None:
        api_key = os.environ.get("GOOGLE_API_KEY")
        _remediator = ContextRemediator(api_key=api_key)
    return _remediator

@mcp.tool()
def get_token_metrics(context_text: str, max_window_size: int = 128000) -> dict:
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
    token_count = tokenizer.count_tokens(context_text)
    max_window = 128000
    utilization = token_count / max_window

    relevance_score = 1.0
    redundancy_ratio = 0.0
    
    if goal and len(context_text) > 500:
        detector = get_detector()
        chunk_size = 1000
        chunks = [context_text[i:i+chunk_size] for i in range(0, len(context_text), chunk_size)]
        
        relevance_score = detector.compute_relevance_score(chunks, goal)
        redundancy_ratio, _ = detector.check_redundancy(chunks)
        
        if relevance_score < 0.5:
            add_alert("ROT_DRIFT", f"Relevance dropped to {relevance_score:.2f}", "WARNING")
        if redundancy_ratio > 0.3:
            add_alert("ROT_REDUNDANCY", f"Redundancy is high: {redundancy_ratio:.1%}", "WARNING")

    health_input = HealthScoreInput(
        utilization_ratio=utilization,
        relevance_score=relevance_score,
        redundancy_ratio=redundancy_ratio,
        coherence_score=1.0, 
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

    # Save to history DB
    save_metrics(result)

    update_health_resource({
        "score": result["health_score"],
        "status": result["status"],
        "timestamp": datetime.datetime.now().isoformat(),
        "latest_analysis": result,
    })

    return result

@mcp.tool()
def detect_context_rot(context_text: str, goal: str, chunk_size: int = 1000) -> dict:
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
        "redundant_snippets": snippets[:3],
        "positional_risk_level": pos_risk
    }

@mcp.tool()
def recommend_pruning(context_text: str, goal: str = "") -> dict:
    """
    Suggest chunks of context to remove to improve health.
    """
    remediator = get_remediator()
    detector = get_detector()
    
    chunk_size = 1000
    chunks = [context_text[i:i+chunk_size] for i in range(0, len(context_text), chunk_size)]
    
    try:
        if goal:
            # Re-encoding locally for per-chunk scores
            goal_emb = detector.model.encode(goal)
            chunk_embs = detector.model.encode(chunks)
            from sklearn.metrics.pairwise import cosine_similarity
            # returns shape (1, n_chunks)
            sims = cosine_similarity([goal_emb], chunk_embs)[0]
            relevance_scores = sims.tolist()
        else:
            relevance_scores = [1.0] * len(chunks)
    except:
        relevance_scores = [1.0] * len(chunks)
        
    redundancy = [False] * len(chunks) # TODO: Implement per-chunk redundancy flags properly
    
    recommendations = remediator.recommend_pruning(chunks, relevance_scores, redundancy)
    return {"pruning_recommendations": recommendations}

@mcp.tool()
def summarize_context(context_text: str) -> str:
    """
    Compress the context using an LLM summary.
    Requires GOOGLE_API_KEY.
    """
    remediator = get_remediator()
    return remediator.summarize_context(context_text)

@mcp.resource("rot://health/current")
def current_health() -> str:
    return get_health_resource()

@mcp.resource("rot://alerts/active")
def active_alerts() -> str:
    return get_active_alerts()

@mcp.resource("rot://metrics/history")
def metrics_history() -> str:
    """
    Historical health scores and metrics (last 50).
    """
    return get_metrics_history()


from src.prompts.templates import DIAGNOSE_ROT_PROMPT, OPTIMIZE_CONTEXT_PROMPT
import argparse

# Register prompts (parameter-free so Claude Desktop doesn't show manual input dialogs)
@mcp.prompt("diagnose_rot")
def diagnose_rot() -> str:
    return DIAGNOSE_ROT_PROMPT

@mcp.prompt("optimize_context")
def optimize_context() -> str:
    return OPTIMIZE_CONTEXT_PROMPT

def main():
    parser = argparse.ArgumentParser(description="Context Rot Monitor MCP Server")
    parser.add_argument(
        "--transport", 
        default="stdio", 
        choices=["stdio", "sse"], 
        help="Transport protocol to use (stdio or sse)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port for SSE transport (default: 8000)"
    )
    args = parser.parse_args()

    if args.transport == "sse":
        print(f"Starting SSE server on port {args.port}...")
        # FastMCP run method handles transport selection if supported,
        # but the current mcp version might have different API.
        # Checking FastMCP docs/source implies usage:
        mcp.run(transport="sse", port=args.port)
    else:
        mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
