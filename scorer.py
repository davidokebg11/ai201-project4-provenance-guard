def combine_scores(llm_score: float, stylo_score: float) -> dict:
    """
    Combines LLM and stylometric scores into a single confidence score.
    LLM is weighted 60%, stylometrics 40%.
    Returns a dict with combined score and attribution label.
    """

    # Weighted combination — LLM gets more weight (more semantically aware)
    confidence = round((llm_score * 0.60) + (stylo_score * 0.40), 4)

    # Determine attribution based on thresholds from planning.md
    if confidence >= 0.65:
        attribution = "likely_ai"
    elif confidence >= 0.40:
        attribution = "uncertain"
    else:
        attribution = "likely_human"

    return {
        "confidence": confidence,
        "attribution": attribution,
        "llm_score": round(llm_score, 4),
        "stylo_score": round(stylo_score, 4),
    }