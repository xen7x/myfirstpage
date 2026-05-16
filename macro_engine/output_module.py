import json
from datetime import datetime, timezone
from typing import Dict
from .interfaces import OutputData

def generate_o2c_output(active_signals: Dict[str, bool], industry_scores: Dict[str, int]) -> str:
    """
    Generates an Office 2.0 Canvas (.o2c) compliant JSON string.

    Args:
        active_signals: Dictionary of signal names and boolean status.
        industry_scores: Dictionary of industry names and impact scores.

    Returns:
        A JSON string formatted according to the .o2c specification.
    """
    data: OutputData = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "active_signals": active_signals,
        "industry_scores": industry_scores
    }

    return json.dumps(data, indent=2)
