"""
slice_isolator.py
Simulates isolating a compromised 5G network slice and failing traffic
over to a backup slice. In a real deployment this would call the
telecom operator's Network Slice Management API (3GPP TS 28.531 /
NSMF interfaces); here it's a clean, swappable simulation so the
control-flow logic can be demoed and unit-tested without live
network access.
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger("SliceSecurity")


class SliceIsolator:
    def __init__(self, slice_name: str, backup_slice_name: str = None):
        self.slice_name = slice_name
        self.backup_slice_name = backup_slice_name or f"{slice_name}-Backup"
        self.status = "ACTIVE"
        self.events = []

    def isolate(self):
        """Isolate the compromised slice and fail over to backup."""
        timestamp = datetime.now(timezone.utc).isoformat()
        self.status = "ISOLATED"
        event = {
            "timestamp": timestamp,
            "action": "ISOLATE",
            "slice": self.slice_name,
            "failover_to": self.backup_slice_name,
        }
        self.events.append(event)
        logger.info(f"🛡️  {self.slice_name} ISOLATED — traffic failed over to {self.backup_slice_name}")
        return event

    def restore(self):
        """Restore the primary slice once it's cleared as safe."""
        timestamp = datetime.now(timezone.utc).isoformat()
        self.status = "ACTIVE"
        event = {
            "timestamp": timestamp,
            "action": "RESTORE",
            "slice": self.slice_name,
        }
        self.events.append(event)
        logger.info(f"✅ {self.slice_name} RESTORED — primary slice back in service")
        return event


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    isolator = SliceIsolator("Hajj-Emergency-Slice")
    isolator.isolate()
    isolator.restore()
    print(isolator.events)
