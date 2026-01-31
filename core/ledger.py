from datetime import datetime
from sqlalchemy.orm import Session
from models import IncidentEvent

# =========================================================
# Ledger Event Types (canonical – do not rename later)
# =========================================================

EVENT_DETECTED = "detected"
EVENT_ALERTED = "alerted"
EVENT_ESCALATED = "escalated"
EVENT_RESPONSE_DRAFTED = "response_drafted"
EVENT_STATUS_CHANGED = "status_changed"
EVENT_CLOSED = "closed"

# =========================================================
# Ledger Writer
# =========================================================

class IncidentLedger:
    """
    Append-only ledger for incident lifecycle events.
    Each event represents a meaningful state change.
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    # -----------------------------------------------------
    # Core event writer
    # -----------------------------------------------------

    def record_event(
        self,
        incident_id: int,
        event_type: str,
        description: str,
    ):
        event = IncidentEvent(
            incident_id=incident_id,
            event_type=event_type,
            description=description,
            created_at=datetime.utcnow(),
        )

        self.db.add(event)
        self.db.commit()

    # -----------------------------------------------------
    # Semantic helpers (use THESE everywhere)
    # -----------------------------------------------------

    def record_detected(self, incident_id: int, source: str):
        self.record_event(
            incident_id,
            EVENT_DETECTED,
            f"Incident detected from source: {source}"
        )

    def record_alerted(self, incident_id: int, risk_level: str):
        self.record_event(
            incident_id,
            EVENT_ALERTED,
            f"Incident crossed alert threshold (risk={risk_level})"
        )

    def record_escalated(self, incident_id: int, from_level: str, to_level: str):
        self.record_event(
            incident_id,
            EVENT_ESCALATED,
            f"Risk escalated from {from_level} to {to_level}"
        )

    def record_response_drafted(self, incident_id: int):
        self.record_event(
            incident_id,
            EVENT_RESPONSE_DRAFTED,
            "AI-assisted response draft generated"
        )

    def record_status_change(self, incident_id: int, new_status: str):
        self.record_event(
            incident_id,
            EVENT_STATUS_CHANGED,
            f"Incident status changed to '{new_status}'"
        )

    def record_closed(self, incident_id: int):
        self.record_event(
            incident_id,
            EVENT_CLOSED,
            "Incident closed"
        )

    # -----------------------------------------------------
    # Timeline retrieval
    # -----------------------------------------------------

    def get_timeline(self, incident_id: int):
        """
        Returns a chronological list of ledger events
        for an incident.
        """
        return (
            self.db.query(IncidentEvent)
            .filter(IncidentEvent.incident_id == incident_id)
            .order_by(IncidentEvent.created_at.asc())
            .all()
        )
# =========================================================
# BACKWARD-COMPATIBILITY HELPERS
# =========================================================

import hashlib
from datetime import datetime

# =========================================================
# BACKWARD-COMPATIBILITY HELPERS
# =========================================================

import hashlib
import json

def compute_hash(prev_hash, data) -> str:
    """
    Legacy-compatible hash function.

    Combines previous hash + structured data
    to produce deterministic SHA-256 hash.
    """
    payload = {
        "prev": prev_hash,
        "data": data,
    }

    serialized = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

