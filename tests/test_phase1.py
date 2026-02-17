
import unittest
from src.core.tokenizer import Tokenizer
from src.core.scorer import ContextHealthScorer, HealthScoreInput
from src.tools.metrics import MetricsTools
from src.tools.analyze import AnalyzeTools

class TestPhase1(unittest.TestCase):
    def test_tokenizer(self):
        tokenizer = Tokenizer()
        text = "Hello world"
        count = tokenizer.count_tokens(text)
        self.assertGreater(count, 0)
        self.assertEqual(tokenizer.count_tokens(""), 0)

    def test_scorer(self):
        scorer = ContextHealthScorer()
        # Perfect health input
        input_data = HealthScoreInput(
            utilization_ratio=0.0,
            relevance_score=1.0,
            redundancy_ratio=0.0,
            coherence_score=1.0
        )
        score = scorer.calculate_score(input_data)
        self.assertAlmostEqual(score, 100.0)

        # Worst health input
        input_data_bad = HealthScoreInput(
            utilization_ratio=1.0,
            relevance_score=0.0,
            redundancy_ratio=1.0, # (1-1=0)
            coherence_score=0.0
        )
        score_bad = scorer.calculate_score(input_data_bad)
        self.assertAlmostEqual(score_bad, 0.0)

    def test_metrics_tool(self):
        tool = MetricsTools()
        text = "Hello " * 100
        metrics = tool.get_token_metrics(text, max_window_size=1000)
        self.assertIn("current_tokens", metrics)
        self.assertIn("utilization_ratio", metrics)
        self.assertTrue(0 <= metrics["utilization_ratio"] <= 1)

    def test_analyze_tool(self):
        tool = AnalyzeTools()
        text = "System is running. " * 50
        result = tool.analyze_context_health(text, step_number=1)
        self.assertIn("health_score", result)
        self.assertIn("status", result)
        self.assertIn("metrics", result)
        self.assertEqual(result["step_number"], 1)

if __name__ == "__main__":
    unittest.main()
