
from typing import Any
from src.core.tokenizer import Tokenizer


class MetricsTools:
    """Token metrics computation for context analysis."""

    def __init__(self):
        self.tokenizer = Tokenizer()

    def get_token_metrics(
        self, context_text: str, max_window_size: int = 128000
    ) -> dict[str, Any]:
        """
        Get token counts and utilization metrics for the given context.
        """
        current_tokens = self.tokenizer.count_tokens(context_text)
        utilization_ratio = (
            current_tokens / max_window_size if max_window_size > 0 else 0.0
        )

        return {
            "current_tokens": current_tokens,
            "max_window_size": max_window_size,
            "utilization_ratio": round(utilization_ratio, 4),
            "utilization_percentage": round(utilization_ratio * 100, 2),
            "is_critical": utilization_ratio > 0.9,
            "is_warning": utilization_ratio > 0.8,
        }
