import re
import math

def compute_stylometrics(text: str) -> float:
    """
    Computes stylometric heuristics to detect AI-generated text.
    Returns a float between 0 (human-like) and 1 (AI-like).
    """

    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    words = re.findall(r'\b\w+\b', text.lower())

    if len(sentences) < 2 or len(words) < 10:
        return 0.5  # not enough data

    # --- Metric 1: Sentence length variance ---
    # AI text tends to have uniform sentence lengths (low variance)
    lengths = [len(re.findall(r'\b\w+\b', s)) for s in sentences]
    mean_len = sum(lengths) / len(lengths)
    variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
    std_dev = math.sqrt(variance)

    # Normalize: low std_dev = AI-like (score near 1), high = human-like (score near 0)
    # Typical human std_dev is 5–15, AI is often 2–6
    sentence_variance_score = max(0.0, min(1.0, 1.0 - (std_dev / 15.0)))

    # --- Metric 2: Type-Token Ratio (vocabulary diversity) ---
    # AI text reuses words more; humans use more varied vocabulary
    unique_words = set(words)
    ttr = len(unique_words) / len(words)

    # Low TTR = AI-like (score near 1), high TTR = human-like (score near 0)
    # TTR typically ranges 0.4–0.9; AI tends toward lower end
    ttr_score = max(0.0, min(1.0, 1.0 - ((ttr - 0.3) / 0.6)))

    # --- Metric 3: Punctuation density ---
    # AI text tends to use punctuation more consistently/sparingly
    punctuation_count = len(re.findall(r'[,;:\-\(\)\"\']', text))
    punct_density = punctuation_count / len(words)

    # Very low or very high punctuation density can indicate AI
    # Human writing typically has density 0.05–0.20
    if punct_density < 0.03 or punct_density > 0.25:
        punct_score = 0.7  # unusual = slightly AI-like
    else:
        punct_score = 0.3  # normal range = human-like

    # --- Combine the three metrics ---
    stylo_score = (
        sentence_variance_score * 0.45 +
        ttr_score * 0.40 +
        punct_score * 0.15
    )

    return round(max(0.0, min(1.0, stylo_score)), 4)