
from typing import Any
from src.core.tokenizer import Tokenizer
from src.core.scorer import ContextHealthScorer, HealthScoreInput


class AnalyzeTools:
    """Context health analysis tool logic."""

    def __init__(self):
        self.tokenizer = Tokenizer()
        self.scorer = ContextHealthScorer()

    def analyze_context_health(
        self,
        context_text: str,
        step_number: int,
        model_name: str = "gpt-4o",
    ) -> dict[str, Any]:
        """
        Compute composite health score for current context.
        """
        token_count = self.tokenizer.count_tokens(context_text)
        max_window = 128000
        utilization = token_count / max_window

        health_input = HealthScoreInput(
            utilization_ratio=utilization,
            relevance_score=1.0,   # Placeholder — Phase 2
            redundancy_ratio=0.0,  # Placeholder — Phase 2
            coherence_score=1.0,   # Placeholder — Phase 2
        )

        score = self.scorer.calculate_score(health_input)
        status = self.scorer.get_status_label(score)

        return {
            "health_score": round(score, 1),
            "status": status,
            "metrics": {
                "token_count": token_count,
                "utilization_ratio": round(utilization, 4),
            },
            "step_number": step_number,
            "model": model_name,
        }
