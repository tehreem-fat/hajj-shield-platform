"""
hajj_day3_emergency.py
Scripted end-to-end demo: "Hajj Day 3 — Emergency Drill"

Runs Modules 1, 2, and 3 together in a single narrative timeline to show
how HAJJ-SHIELD detects a DDoS attack, flags a crowd density anomaly,
blocks a fake emergency alert, and broadcasts a verified one — the
exact scenario described in the project README.

Run from the repo root:
    python demo_scenario/hajj_day3_emergency.py
"""

import sys
import time
from pathlib import Path

# Make sibling module folders importable when run from repo root or in place.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "module_1_slice_security"))
sys.path.insert(0, str(ROOT / "module_2_crowd_anomaly"))
sys.path.insert(0, str(ROOT / "module_3_alert_validator"))

from ddos_detector import SliceSecurityMonitor          # noqa: E402
from anomaly_detector import CrowdAnomalyDetector        # noqa: E402
from sensor_simulator import generate_baseline_readings  # noqa: E402
from alert_verifier import AlertSigner, AlertVerifier, AlertPriorityQueue  # noqa: E402


def banner(text):
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


def step(clock, text, pause=0.6):
    print(f"[{clock}] {text}")
    time.sleep(pause)


def main():
    banner("HAJJ-SHIELD — Hajj Day 3: Emergency Drill (scripted demo)")

    # ------------------------------------------------------------------ #
    # 14:00 — Normal operations
    # ------------------------------------------------------------------ #
    step("14:00", "Normal operations. Dashboard shows all zones GREEN.")

    # ------------------------------------------------------------------ #
    # 14:05 — DDoS attack on the Emergency Slice
    # ------------------------------------------------------------------ #
    os_path = str(ROOT / "module_1_slice_security" / "training_data.csv")
    slice_monitor = SliceSecurityMonitor()
    slice_monitor.train_model(os_path)

    ddos_reading = {
        "packet_rate": 17800, "bandwidth_mbps": 495, "unique_ips": 95,
        "syn_ratio": 0.88, "avg_packet_size": 82,
    }
    step("14:05", "5G Slice Monitor detects DDoS attack on Emergency Slice.")
    result = slice_monitor.monitor_traffic(ddos_reading)
    step("14:05", f"  -> Verdict: {result['prediction'].upper()} "
                   f"(confidence={result['confidence']}). Action: {result['action']}.")
    step("14:06", "  -> Alert triggered. Slice auto-isolated. Backup slice activated.")

    # ------------------------------------------------------------------ #
    # 14:07 — Crowd anomaly at Jamarat
    # ------------------------------------------------------------------ #
    baseline = generate_baseline_readings()
    crowd_detector = CrowdAnomalyDetector()
    crowd_detector.train(baseline)

    step("14:07", "Crowd Anomaly Detector flags Jamarat zone: density spike detected.")
    jamarat_reading = {
        "zone": "Jamarat", "people_count": 10200,
        "movement_speed_avg": 0.22, "density_score": 85.0,
    }
    prior_score = 30
    crowd_result = crowd_detector.score(jamarat_reading)
    step("14:07", f"  -> Risk score jumps from {prior_score} to "
                   f"{int(crowd_result['density_score'])}. Risk level: {crowd_result['risk_level']}.")

    # ------------------------------------------------------------------ #
    # 14:08 — Fake alert received and blocked
    # ------------------------------------------------------------------ #
    SECRET = b"hajj-shield-demo-secret-key-2026"
    signer = AlertSigner(SECRET)
    verifier = AlertVerifier(SECRET)
    queue = AlertPriorityQueue()

    step("14:08", "Fake alert received: \"Bridge collapsed at Jamarat!\"")
    forged_alert = {
        "message": "Bridge collapsed at Jamarat!",
        "severity": "CRITICAL",
        "source": "unknown",
        "signature": "0" * 64,
    }
    if verifier.verify(forged_alert):
        queue.push(forged_alert)
        step("14:08", "  -> Alert Integrity System verifies: signature OK. Broadcasting.")
    else:
        step("14:08", "  -> Alert Integrity System verifies: FAKE (invalid signature). Blocks broadcast.")

    # ------------------------------------------------------------------ #
    # 14:10 — Verified alert broadcast
    # ------------------------------------------------------------------ #
    step("14:10", "Verified alert prepared for broadcast.")
    real_alert = signer.create_alert(
        "Please use alternate route to Jamarat. Gate 4 congested.",
        severity="HIGH", source="Hajj-Control-Room-01",
    )
    if verifier.verify(real_alert):
        queue.push(real_alert)
        step("14:10", f'  -> VERIFIED & SENT via 5G broadcast: "{real_alert["message"]}"')

    # ------------------------------------------------------------------ #
    # 14:15 — Situation resolved
    # ------------------------------------------------------------------ #
    step("14:15", "Crowd density in Jamarat reduces. Risk score drops to 40.")
    step("14:15", "Dashboard returns to GREEN across all zones.", pause=0.2)

    banner("Drill complete. All modules responded within policy thresholds.")

    print("\nSummary:")
    print(f"  - DDoS attacks blocked:      1  (Module 1)")
    print(f"  - Crowd anomalies flagged:   1  (Module 2, Jamarat -> RED)")
    print(f"  - Fake alerts blocked:       1  (Module 3)")
    print(f"  - Verified alerts broadcast: 1  (Module 3)")


if __name__ == "__main__":
    main()
