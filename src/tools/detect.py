
from typing import Any
from src.core.detector import ContextRotDetector

# Initialize the detector lazily or on server start
_detector = None

def get_detector():
    global _detector
    if _detector is None:
        _detector = ContextRotDetector()  # Loads the model (heavy)
    return _detector

def detect_context_rot(
    context_text: str, goal: str, chunk_size: int = 1000
) -> dict[str, Any]:
    """
    Perform deep analysis to detect context rot patterns.
    
    Splits context into chunks and analyzes:
    1. Relevance Decay: Are chunks drifting from the goal?
    2. Redundancy: Are chunks repeating information?
    3. Positional Risk: Is the context length causing "Lost-in-the-Middle"?
    """
    if not context_text:
        return {"error": "Empty context provided"}

    # Naive chunking for now (by characters, roughly)
    # Ideally should use tokenizer-based chunking
    chunks = [context_text[i:i+chunk_size] for i in range(0, len(context_text), chunk_size)]
    
    detector = get_detector()
    
    relevance_score = detector.compute_relevance_score(chunks, goal)
    redundancy_ratio, redundant_snippets = detector.check_redundancy(chunks)
    positional_risk = detector.analyze_positional_risk(len(context_text)/4, 128000) # approx tokens

    return {
        "rot_analysis": {
            "relevance_score": round(relevance_score, 2),
            "redundancy_ratio": round(redundancy_ratio, 2),
            "redundant_snippets_count": len(redundant_snippets),
            "positional_risk": positional_risk
        },
        "alerts": [] # TODO: Populate alerts based on thresholds
    }
