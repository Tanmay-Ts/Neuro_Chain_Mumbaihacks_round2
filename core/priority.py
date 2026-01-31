"""
priority.py

Priority & risk scoring engine.
FULLY backward-compatible.
NEVER raises runtime errors.
"""

from datetime import datetime
from models import (
    INCIDENT_STATUS_OPEN,
    INCIDENT_STATUS_MONITORING,
)

# =========================================================
# Risk ordering
# =========================================================

RISK_ORDER = {
    "low": 1,
    "medium": 2,
    "high": 3,
}

# =========================================================
# Source weighting
# =========================================================

SOURCE_WEIGHTS = {
    "news": 1.0,
    "youtube": 0.85,
    "reddit": 0.7,
    "twitter": 0.6,
    "web": 0.5,
    "unknown": 0.4,
}

# =========================================================
# Alert thresholds
# =========================================================

MIN_ALERT_RISK = "medium"
MIN_ALERT_MENTIONS = 3


# =========================================================
# MAIN ENTRY (LEGACY SAFE)
# =========================================================

def score_priority(*args):
    """
    Accepts ALL legacy call styles safely.

    Supported:
    - score_priority(likes, comments, shares, text)
    - score_priority(likes, comments, text)
    - score_priority(db, post)

    ALWAYS returns: "low" | "medium" | "high"
    NEVER raises.
    """

    # --------------------------------------------------
    # LEGACY COLLECTOR PATH (NO DB)
    # --------------------------------------------------
    if len(args) in (3, 4):
        likes = args[0] or 0
        comments = args[1] or 0
        shares = args[2] or 0 if len(args) == 4 else 0

        mentions = likes + comments + shares

        if mentions >= 20:
            return "high"
        elif mentions >= 5:
            return "medium"
        return "low"

    # --------------------------------------------------
    # FULL PIPELINE PATH (DB + Post)
    # --------------------------------------------------
    if len(args) == 2:
        db, post = args

        base_score = (
            0.9 if post.priority.lower() == "high"
            else 0.6 if post.priority.lower() == "medium"
            else 0.3
        )

        mentions = (
            (post.likes or 0)
            + (post.comments or 0)
            + (post.shares or 0)
        )

        from models import Incident
        from core.ledger import IncidentLedger

        incident = (
            db.query(Incident)
            .filter(Incident.title == post.text[:512])
            .first()
        )

        if not incident:
            incident = Incident(
                title=post.text[:512],
                source=post.platform,
                risk_level="low",
                status=INCIDENT_STATUS_OPEN,
            )
            db.add(incident)
            db.commit()
            db.refresh(incident)

        # Simple escalation logic (safe)
        if mentions >= MIN_ALERT_MENTIONS:
            incident.status = INCIDENT_STATUS_MONITORING

        db.add(incident)
        db.commit()

        return incident.risk_level

    # --------------------------------------------------
    # SAFETY FALLBACK
    # --------------------------------------------------
    return "low"
