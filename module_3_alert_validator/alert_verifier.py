"""
alert_verifier.py
Verifies emergency alert authenticity using HMAC-based digital signatures,
so only alerts issued by an authorized Hajj control-room key can reach
the 5G broadcast channel. Also implements a priority queue for verified
alerts (CRITICAL > HIGH > MEDIUM > LOW).
"""

import hashlib
import hmac
import heapq
import itertools
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AlertIntegrity")

SEVERITY_RANK = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


class AlertSigner:
    """Used by an authorized control-room source to sign outgoing alerts."""

    def __init__(self, secret_key: bytes):
        self.secret_key = secret_key

    def sign(self, message: str) -> str:
        return hmac.new(self.secret_key, message.encode(), hashlib.sha256).hexdigest()

    def create_alert(self, message: str, severity: str, source: str) -> dict:
        signature = self.sign(message)
        return {
            "message": message,
            "severity": severity,
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "signature": signature,
        }


class AlertVerifier:
    """Used by the broadcast controller to verify incoming alerts before queueing."""

    def __init__(self, secret_key: bytes):
        self.secret_key = secret_key

    def verify(self, alert: dict) -> bool:
        expected = hmac.new(self.secret_key, alert["message"].encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, alert.get("signature", ""))


class AlertPriorityQueue:
    """Min-heap priority queue ordered by severity, then arrival order."""

    def __init__(self):
        self._heap = []
        self._counter = itertools.count()

    def push(self, alert: dict):
        rank = SEVERITY_RANK.get(alert["severity"], 99)
        heapq.heappush(self._heap, (rank, next(self._counter), alert))

    def pop(self) -> dict:
        if not self._heap:
            return None
        _, _, alert = heapq.heappop(self._heap)
        return alert

    def __len__(self):
        return len(self._heap)


if __name__ == "__main__":
    SECRET = b"hajj-shield-demo-secret-key-2026"  # in production: pulled from a secrets manager
    signer = AlertSigner(SECRET)
    verifier = AlertVerifier(SECRET)
    queue = AlertPriorityQueue()

    # Legitimate, signed alert
    valid_alert = signer.create_alert(
        "Please use alternate route to Jamarat. Gate 4 congested.",
        severity="HIGH",
        source="Hajj-Control-Room-01",
    )

    # Forged alert — no valid signature (attacker guesses a fake one)
    forged_alert = {
        "message": "Bridge collapsed at Jamarat!",
        "severity": "CRITICAL",
        "source": "unknown",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "signature": "0" * 64,
    }

    for alert in (valid_alert, forged_alert):
        if verifier.verify(alert):
            logger.info(f"✅ Verified alert from {alert['source']}: '{alert['message']}'")
            queue.push(alert)
        else:
            logger.warning(f"🚫 REJECTED unverified/forged alert: '{alert['message']}'")

    print(f"\n{len(queue)} verified alert(s) queued for broadcast:")
    while len(queue):
        print(" -", queue.pop())
