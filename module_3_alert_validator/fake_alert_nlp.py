"""
fake_alert_nlp.py
Lightweight NLP classifier that flags suspicious language patterns in
emergency messages (e.g., panic-inducing, unverifiable, sensational
phrasing) as a second line of defense alongside HMAC signature
verification. Uses TF-IDF + Logistic Regression on a small labelled
seed set — enough to demo the concept end-to-end.
"""

import logging

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("FakeAlertNLP")

# Seed training set: 1 = suspicious / likely fake, 0 = legitimate control-room style
TRAIN_MESSAGES = [
    # Legitimate (0)
    ("Please use alternate route to Jamarat. Gate 4 congested.", 0),
    ("Mataf area at capacity, security directing pilgrims to Masa'a entrance 3.", 0),
    ("Water stations refilled at King Fahd Gate, please proceed calmly.", 0),
    ("Prayer time adjustment: Isha delayed by 10 minutes for crowd flow.", 0),
    ("Medical tent relocated near Gate 2 for faster access.", 0),
    ("Shuttle bus route B temporarily rerouted due to maintenance.", 0),
    ("Temperature advisory: stay hydrated, shaded rest areas available at all zones.", 0),
    ("Crowd control update: Jamarat flow normalized, proceed as scheduled.", 0),
    ("Lost and found desk relocated to King Fahd Gate information center.", 0),
    ("Scheduled network maintenance tonight 2-3 AM, emergency lines unaffected.", 0),
    # Suspicious / fake (1)
    ("BREAKING: Bridge collapsed at Jamarat! Evacuate now!!!", 1),
    ("URGENT!!! Stampede happening RIGHT NOW run immediately!!!", 1),
    ("Terrorist attack confirmed near Mataf, authorities hiding the truth!", 1),
    ("Share this NOW everyone is going to die if you don't leave!!!", 1),
    ("Secret government cover-up: gas leak at Masa'a, do not trust officials", 1),
    ("EMERGENCY EMERGENCY building on fire everyone panic and run", 1),
    ("Fake news alert but believe me thousands trampled already", 1),
    ("They are not telling you the real death count, get out now", 1),
    ("Explosion reported!!! forward to all your family immediately", 1),
    ("Unconfirmed rumor: mass casualty event, spread the word fast", 1),
]


class FakeAlertDetector:
    def __init__(self):
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, stop_words="english")),
            ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ])
        self.is_trained = False

    def train(self, messages=None):
        messages = messages or TRAIN_MESSAGES
        X = [m for m, _ in messages]
        y = [label for _, label in messages]
        self.pipeline.fit(X, y)
        self.is_trained = True
        logger.info(f"Fake-alert NLP model trained on {len(messages)} seed examples.")

    def predict(self, text: str) -> dict:
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")
        proba = self.pipeline.predict_proba([text])[0]
        pred = int(self.pipeline.predict([text])[0])
        return {
            "text": text,
            "suspicious": bool(pred == 1),
            "confidence": round(float(proba[pred]), 4),
        }

    def save(self, path="fake_alert_model.joblib"):
        joblib.dump(self.pipeline, path)

    def load(self, path="fake_alert_model.joblib"):
        self.pipeline = joblib.load(path)
        self.is_trained = True


if __name__ == "__main__":
    detector = FakeAlertDetector()
    detector.train()
    detector.save()

    test_messages = [
        "Please use alternate route to Jamarat. Gate 4 congested.",
        "BREAKING: Bridge collapsed at Jamarat! Evacuate now!!!",
        "Water distribution point added near Masa'a entrance 2.",
        "URGENT share now stampede confirmed thousands trapped",
    ]

    for msg in test_messages:
        result = detector.predict(msg)
        tag = "🚫 SUSPICIOUS" if result["suspicious"] else "✅ Looks legitimate"
        print(f"{tag} ({result['confidence']}): {msg}")
