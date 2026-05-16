import requests
import pandas as pd
import io
import time
import logging

logger = logging.getLogger(__name__)

FRED_DGS10_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10"

def fetch_fred_dgs10_data(retries: int = 3, backoff_factor: float = 0.5) -> pd.DataFrame:
    """
    Fetches the DGS10 (10-Year Treasury Constant Maturity Rate) data from FRED.
    Uses exponential backoff for retries.
    Returns a pandas DataFrame with 'observation_date' and 'DGS10' columns.
    """
    for attempt in range(retries):
        try:
            response = requests.get(FRED_DGS10_URL, timeout=10)
            response.raise_for_status()

            df = pd.read_csv(io.StringIO(response.text))

            # Basic validation
            if 'observation_date' not in df.columns or 'DGS10' not in df.columns:
                raise ValueError("Missing required columns in FRED data")

            # Clean up missing values which are represented as '.' in FRED CSVs
            df['DGS10'] = pd.to_numeric(df['DGS10'], errors='coerce')
            df['observation_date'] = pd.to_datetime(df['observation_date'])
            df = df.dropna(subset=['DGS10']).sort_values('observation_date')

            return df

        except (requests.RequestException, ValueError) as e:
            if attempt == retries - 1:
                logger.error(f"Failed to fetch FRED data after {retries} attempts: {e}")
                pass
            else:
                sleep_time = backoff_factor * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)

    raise RuntimeError("FRED API ingestion failed after max retries")
