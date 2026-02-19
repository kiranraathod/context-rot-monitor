
import unittest
from unittest.mock import MagicMock, patch
from src.core.remediator import ContextRemediator
from src.storage.metrics_store import MetricsStore
import os

class TestPhase3(unittest.TestCase):
    def setUp(self):
        # Use a temp file for testing so connection closing doesn't wipe data
        import tempfile
        self.db_file = tempfile.NamedTemporaryFile(delete=False)
        self.db_path = self.db_file.name
        self.db_file.close() # Close handle immediately to avoid Windows locking
        self.store = MetricsStore(db_path=self.db_path)

    def tearDown(self):
        import os
        try:
            os.unlink(self.db_path)
        except PermissionError:
            pass

    def test_metrics_store(self):
        data = {
            "health_score": 85.5,
            "status": "HEALTHY",
            "metrics": {
                "token_count": 1000,
                "utilization_ratio": 0.1
            },
            "step_number": 1,
            "model": "test-model"
        }
        self.store.add_record(data)
        history = self.store.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["score"], 85.5)

    @patch('src.core.remediator.genai')
    def test_summarize_context(self, mock_genai):
        # Mock Gemini client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Summary"
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client
        
        remediator = ContextRemediator(api_key="test-key")
        summary = remediator.summarize_context("Long text", 100)
        
        self.assertEqual(summary, "Summary")
        mock_client.models.generate_content.assert_called_once()

    def test_pruning_recommendation(self):
        remediator = ContextRemediator(api_key="test-key")
        chunks = ["Relevant", "Irrelevant garbage", "Relevant"]
        scores = [0.9, 0.1, 0.8] # Middle one is low relevance
        redundancy = [False, False, False]
        
        recs = remediator.recommend_pruning(chunks, scores, redundancy, relevance_threshold=0.3)
        
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["chunk_index"], 1)
        self.assertEqual(recs[0]["reason"], "LOW_RELEVANCE")

if __name__ == "__main__":
    unittest.main()
