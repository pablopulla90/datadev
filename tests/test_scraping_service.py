from app.services.nlp_utils import clean_text, detect_language, sentiment


def test_clean_text():
    assert clean_text(" Hola   Mundo ") == "hola mundo"


def test_detect_language_spanish():
    assert detect_language("este es el texto de prueba y ejemplo") == "es"


def test_sentiment_positive():
    label, score, confidence = sentiment("excelente aprendizaje bueno")
    assert label == "positive"
    assert score > 0
    assert confidence >= 0.5
