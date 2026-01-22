"""
Unit tests for Logic module
"""
import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from logic import determine_severity, select_remediation_action, should_remediate


class TestLogic(unittest.TestCase):
    
    def test_determine_severity_critical(self):
        """Test severity determination for critical scores"""
        severity = determine_severity(50)
        self.assertEqual(severity, "critical")
    
    def test_determine_severity_high(self):
        """Test severity determination for high scores"""
        severity = determine_severity(65)
        self.assertEqual(severity, "high")
    
    def test_determine_severity_medium(self):
        """Test severity determination for medium scores"""
        severity = determine_severity(75)
        self.assertEqual(severity, "medium")
    
    def test_determine_severity_low(self):
        """Test severity determination for low scores"""
        severity = determine_severity(85)
        self.assertEqual(severity, "low")
    
    def test_select_remediation_action_throughput(self):
        """Test remediation action selection for throughput"""
        action = select_remediation_action("throughput")
        self.assertIn(action, ["reboot", "rrm"])
    
    def test_select_remediation_action_unknown(self):
        """Test remediation action selection for unknown SLE"""
        action = select_remediation_action("unknown_sle_type")
        self.assertEqual(action, "reboot")  # Default
    
    def test_should_remediate_low_score(self):
        """Test remediation decision for low SLE score"""
        should, reason = should_remediate("AP123", "throughput", 70)
        self.assertTrue(should)
    
    def test_should_not_remediate_high_score(self):
        """Test remediation decision for high SLE score"""
        should, reason = should_remediate("AP123", "throughput", 95)
        self.assertFalse(should)


if __name__ == '__main__':
    unittest.main()
