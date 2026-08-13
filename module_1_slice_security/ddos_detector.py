"""
ddos_detector.py
5G Network Slice Security Monitor.

Trains a Random Forest classifier on synthetic 5G slice traffic
(normal vs DDoS) and exposes a monitor() method that scores live
traffic windows and triggers an alert + isolation workflow when an
attack is detected.

Run standalone: python ddos_detector.py
(expects training_data.csv in the same folder — generate it first
with generate_training_data.py)
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from slice_isolator import SliceIsolator

FEATURES = ["packet_rate", "bandwidth_mbps", "unique_ips", "syn_ratio", "avg_packet_size"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("SliceSecurity")


class SliceSecurityMonitor:
    def __init__(self, slice_name="Hajj-Emergency-Slice", model_path="ddos_model.joblib"):
        self.slice_name = slice_name
        self.model_path = Path(model_path)
        self.model = RandomForestClassifier(
            n_estimators=200, max_depth=8, random_state=42, class_weight="balanced"
        )
        self.threat_log = []
        self.isolator = SliceIsolator(slice_name)
        self.is_trained = False

    # ------------------------------------------------------------------ #
    # Training
    # ------------------------------------------------------------------ #
    def train_model(self, csv_path="training_data.csv"):
        data = pd.read_csv(csv_path)
        X = data[FEATURES]
        y = data["label"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        self.model.fit(X_train, y_train)
        self.is_trained = True

        preds = self.model.predict(X_test)
        logger.info("Model trained. Holdout evaluation:")
        print(classification_report(y_test, preds, target_names=["normal", "ddos"]))
        print("Confusion matrix:\n", confusion_matrix(y_test, preds))

        joblib.dump(self.model, self.model_path)
        logger.info(f"Model saved -> {self.model_path}")

    def load_model(self):
        self.model = joblib.load(self.model_path)
        self.is_trained = True

    # ------------------------------------------------------------------ #
    # Live monitoring
    # ------------------------------------------------------------------ #
    def monitor_traffic(self, live_reading: dict) -> dict:
        """
        live_reading: dict with keys matching FEATURES, e.g.
            {"packet_rate": 18000, "bandwidth_mbps": 510,
             "unique_ips": 90, "syn_ratio": 0.81, "avg_packet_size": 88}
        Returns a result dict with the verdict and confidence.
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained/loaded. Call train_model() or load_model() first.")

        row = pd.DataFrame([live_reading])[FEATURES]
        proba = self.model.predict_proba(row)[0]
        prediction = int(self.model.predict(row)[0])
        confidence = float(proba[prediction])

        result = {
            "slice": self.slice_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prediction": "ddos" if prediction == 1 else "normal",
            "confidence": round(confidence, 4),
            "reading": live_reading,
        }

        if prediction == 1:
            self.trigger_alert(result)
            self.isolator.isolate()
            result["action"] = "SLICE_ISOLATED"
        else:
            result["action"] = "NONE"

        return result

    def trigger_alert(self, result: dict):
        alert = {
            "severity": "CRITICAL",
            "message": f"DDoS attack detected on {self.slice_name}",
            **result,
        }
        self.threat_log.append(alert)
        logger.warning(f"⚠️  {alert['message']} (confidence={result['confidence']})")
        # In production this would call an SMTP/SMS/webhook alert channel.

    def export_threat_log(self, path="threat_log.json"):
        with open(path, "w") as f:
            json.dump(self.threat_log, f, indent=2)
        logger.info(f"Threat log exported -> {path} ({len(self.threat_log)} entries)")


if __name__ == "__main__":
    monitor = SliceSecurityMonitor()
    monitor.train_model("training_data.csv")

    # Simulate a normal reading
    normal_reading = {
        "packet_rate": 1150, "bandwidth_mbps": 78, "unique_ips": 310,
        "syn_ratio": 0.12, "avg_packet_size": 520,
    }
    print("\n--- Normal traffic test ---")
    print(monitor.monitor_traffic(normal_reading))

    # Simulate a DDoS reading
    ddos_reading = {
        "packet_rate": 17800, "bandwidth_mbps": 495, "unique_ips": 95,
        "syn_ratio": 0.88, "avg_packet_size": 82,
    }
    print("\n--- DDoS traffic test ---")
    print(monitor.monitor_traffic(ddos_reading))

    monitor.export_threat_log()
