"""
pilgrim_encryptor.py
Pilgrim Privacy Shield.

- PilgrimPrivacyShield: encrypts pilgrim PII (id + location) with Fernet
  (AES-128 in CBC mode + HMAC), and only decrypts for callers with
  EMERGENCY_RESPONSE authority — every access attempt is logged.
- Anonymizer: masks pilgrim IDs and buckets locations for GDPR/PDPL-style
  analytics without exposing raw PII.
- ConsentManager: tracks pilgrim opt-in/out for location tracking.
"""

import hashlib
import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from cryptography.fernet import Fernet

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PrivacyShield")

AUTHORIZED_ROLES = {"EMERGENCY_RESPONSE", "SYSTEM_ADMIN"}


class AccessLogger:
    def __init__(self, db_path="access_log.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS access_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                pilgrim_ref TEXT,
                requester_role TEXT,
                reason TEXT,
                granted INTEGER
            )
        """)
        conn.commit()
        conn.close()

    def log_access(self, pilgrim_ref: str, requester_role: str, reason: str, granted: bool):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO access_log (timestamp, pilgrim_ref, requester_role, reason, granted) "
            "VALUES (?, ?, ?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(), pilgrim_ref, requester_role, reason, int(granted)),
        )
        conn.commit()
        conn.close()

    def all_logs(self):
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute("SELECT * FROM access_log ORDER BY id DESC").fetchall()
        conn.close()
        return rows


class PilgrimPrivacyShield:
    def __init__(self, key: bytes = None, log_path="access_log.db"):
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.access_logger = AccessLogger(log_path)

    def encrypt_pilgrim_data(self, pilgrim_id: str, location: str) -> bytes:
        timestamp = datetime.now(timezone.utc).isoformat()
        data = f"{pilgrim_id}|{location}|{timestamp}"
        return self.cipher.encrypt(data.encode())

    def emergency_access(self, encrypted_data: bytes, requester_role: str, reason: str,
                          pilgrim_ref: str = "unknown") -> str:
        granted = requester_role in AUTHORIZED_ROLES
        self.access_logger.log_access(pilgrim_ref, requester_role, reason, granted)

        if granted:
            logger.info(f"✅ Access GRANTED to {requester_role} — reason: {reason}")
            return self.cipher.decrypt(encrypted_data).decode()
        else:
            logger.warning(f"🚫 Access DENIED to {requester_role} — reason given: {reason}")
            return "ACCESS DENIED"


class Anonymizer:
    """Masks PII for analytics: hashes pilgrim IDs, buckets locations into zones."""

    @staticmethod
    def mask_id(pilgrim_id: str) -> str:
        return "PID-" + hashlib.sha256(pilgrim_id.encode()).hexdigest()[:10]

    @staticmethod
    def bucket_location(zone_name: str, granularity_minutes: int = 15) -> str:
        # For analytics we only need the zone + coarse time bucket, not exact coords/timestamps.
        now = datetime.now(timezone.utc)
        bucket = now.replace(minute=(now.minute // granularity_minutes) * granularity_minutes,
                              second=0, microsecond=0)
        return f"{zone_name}@{bucket.isoformat()}"

    def anonymize_record(self, pilgrim_id: str, zone_name: str) -> dict:
        return {
            "masked_id": self.mask_id(pilgrim_id),
            "location_bucket": self.bucket_location(zone_name),
        }


class ConsentManager:
    def __init__(self, db_path="consent.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS consent (
                pilgrim_id TEXT PRIMARY KEY,
                opted_in INTEGER,
                updated_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def set_consent(self, pilgrim_id: str, opted_in: bool):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO consent (pilgrim_id, opted_in, updated_at) VALUES (?, ?, ?) "
            "ON CONFLICT(pilgrim_id) DO UPDATE SET opted_in=excluded.opted_in, updated_at=excluded.updated_at",
            (pilgrim_id, int(opted_in), datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        conn.close()

    def has_consented(self, pilgrim_id: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        row = conn.execute("SELECT opted_in FROM consent WHERE pilgrim_id = ?", (pilgrim_id,)).fetchone()
        conn.close()
        return bool(row[0]) if row else False


if __name__ == "__main__":
    shield = PilgrimPrivacyShield()
    consent = ConsentManager()
    anonymizer = Anonymizer()

    pilgrim_id = "PIL-88213"
    consent.set_consent(pilgrim_id, opted_in=True)

    encrypted = shield.encrypt_pilgrim_data(pilgrim_id, location="Mataf")
    print("Encrypted blob:", encrypted[:40], "...")

    print("\n--- Emergency responder requests access (authorized) ---")
    decrypted = shield.emergency_access(
        encrypted, requester_role="EMERGENCY_RESPONSE",
        reason="Pilgrim reported missing near Mataf", pilgrim_ref=anonymizer.mask_id(pilgrim_id),
    )
    print("Decrypted:", decrypted)

    print("\n--- Marketing team requests access (unauthorized) ---")
    denied = shield.emergency_access(
        encrypted, requester_role="MARKETING", reason="Analytics dashboard",
        pilgrim_ref=anonymizer.mask_id(pilgrim_id),
    )
    print("Result:", denied)

    print("\n--- Anonymized record for analytics ---")
    print(anonymizer.anonymize_record(pilgrim_id, "Mataf"))

    print("\n--- Access log ---")
    for row in shield.access_logger.all_logs():
        print(row)
