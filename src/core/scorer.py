
from dataclasses import dataclass
from typing import Optional

@dataclass
class HealthScoreInput:
    utilization_ratio: float
    relevance_score: float = 1.0  # Default to 1.0 if not yet computed
    redundancy_ratio: float = 0.0 # Default to 0.0 if not checked
    coherence_score: float = 1.0  # Default to 1.0 if not checked

class ContextHealthScorer:
    # Weights for the composite score
    W_UTILIZATION = 0.4
    W_RELEVANCE = 0.3
    W_REDUNDANCY = 0.2
    W_COHERENCE = 0.1

    def calculate_score(self, input_data: HealthScoreInput) -> float:
        """
        Calculate Context Health Score (CHS) from 0 to 100.
        Higher is better.
        
        CHS = w1*(1 - utilization) + w2*relevance + w3*(1 - redundancy) + w4*coherence
        """
        
        # Invert negative signals (utilization and redundancy)
        # We want low utilization and low redundancy for high health
        
        score = (
            self.W_UTILIZATION * (1.0 - input_data.utilization_ratio) +
            self.W_RELEVANCE * input_data.relevance_score +
            self.W_REDUNDANCY * (1.0 - input_data.redundancy_ratio) +
            self.W_COHERENCE * input_data.coherence_score
        )
        
        # Clamp between 0 and 1, then scale to 100
        return max(0.0, min(1.0, score)) * 100.0

    def get_status_label(self, score: float) -> str:
        if score >= 80:
            return "HEALTHY"
        elif score >= 50:
            return "DEGRADING"
        else:
            return "CRITICAL"
