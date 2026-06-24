import json
import os
from datetime import datetime, timezone

LOG_FILE = "audit_log.json"


def _load_log() -> list:
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save_log(entries: list):
    with open(LOG_FILE, "w") as f:
        json.dump(entries, f, indent=2)


def log_submission(content_id: str, creator_id: str, attribution: str,
                   confidence: float, llm_score: float, stylo_score: float) -> None:
    """Writes a new classification entry to the audit log."""
    entries = _load_log()
    entry = {
        "content_id": content_id,
        "creator_id": creator_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "attribution": attribution,
        "confidence": confidence,
        "llm_score": llm_score,
        "stylo_score": stylo_score,
        "status": "classified",
        "appeal_reasoning": None,
    }
    entries.append(entry)
    _save_log(entries)


def log_appeal(content_id: str, creator_reasoning: str) -> bool:
    """
    Updates an existing log entry with appeal info.
    Returns True if found and updated, False if content_id not found.
    """
    entries = _load_log()
    for entry in entries:
        if entry["content_id"] == content_id:
            entry["status"] = "under_review"
            entry["appeal_reasoning"] = creator_reasoning
            entry["appeal_timestamp"] = datetime.now(timezone.utc).isoformat()
            _save_log(entries)
            return True
    return False


def get_log() -> list:
    """Returns all audit log entries."""
    return _load_log()