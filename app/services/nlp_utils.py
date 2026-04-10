import re
from collections import Counter

POSITIVE_WORDS = {"bueno", "excelente", "positivo", "feliz", "mejor", "aprendizaje"}
NEGATIVE_WORDS = {"malo", "terrible", "negativo", "triste", "peor", "error"}


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def detect_language(text: str) -> str:
    spanish_markers = [" el ", " la ", " de ", " y ", " que "]
    score = sum(1 for marker in spanish_markers if marker in f" {text} ")
    return "es" if score >= 2 else "unknown"


def sentiment(text: str) -> tuple[str, float, float]:
    tokens = re.findall(r"\w+", text)
    counts = Counter(tokens)
    pos = sum(counts[w] for w in POSITIVE_WORDS)
    neg = sum(counts[w] for w in NEGATIVE_WORDS)
    total = pos + neg
    if total == 0:
        return "neutral", 0.0, 0.5
    score = (pos - neg) / total
    label = "positive" if score > 0.15 else "negative" if score < -0.15 else "neutral"
    confidence = min(0.99, 0.5 + abs(score) / 2)
    return label, score, confidence


def topic_from_text(text: str) -> str:
    if "datos" in text or "analítica" in text:
        return "datos"
    if "educ" in text:
        return "educación"
    return "general"
