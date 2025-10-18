#!/usr/bin/env python3
import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestConfig(unittest.TestCase):
    
    def test_missing_config(self):
        """Test configuration validation with missing vars"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('dotenv.load_dotenv'):
                # Import after patching environment
                import generate_signed_urls
                import importlib
                importlib.reload(generate_signed_urls)
                
                with patch('builtins.print'):
                    result = generate_signed_urls.check_config()
                    self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()