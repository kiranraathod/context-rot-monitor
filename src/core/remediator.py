
from typing import List, Dict, Any, Tuple
import google.genai as genai
import os
import logging

logger = logging.getLogger(__name__)

class ContextRemediator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("No GOOGLE_API_KEY provided. Summarization will be disabled.")

    def recommend_pruning(
        self, 
        context_chunks: List[str], 
        relevance_scores: List[float], 
        redundancy_flags: List[bool],
        relevance_threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Identify chunks that should be pruned based on low relevance or redundancy.
        Returns a list of recommendations: {index, reason, snippet}
        """
        recommendations = []
        
        # Check relevance
        for i, score in enumerate(relevance_scores):
            if score < relevance_threshold:
                recommendations.append({
                    "chunk_index": i,
                    "reason": "LOW_RELEVANCE",
                    "score": score,
                    "snippet": context_chunks[i][:50] + "..."
                })
        
        # Check redundancy
        for i, is_redundant in enumerate(redundancy_flags):
            if is_redundant:
                # Avoid double listing if already flagged for relevance
                if not any(r["chunk_index"] == i for r in recommendations):
                    recommendations.append({
                        "chunk_index": i,
                        "reason": "REDUNDANT",
                        "score": 0.0, # Implies 0 value add
                        "snippet": context_chunks[i][:50] + "..."
                    })
                    
        return recommendations

    def summarize_context(self, context_text: str, target_length_words: int = 200) -> str:
        """
        Use Gemini to summarize the context.
        """
        if not self.client:
            return "Error: GOOGLE_API_KEY not configured."
        
        prompt = f"""
        Summarize the following context, preserving key facts, decisions, and outcomes.
        Target length: ~{target_length_words} words.
        
        Context:
        {context_text}
        """
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return f"Error during summarization: {str(e)}"
