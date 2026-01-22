"""
Unit tests for Mist API client
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mist import get_ap_stats, reboot_ap, get_sle_metrics


class TestMistClient(unittest.TestCase):

    def setUp(self):
        # Provide dummy env vars so config validation passes during tests
        self.env_patcher = patch.dict(os.environ, {
            "MIST_API_TOKEN": "TEST_TOKEN",
            "SITE_ID": "TEST_SITE"
        })
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()
    
    @patch('mist.requests.get')
    def test_get_ap_stats_success(self, mock_get):
        """Test successful AP stats retrieval"""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "connected",
            "num_clients": 15,
            "uptime": 86400
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Test
        result = get_ap_stats("TEST_AP_123")
        
        # Assertions
        self.assertEqual(result["status"], "connected")
        self.assertEqual(result["num_clients"], 15)
        mock_get.assert_called_once()
    
    @patch('mist.requests.post')
    def test_reboot_ap_success(self, mock_post):
        """Test successful AP reboot"""
        # Mock response
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        # Test
        result = reboot_ap("TEST_AP_123")
        
        # Assertions
        self.assertEqual(result["status"], "reboot_issued")
        self.assertEqual(result["ap_id"], "TEST_AP_123")
        mock_post.assert_called_once()
    
    @patch('mist.requests.get')
    def test_get_sle_metrics_success(self, mock_get):
        """Test successful SLE metrics retrieval"""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "client": {
                "throughput": {"score": 95.5},
                "successful-connects": {"score": 99.2}
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Test
        result = get_sle_metrics()
        
        # Assertions
        self.assertIn("client", result)
        self.assertEqual(result["client"]["throughput"]["score"], 95.5)
        mock_get.assert_called_once()


if __name__ == '__main__':
    unittest.main()
