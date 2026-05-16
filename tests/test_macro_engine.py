import unittest
import pandas as pd
import json
from unittest.mock import patch, MagicMock
from macro_engine.data_ingestion import fetch_fred_dgs10_data
from macro_engine.core_logic import detect_interest_rate_signal, calculate_industry_impact
from macro_engine.output_module import generate_o2c_output

class TestMacroEngine(unittest.TestCase):

    @patch('macro_engine.data_ingestion.requests.get')
    def test_fetch_fred_dgs10_data(self, mock_get):
        # Mock the FRED API response
        mock_response = MagicMock()
        mock_response.text = "observation_date,DGS10\n2024-01-01,4.0\n2024-01-02,3.9\n2024-01-03,."
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        df = fetch_fred_dgs10_data(retries=1)

        self.assertEqual(len(df), 2) # Should drop the row with '.'
        self.assertIn('observation_date', df.columns)
        self.assertIn('DGS10', df.columns)
        self.assertEqual(df.iloc[0]['DGS10'], 4.0)

    @patch('macro_engine.data_ingestion.requests.get')
    @patch('macro_engine.data_ingestion.time.sleep')
    def test_fetch_fred_dgs10_data_retry_failure(self, mock_sleep, mock_get):
        from requests import RequestException
        # Simulate constant network failure
        mock_get.side_effect = RequestException("Network error")

        with self.assertRaises(RuntimeError) as context:
            fetch_fred_dgs10_data(retries=3, backoff_factor=0.01)

        self.assertEqual(str(context.exception), "FRED API ingestion failed after max retries")
        self.assertEqual(mock_get.call_count, 3)

    def test_detect_interest_rate_signal_active(self):
        # Create a dataframe showing a drop
        data = {
            'observation_date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05', '2024-01-06']),
            'DGS10': [4.0, 4.0, 4.0, 4.0, 4.0, 3.8] # SMA of previous 5 days is 4.0, drop is -0.2 (<= -0.1 threshold)
        }
        df = pd.DataFrame(data)

        signal = detect_interest_rate_signal(df, window_size=5, threshold=-0.1)
        self.assertTrue(signal)

    def test_detect_interest_rate_signal_inactive(self):
        # Create a dataframe showing no significant drop
        data = {
            'observation_date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05', '2024-01-06']),
            'DGS10': [4.0, 4.0, 4.0, 4.0, 4.0, 4.1]
        }
        df = pd.DataFrame(data)

        signal = detect_interest_rate_signal(df, window_size=5, threshold=-0.1)
        self.assertFalse(signal)

    def test_detect_interest_rate_signal_edge_cases(self):
        # df = None
        self.assertFalse(detect_interest_rate_signal(None))

        # empty df
        self.assertFalse(detect_interest_rate_signal(pd.DataFrame()))

        # length < window_size
        data = {
            'observation_date': pd.to_datetime(['2024-01-01', '2024-01-02']),
            'DGS10': [4.0, 3.8]
        }
        df = pd.DataFrame(data)
        self.assertFalse(detect_interest_rate_signal(df, window_size=5))

    def test_calculate_industry_impact_signal_true(self):
        scores = calculate_industry_impact(True)
        self.assertEqual(scores["Real Estate"], 50)
        self.assertEqual(scores["Banking"], -30)
        self.assertEqual(scores["Energy"], 0)
        self.assertEqual(len(scores), 16)

    def test_calculate_industry_impact_signal_false(self):
        scores = calculate_industry_impact(False)
        self.assertEqual(scores["Real Estate"], 0)
        self.assertEqual(scores["Banking"], 0)
        self.assertEqual(len(scores), 16)

    def test_generate_o2c_output(self):
        active_signals = {"SIGNAL_LONG_TERM_INTEREST_RATE_DOWN": True}
        industry_scores = {"Real Estate": 50, "Banking": -30}

        output_str = generate_o2c_output(active_signals, industry_scores)
        output_dict = json.loads(output_str)

        self.assertIn("timestamp", output_dict)

        # Strict UTC timestamp validation
        from datetime import datetime
        try:
            # isoformat with timezone handles it well, e.g. 2026-05-16T23:18:24.000+00:00
            dt = datetime.fromisoformat(output_dict["timestamp"])
            self.assertIsNotNone(dt.tzinfo)
        except ValueError:
            self.fail("Timestamp is not a valid ISO 8601 format")

        self.assertEqual(output_dict["active_signals"], active_signals)
        self.assertEqual(output_dict["industry_scores"], industry_scores)

if __name__ == '__main__':
    unittest.main()
