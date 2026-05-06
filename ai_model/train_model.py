"""
ML Model Training: Naive Bayes + Logistic Regression with TF-IDF
"""
import os
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder

from preprocessor import preprocess_text, extract_risk_features

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def load_dataset(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.dropna(subset=["text", "label"])
    df["processed_text"] = df["text"].apply(preprocess_text)
    return df


def build_pipeline(model_type: str = "logistic") -> Pipeline:
    vectorizer = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=1,
    )
    if model_type == "naive_bayes":
        classifier = MultinomialNB(alpha=0.1)
    else:
        classifier = LogisticRegression(
            max_iter=1000,
            C=1.0,
            class_weight="balanced",
            random_state=42,
        )
    return Pipeline([("tfidf", vectorizer), ("clf", classifier)])


def train(dataset_path: str = None):
    if dataset_path is None:
        dataset_path = os.path.join(os.path.dirname(__file__), "data", "phishing_dataset.csv")

    print(f"Loading dataset from {dataset_path}...")
    df = load_dataset(dataset_path)
    print(f"Dataset size: {len(df)} samples")
    print(f"Label distribution:\n{df['label'].value_counts()}")

    # Map labels: phishing=2, suspicious=1, legitimate=0
    label_map = {"legitimate": 0, "suspicious": 1, "phishing": 2}
    df["label_encoded"] = df["label"].map(label_map).fillna(1).astype(int)

    X = df["processed_text"]
    y = df["label_encoded"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y if len(df) > 10 else None
    )

    results = {}
    for model_type in ["logistic", "naive_bayes"]:
        print(f"\nTraining {model_type}...")
        pipeline = build_pipeline(model_type)
        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        print(f"Accuracy ({model_type}): {acc:.4f}")
        if len(set(y_test)) > 1:
            labels_present = sorted(set(y_test))
            label_names = ["legitimate", "suspicious", "phishing"]
            names = [label_names[i] for i in labels_present]
            print(classification_report(y_test, y_pred, labels=labels_present, target_names=names, zero_division=0))

        model_path = os.path.join(MODEL_DIR, f"{model_type}_model.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(pipeline, f)
        print(f"Saved: {model_path}")
        results[model_type] = {"accuracy": acc, "path": model_path}

    # Save label map
    with open(os.path.join(MODEL_DIR, "label_map.pkl"), "wb") as f:
        pickle.dump(label_map, f)

    print("\nTraining complete!")
    return results


def load_model(model_type: str = "logistic"):
    model_path = os.path.join(MODEL_DIR, f"{model_type}_model.pkl")
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}, training now...")
        train()
    with open(model_path, "rb") as f:
        return pickle.load(f)


class PhishingDetector:
    LABEL_MAP = {0: "legitimate", 1: "suspicious", 2: "phishing"}

    def __init__(self, model_type: str = "logistic"):
        self.model = load_model(model_type)
        self.model_type = model_type

    def predict(self, text: str) -> dict:
        from preprocessor import extract_risk_features, build_explanation, detect_language

        processed = preprocess_text(text)
        features = extract_risk_features(text)
        lang = features["language"]

        proba = self.model.predict_proba([processed])[0]
        pred_idx = int(np.argmax(proba))
        confidence = float(proba[pred_idx])

        # Boost confidence based on URL risk
        if features["url_risk_score"] > 3 and pred_idx < 2:
            pred_idx = 2
            confidence = max(confidence, 0.85)

        prediction = self.LABEL_MAP[pred_idx]
        explanation = build_explanation(features, prediction, lang)

        return {
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "confidence_percent": round(confidence * 100, 1),
            "explanation": explanation,
            "language": lang,
            "features": {
                "urls_found": features["urls"],
                "url_risk_score": features["url_risk_score"],
                "risk_keywords": features["keyword_hits"],
                "caps_ratio": round(features["caps_ratio"], 3),
            },
            "probabilities": {
                "legitimate": round(float(proba[0]), 4),
                "suspicious": round(float(proba[1]), 4) if len(proba) > 2 else 0.0,
                "phishing": round(float(proba[2]), 4) if len(proba) > 2 else round(float(proba[1]), 4),
            }
        }


if __name__ == "__main__":
    train()
