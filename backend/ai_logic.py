# backend/ai_logic.py
from typing import Dict, Tuple
import re

_ZS_MODEL_ID = "facebook/bart-large-mnli"  # robust, well-known for zero-shot NLI

def _lazy_load_pipeline():
    # Lazy-import to speed server start when unused
    from transformers import pipeline
    return pipeline("zero-shot-classification", model=_ZS_MODEL_ID)

def _basic_rule_scores(text: str) -> Dict[str, float]:
    t = text.lower()
    return {
        "ads": 1.0 if re.search(r"\b(advertis|ads|targeted|marketing)\b", t) else 0.0,
        "analytics": 1.0 if re.search(r"\banalytics|measure|metrics|performance\b", t) else 0.0,
        "functional": 1.0 if re.search(r"\bfunctional|preferences|remember\b", t) else 0.0,
        "essential": 1.0 if re.search(r"\bstrictly necessary|essential|required\b", t) else 0.0,
        "personalization": 1.0 if re.search(r"\bpersonaliz|customiz|recommendation\b", t) else 0.0,
    }

def classify_banner(text: str) -> Dict[str, float]:
    """
    Returns normalized confidence for each purpose label using zero-shot;
    falls back to simple rules if model unavailable.
    """
    candidate_labels = ["ads", "analytics", "functional", "essential", "personalization"]
    try:
        pipe = _lazy_load_pipeline()
        res = pipe(
            text,
            candidate_labels=candidate_labels,
            multi_label=True
        )
        # Map scores to labels
        scores = {lbl: float(score) for lbl, score in zip(res["labels"], res["scores"])}
        # Reorder into our canonical label order
        return {lbl: float(scores.get(lbl, 0.0)) for lbl in candidate_labels}
    except Exception:
        # Fallback rule-based
        return _basic_rule_scores(text)

def negotiate_consent(banner_text: str, prefs: Dict[str, bool] | None) -> Tuple[str, Dict[str, bool], Dict[str, float]]:
    """
    Decide consent outcome given banner content and (optional) user preferences.
    Strategy:
      - classify text into purposes with confidences
      - default policy: deny high-risk categories unless user explicitly allows
      - allow essential always
    """
    scores = classify_banner(banner_text)
    # Default preferences if none provided (privacy-friendly)
    effective = {
        "essential": True,
        "analytics": False,
        "ads": False,
        "functional": True,
        "personalization": False
    }
    if prefs:
        effective.update(prefs)

    # Apply a threshold: if model is >0.5 confident a purpose is present,
    # then enforce the user's preference for that purpose.
    threshold = 0.5
    decision_map = {
        "essential": True,  # always allow essential
        "analytics": effective["analytics"] if scores["analytics"] > threshold else False,
        "ads":        effective["ads"]        if scores["ads"] > threshold else False,
        "functional": effective["functional"] if scores["functional"] > threshold else True,
        "personalization": effective["personalization"] if scores["personalization"] > threshold else False
    }

    # Summary decision:
    unique_vals = set(decision_map.values())
    if unique_vals == {True}:
        decision = "Accept All"
    elif unique_vals == {False} or (decision_map["essential"] is False):
        decision = "Reject All"
    else:
        decision = "Custom"

    return decision, decision_map, scores
