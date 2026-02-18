
import unittest
from unittest.mock import MagicMock, patch
from src.core.detector import ContextRotDetector
from src.resources.alerts import add_alert, get_active_alerts, clear_alerts
import json

class TestPhase2(unittest.TestCase):
    def setUp(self):
        clear_alerts()

    @patch('src.core.detector.SentenceTransformer')
    def test_detector_relevance(self, mock_transformer):
        # Mock the embedding model so we don't need to load the real one (slow/heavy)
        mock_model = MagicMock()
        # Mock encode to return dummy embeddings
        # 2 chunks, 1 goal. Embeddings size 3.
        mock_model.encode.side_effect = lambda x: [[1.0, 0.0, 0.0]] if isinstance(x, str) else [[0.9, 0.1, 0.0], [0.1, 0.9, 0.0]]
        mock_model.get_sentence_embedding_dimension.return_value = 3
        mock_transformer.return_value = mock_model

        detector = ContextRotDetector()
        score = detector.compute_relevance_score(["chunk1", "chunk2"], "goal")
        
        # With our mock, chunk1 is close to goal (0.9), chunk2 is far (0.1). Avg ~0.5
        # The exact value depends on cosine similarity implementation details, 
        # but we expect a float 0-1
        self.assertTrue(0.0 <= score <= 1.0)

    def test_alerts_resource(self):
        add_alert("TEST_ALERT", "Test message", "WARNING")
        alerts_json = get_active_alerts()
        data = json.loads(alerts_json)
        self.assertIn("active_alerts", data)
        self.assertEqual(len(data["active_alerts"]), 1)
        self.assertEqual(data["active_alerts"][0]["type"], "TEST_ALERT")

    @patch('src.core.detector.SentenceTransformer')
    def test_detector_redundancy(self, mock_transformer):
        mock_model = MagicMock()
        # Identical embeddings for redundancy
        mock_model.encode.return_value = [[1.0, 0.0, 0.0], [1.0, 0.0, 0.0]] 
        mock_transformer.return_value = mock_model

        detector = ContextRotDetector()
        ratio, snippets = detector.check_redundancy(["A", "A"])
        
        # Should be 50% redundant (1 out of 2 is redundant)
        self.assertEqual(ratio, 0.5)
        self.assertEqual(len(snippets), 1)

if __name__ == "__main__":
    unittest.main()
