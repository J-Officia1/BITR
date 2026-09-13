"""
Core analysis engine for the BITR manipulation detector.
Utilizes VADER sentiment analysis, rule-based keyword matching, 
and formatting heuristics to compute credibility and risk scores.
"""

import re
from langdetect import detect
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

try:
    from .keywords import (
        FEAR_TRIGGERS,
        AUTHORITY_IMPERSONATION,
        SCARCITY_URGENCY,
        SOCIAL_PROOF,
        EMOTIONAL_AMPLIFICATION,
        SOURCE_INDICATORS,
        SUSPICIOUS_URL_PATTERNS,
    )
except ImportError:
    from keywords import (
        FEAR_TRIGGERS,
        AUTHORITY_IMPERSONATION,
        SCARCITY_URGENCY,
        SOCIAL_PROOF,
        EMOTIONAL_AMPLIFICATION,
        SOURCE_INDICATORS,
        SUSPICIOUS_URL_PATTERNS,
    )


def check_keywords(text: str, keyword_list: list[str]) -> tuple[float, list[str]]:
    """
    Evaluates keyword match density and count within input text using word boundary regex.
    Returns a score scaled (0-10) and a list of matched keywords.
    """
    text_lower = text.lower()
    words = text_lower.split()
    total_words = len(words)

    if total_words == 0:
        return 0.0, []

    matched_keywords = []
    weighted_match_count = 0

    for keyword in keyword_list:
        lower_keyword = keyword.lower()
        pattern = rf"\b{re.escape(lower_keyword)}\b"

        if re.search(pattern, text_lower):
            matched_keywords.append(keyword)
            # Give higher weight to multi-word phrases
            weighted_match_count += 2 if ' ' in keyword else 1

    density_score = (weighted_match_count / total_words) * 100
    absolute_score = weighted_match_count * 2.5
    
    score = min(max(density_score, absolute_score), 10.0)
    return score, matched_keywords


def get_sentiment_score(text: str) -> float:
    """
    Computes absolute sentiment intensity using VADER, scaled from 0 to 10.
    High absolute polarity (extreme positive or extreme negative) indicates potential manipulation.
    """
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    compound = abs(scores['compound'])
    return round(compound * 10, 2)


def get_credibility_penalty(text: str) -> float:
    """
    Calculates credibility penalty based on formatting triggers:
    - Excessive uppercase words (>15%)
    - Excessive exclamation marks (>3)
    - Suspicious short URL patterns
    - Lack of source attribution
    """
    penalty = 0.0
    words = text.split()

    if words:
        caps_count = sum(1 for word in words if word.isupper())
        if caps_count / len(words) > 0.15:
            penalty += 3.0

    if text.count('!') > 3:
        penalty += 2.0

    lower_text = text.lower()
    if any(pattern in lower_text for pattern in SUSPICIOUS_URL_PATTERNS):
        penalty += 3.0

    source_phrases = ['according to', 'reported by', 'source', 'cited by']
    if not any(phrase in lower_text for phrase in source_phrases):
        penalty += 2.0

    return min(penalty, 10.0)


def analyze_text(text: str) -> dict:
    """
    Main analysis pipeline. Evaluates language support, tactic match scores,
    sentiment intensity, and formatting penalties to derive the final hybrid score.
    """
    try:
        language_detected = detect(text)
    except Exception:
        language_detected = "en"

    if language_detected != 'en':
        return {
            "error": "Language not supported. Currently English only.",
            "manipulation_score": None,
            "authenticity_score": None,
            "risk_level": None,
            "risk_color": None,
            "guidance": None,
            "category_scores": None,
            "detected_tactics": None,
            "language_detected": language_detected,
            "ml_score": None,
            "hybrid_score": None,
        }

    # Handle very short texts with low risk unless explicit signals are detected
    if len(text.strip().split()) < 3:
        temp_fear, _ = check_keywords(text, FEAR_TRIGGERS)
        temp_urgency, _ = check_keywords(text, SCARCITY_URGENCY)
        temp_cred = get_credibility_penalty(text)

        if temp_fear == 0 and temp_urgency == 0 and temp_cred == 0:
            return {
                "manipulation_score": 0,
                "authenticity_score": 100,
                "risk_level": "Low Risk",
                "risk_color": "green",
                "guidance": "The input text is too short to analyze.",
                "category_scores": {
                    "Fear Triggers": 0,
                    "Authority Impersonation": 0,
                    "Scarcity / Urgency": 0,
                    "Social Proof Manipulation": 0,
                    "Emotional Amplification": 0,
                    "Sentiment Intensity": 0.0,
                    "Credibility Penalty": 0,
                },
                "detected_tactics": {
                    'Fear Triggers': [],
                    'Authority Impersonation': [],
                    'Scarcity / Urgency': [],
                    'Social Proof Manipulation': [],
                    'Emotional Amplification': [],
                },
                "language_detected": language_detected,
                "ml_score": None,
                "hybrid_score": 0,
            }

    fear_score, fear_words = check_keywords(text, FEAR_TRIGGERS)
    authority_score, authority_words = check_keywords(text, AUTHORITY_IMPERSONATION)
    scarcity_score, scarcity_words = check_keywords(text, SCARCITY_URGENCY)
    social_score, social_words = check_keywords(text, SOCIAL_PROOF)
    emotional_score, emotional_words = check_keywords(text, EMOTIONAL_AMPLIFICATION)

    sentiment_score = get_sentiment_score(text)
    credibility_penalty = get_credibility_penalty(text)

    # Weighted score aggregation
    formula_result = (
        (fear_score * 0.26) +
        (authority_score * 0.22) +
        (scarcity_score * 0.18) +
        (social_score * 0.10) +
        (emotional_score * 0.08) +
        (sentiment_score * 0.10) +
        (credibility_penalty * 0.06)
    )

    scaled_score = round(formula_result * 10, 2)
    manipulation_score = min(scaled_score, 100)

    # Multi-tactic amplification penalty
    tactics_scores = [fear_score, authority_score, scarcity_score, social_score, emotional_score]
    active_signals = sum(1 for score in tactics_scores if score > 0)
    if active_signals >= 4:
        manipulation_score = min(manipulation_score + 30, 100)
    elif active_signals == 3:
        manipulation_score = min(manipulation_score + 15, 100)

    authenticity_score = 100 - manipulation_score

    if manipulation_score <= 30:
        risk_level = "Low Risk"
        risk_color = "green"
        guidance = "The text appears authentic with minimal signs of manipulation."
    elif manipulation_score <= 60:
        risk_level = "Moderate Risk"
        risk_color = "orange"
        guidance = "Some manipulative patterns detected. Exercise caution and verify the source."
    else:
        risk_level = "High Risk"
        risk_color = "red"
        guidance = "High likelihood of manipulation or fake news. Do not trust without strong verification."

    category_scores = {
        "Fear Triggers": fear_score,
        "Authority Impersonation": authority_score,
        "Scarcity / Urgency": scarcity_score,
        "Social Proof Manipulation": social_score,
        "Emotional Amplification": emotional_score,
        "Sentiment Intensity": sentiment_score,
        "Credibility Penalty": credibility_penalty,
    }

    detected_tactics = {
        'Fear Triggers': fear_words,
        'Authority Impersonation': authority_words,
        'Scarcity / Urgency': scarcity_words,
        'Social Proof Manipulation': social_words,
        'Emotional Amplification': emotional_words,
    }

    return {
        "manipulation_score": manipulation_score,
        "authenticity_score": authenticity_score,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "guidance": guidance,
        "category_scores": category_scores,
        "detected_tactics": detected_tactics,
        "language_detected": language_detected,
        "ml_score": None,
        "hybrid_score": manipulation_score,
    }
