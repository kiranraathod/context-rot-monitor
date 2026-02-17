
from mcp.server.fastmcp import FastMCP
from src.core.tokenizer import Tokenizer
from src.core.scorer import ContextHealthScorer, HealthScoreInput
from src.resources.health import get_health_resource, update_health_resource
import datetime
import json

# Initialize Server
mcp = FastMCP("context-rot-monitor")

# Initialize core components
tokenizer = Tokenizer()
scorer = ContextHealthScorer()


@mcp.tool()
def get_token_metrics(context_text: str, max_window_size: int = 128000) -> dict:
    """
    Get token counts and utilization metrics for the given context.

    Returns current token count, utilization ratio, utilization percentage,
    and warning/critical flags based on how full the context window is.
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
    context_text: str, step_number: int = 1, model_name: str = "gpt-4o"
) -> dict:
    """
    Compute composite Context Health Score (0-100) for current context.

    Analyzes token utilization and produces a health score with status
    label (HEALTHY / DEGRADING / CRITICAL). In Phase 1, only token
    utilization is measured; relevance, redundancy, and coherence
    scoring will be added in Phase 2.
    """
    token_count = tokenizer.count_tokens(context_text)
    max_window = 128000
    utilization = token_count / max_window

    health_input = HealthScoreInput(
        utilization_ratio=utilization,
        relevance_score=1.0,   # Placeholder — Phase 2
        redundancy_ratio=0.0,  # Placeholder — Phase 2
        coherence_score=1.0,   # Placeholder — Phase 2
    )

    score = scorer.calculate_score(health_input)
    status = scorer.get_status_label(score)

    result = {
        "health_score": round(score, 1),
        "status": status,
        "metrics": {
            "token_count": token_count,
            "utilization_ratio": round(utilization, 4),
        },
        "step_number": step_number,
        "model": model_name,
    }

    # Update the health resource with latest analysis
    update_health_resource(
        {
            "score": result["health_score"],
            "status": result["status"],
            "timestamp": datetime.datetime.now().isoformat(),
            "latest_analysis": result,
        }
    )

    return result


@mcp.resource("rot://health/current")
def current_health() -> str:
    """
    Real-time Context Health Score (0-100).
    Returns JSON with score, status, and timestamp of last analysis.
    """
    return get_health_resource()


def main():
    mcp.run()


if __name__ == "__main__":
    main()
