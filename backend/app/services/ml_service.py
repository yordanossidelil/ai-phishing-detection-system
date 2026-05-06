"""
ML Service — loads and caches the PhishingDetector model
"""
import sys
import os

# Add ai_model to path
AI_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ai_model")
sys.path.insert(0, AI_MODEL_PATH)

from app.core.config import get_settings

settings = get_settings()
_detector = None


def get_detector():
    global _detector
    if _detector is None:
        try:
            from train_model import PhishingDetector
            _detector = PhishingDetector(model_type=settings.model_type)
            print(f"Loaded {settings.model_type} model")
        except Exception as e:
            print(f"Model load failed: {e}. Training now...")
            from train_model import train, PhishingDetector
            train()
            _detector = PhishingDetector(model_type=settings.model_type)
    return _detector


def analyze_text(text: str) -> dict:
    detector = get_detector()
    return detector.predict(text)


def retrain_model(dataset_path: str = None, model_type: str = "logistic") -> dict:
    global _detector
    from train_model import train, PhishingDetector
    results = train(dataset_path)
    _detector = PhishingDetector(model_type=model_type)
    return results
