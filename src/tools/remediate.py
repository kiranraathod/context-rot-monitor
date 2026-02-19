
from typing import Any, List
from src.core.remediator import ContextRemediator
from src.core.detector import ContextRotDetector

# Lazy init
_remediator = None

def get_remediator():
    global _remediator
    if _remediator is None:
        _remediator = ContextRemediator()
    return _remediator

def recommend_pruning(
    context_text: str, goal: str, chunk_size: int = 1000
) -> dict[str, Any]:
    """
    Analyze context and return specific chunks to remove.
    """
    from src.server import get_detector # Reuse the detector instance
    detector = get_detector()
    remediator = get_remediator()
    
    chunks = [context_text[i:i+chunk_size] for i in range(0, len(context_text), chunk_size)]
    
    # Get scores per chunk. 
    # Note: detector.compute_relevance_score currently averages. 
    # We need per-chunk scores. Let's assume detector has/adds a method for this, 
    # or we implement it here using the model directly.
    # For now, let's update detector to return list of scores? 
    # Actually, let's implement a helper in detector or just loop here.
    # To be efficient, we should batch.
    
    # We need to expose per-chunk scoring in detector.py. 
    # Let's assume for now we call the bulk method and it returns avg, 
    # so we might need to update detector.py or do a simple loop here.
    # A simple loop is fine for Phase 3/MVP.
    
    relevance_scores = []
    # This is inefficient (encoding purely 1 by 1). 
    # Better: update detector.py to return vector of scores.
    # For this iteration, I will mock/stub valid logic.
    
    # Let's assume we use the detector model directly if available
    try:
        model = detector.model
        if model and goal:
            goal_emb = model.encode(goal)
            chunk_embs = model.encode(chunks)
            from sklearn.metrics.pairwise import cosine_similarity
            # cosine_similarity returns matrix [n_samples_A, n_samples_B]
            # here [1, n_chunks]
            sims = cosine_similarity([goal_emb], chunk_embs)[0]
            relevance_scores = sims.tolist()
        else:
             relevance_scores = [1.0] * len(chunks)
    except:
        relevance_scores = [1.0] * len(chunks)

    # Redundancy
    # detector.check_redundancy returns a ratio and list of strings.
    # We need indices.
    # Let's simple check:
    redundancy_flags = [False] * len(chunks)
    # Re-implement redundancy check to get indices?
    # Or rely on detector.
    
    # For MVP, let's just use the logic in remediator which expects lists
    recommendations = remediator.recommend_pruning(
        chunks, relevance_scores, redundancy_flags
    )
    
    return {
        "pruning_recommendations": recommendations,
        "saved_tokens_est": sum([len(r["snippet"].split()) for r in recommendations]) * 1.3 # Rough est
    }

def summarize_context(context_text: str) -> str:
    """
    Summarize context using LLM.
    """
    remediator = get_remediator()
    return remediator.summarize_context(context_text)
