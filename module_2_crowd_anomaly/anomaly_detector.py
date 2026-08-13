"""
anomaly_detector.py
AI Crowd Anomaly Detector — trains an Isolation Forest per zone on
baseline crowd sensor data, then scores new readings for anomalies
(sudden surges, bottlenecks) and assigns a Green/Yellow/Red risk level.
"""

import logging

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

from sensor_simulator import ZONES, generate_baseline_readings, generate_surge_event

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CrowdAnomaly")

FEATURES = ["people_count", "movement_speed_avg", "density_score"]


def risk_level(density_score: float, is_anomaly: bool) -> str:
    if is_anomaly or density_score >= 90:
        return "RED"
    if density_score >= 70:
        return "YELLOW"
    return "GREEN"


class CrowdAnomalyDetector:
    def __init__(self):
        self.models = {}  # one Isolation Forest per zone

    def train(self, baseline_df: pd.DataFrame):
        for zone in ZONES:
            zone_data = baseline_df[baseline_df["zone"] == zone][FEATURES]
            model = IsolationForest(
                n_estimators=150, contamination=0.03, random_state=42
            )
            model.fit(zone_data)
            self.models[zone] = model
        logger.info(f"Trained anomaly models for {len(self.models)} zones.")

    def save(self, path="anomaly_models.joblib"):
        joblib.dump(self.models, path)
        logger.info(f"Models saved -> {path}")

    def load(self, path="anomaly_models.joblib"):
        self.models = joblib.load(path)

    def score(self, reading: dict) -> dict:
        zone = reading["zone"]
        if zone not in self.models:
            raise ValueError(f"No trained model for zone '{zone}'")

        row = pd.DataFrame([reading])[FEATURES]
        model = self.models[zone]
        raw_pred = model.predict(row)[0]  # 1 = normal, -1 = anomaly
        is_anomaly = raw_pred == -1
        anomaly_score = float(-model.score_samples(row)[0])  # higher = more anomalous

        level = risk_level(reading["density_score"], is_anomaly)

        return {
            "zone": zone,
            "people_count": reading["people_count"],
            "density_score": reading["density_score"],
            "movement_speed_avg": reading["movement_speed_avg"],
            "is_anomaly": bool(is_anomaly),
            "anomaly_score": round(anomaly_score, 4),
            "risk_level": level,
        }

    def score_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        results = [self.score(row.to_dict()) for _, row in df.iterrows()]
        return pd.DataFrame(results)


if __name__ == "__main__":
    baseline = generate_baseline_readings()
    detector = CrowdAnomalyDetector()
    detector.train(baseline)
    detector.save()

    print("\n--- Normal reading (Mataf) ---")
    normal_reading = {"zone": "Mataf", "people_count": 3800, "movement_speed_avg": 0.9, "density_score": 76.0}
    print(detector.score(normal_reading))

    print("\n--- Surge event (Jamarat) ---")
    surge_df = generate_surge_event()
    results = detector.score_batch(surge_df)
    print(results[["zone", "people_count", "density_score", "risk_level", "is_anomaly"]])

    results.to_csv("anomaly_results.csv", index=False)
    print("\nSaved anomaly_results.csv")
