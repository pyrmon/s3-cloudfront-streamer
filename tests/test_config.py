#!/usr/bin/env python3
import unittest
import os
import sys
from unittest.mock import patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestConfig(unittest.TestCase):
    
    def test_missing_config(self):
        """Test configuration validation with missing vars"""
        with patch.dict(os.environ, {}, clear=True):
            from generate_signed_urls import check_config
            
            with patch('builtins.print'):
                result = check_config()
                self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()