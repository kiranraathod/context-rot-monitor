
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class ContextRotDetector:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the detector with an embedding model.
        This model is small (80MB) and fast, suitable for real-time analysis.
        """
        try:
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
        except Exception as e:
            logger.error(f"Failed to load embedding model {model_name}: {e}")
            self.model = None

    def compute_relevance_score(self, context_chunks: List[str], goal: str) -> float:
        """
        Compute the average cosine similarity between context chunks and the goal.
        Returns a score between 0.0 (irrelevant) and 1.0 (highly relevant).
        """
        if not self.model or not context_chunks or not goal:
            return 1.0  # Default to perfect relevance if model missing or empty input

        try:
            goal_embedding = self.model.encode(goal).reshape(1, -1)
            chunk_embeddings = self.model.encode(context_chunks)
            
            # Compute similarities
            similarities = cosine_similarity(goal_embedding, chunk_embeddings)[0]
            
            # Weighted average? For now, simple average.
            # In Phase 3 we might weight recent chunks higher.
            avg_similarity = float(np.mean(similarities))
            
            # Clamp to 0-1 range (cosine sim can be negative)
            return max(0.0, min(1.0, avg_similarity))
            
        except Exception as e:
            logger.error(f"Error computing relevance: {e}")
            return 1.0

    def check_redundancy(self, context_chunks: List[str], threshold: float = 0.85) -> Tuple[float, List[str]]:
        """
        Detect redundant chunks using embedding similarity.
        Returns:
            - redundancy_ratio (0.0 to 1.0): Fraction of chunks that are redundant.
            - redundant_snippets: List of text snippets identified as redundant.
        """
        if not self.model or len(context_chunks) < 2:
            return 0.0, []

        try:
            embeddings = self.model.encode(context_chunks)
            sim_matrix = cosine_similarity(embeddings)
            
            # Mask diagonal (self-similarity) and upper triangle to avoid double counting
            np.fill_diagonal(sim_matrix, 0)
            
            redundant_indices = set()
            redundant_snippets = []
            
            # Check for high similarity pairs
            # We iterate through the lower triangle
            rows, cols = np.where(np.tril(sim_matrix, k=-1) > threshold)
            
            for r, c in zip(rows, cols):
                # If chunk r is similar to chunk c (where c < r), mark r as redundant
                if r not in redundant_indices:
                    redundant_indices.add(r)
                    redundant_snippets.append(context_chunks[r][:100] + "...")

            redundancy_ratio = len(redundant_indices) / len(context_chunks)
            return redundancy_ratio, redundant_snippets
            
        except Exception as e:
            logger.error(f"Error checking redundancy: {e}")
            return 0.0, []

    def analyze_positional_risk(self, total_tokens: int, max_window: int) -> str:
        """
        Identify if context is approaching dangerous "Lost-in-the-Middle" territory.
        """
        utilization = total_tokens / max_window if max_window > 0 else 0
        if utilization < 0.3:
            return "LOW"
        elif utilization < 0.7:
            return "MODERATE (Middle Risk)"
        else:
            return "HIGH (Middle content likely lost)"
