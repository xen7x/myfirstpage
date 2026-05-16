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

    def test_detect_interest_rate_signal_active(self):
        # Create a dataframe showing a drop
        data = {
            'observation_date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']),
            'DGS10': [4.0, 4.0, 4.0, 4.0, 3.8] # SMA will be 3.96, drop is -0.16 (<= -0.1 threshold)
        }
        df = pd.DataFrame(data)

        signal = detect_interest_rate_signal(df, window_size=5, threshold=-0.1)
        self.assertTrue(signal)

    def test_detect_interest_rate_signal_inactive(self):
        # Create a dataframe showing no significant drop
        data = {
            'observation_date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']),
            'DGS10': [4.0, 4.0, 4.0, 4.0, 4.1]
        }
        df = pd.DataFrame(data)

        signal = detect_interest_rate_signal(df, window_size=5, threshold=-0.1)
        self.assertFalse(signal)

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
        self.assertEqual(output_dict["active_signals"], active_signals)
        self.assertEqual(output_dict["industry_scores"], industry_scores)

if __name__ == '__main__':
    unittest.main()
