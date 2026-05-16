import pandas as pd
from typing import Dict

def detect_interest_rate_signal(df: pd.DataFrame, window_size: int = 5, threshold: float = -0.1) -> bool:
    """
    Detects if there is a signal for a dropping long-term interest rate.

    Logic:
    - Calculates the simple moving average (SMA) over the last `window_size` days.
    - If the change between the current rate and the SMA is less than `threshold`, signal is active.

    Args:
        df: DataFrame containing 'observation_date' and 'DGS10'
        window_size: Number of days for calculating trend.
        threshold: The negative threshold required to trigger the signal.

    Returns:
        True if the signal is active, False otherwise.
    """
    if df is None or df.empty or len(df) < window_size:
        return False

    df = df.copy().sort_values('observation_date')

    # Calculate SMA
    df['SMA'] = df['DGS10'].rolling(window=window_size).mean()

    # Get latest data point
    latest = df.iloc[-1]

    # Ensure SMA is not NaN before checking
    if pd.isna(latest['SMA']):
        return False

    # Check if the drop is beyond the threshold
    change = latest['DGS10'] - latest['SMA']

    return change <= threshold

def calculate_industry_impact(signal_long_term_interest_rate_down: bool) -> Dict[str, int]:
    """
    Calculates the impact score for 16 industries based on active signals.
    """

    # Initialize all 16 industries with neutral scores (0)
    industries = {
        "Real Estate": 0,
        "Banking": 0,
        "Energy": 0,
        "Automotive": 0,
        "Aviation": 0,
        "Materials": 0,
        "Technology": 0,
        "Healthcare": 0,
        "Consumer Staples": 0,
        "Consumer Discretionary": 0,
        "Utilities": 0,
        "Telecommunications": 0,
        "Industrials": 0,
        "Retail": 0,
        "Pharmaceuticals": 0,
        "Transportation": 0
    }

    if signal_long_term_interest_rate_down:
        # Apply the impact matrix
        industries["Real Estate"] += 50
        industries["Banking"] -= 30
        industries["Energy"] += 0
        industries["Automotive"] += 0
        industries["Aviation"] += 0
        industries["Materials"] += 0

    return industries
