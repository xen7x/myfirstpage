from typing import TypedDict, Dict

class OutputData(TypedDict):
    timestamp: str
    active_signals: Dict[str, bool]
    industry_scores: Dict[str, int]
