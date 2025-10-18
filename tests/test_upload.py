#!/usr/bin/env python3
import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from upload_to_s3 import sanitize_filename

class TestUpload(unittest.TestCase):
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        test_cases = [
            ("My Video File.mp4", "My_Video_File.mp4"),
            ("Special@#$%Characters.mkv", "Special_Characters.mkv"),
            ("Multiple___Underscores.avi", "Multiple_Underscores.avi"),
            ("_Leading_Trailing_.mov", "Leading_Trailing.mov"),
            ("normal-file_name.mp4", "normal-file_name.mp4"),
        ]
        
        for input_name, expected in test_cases:
            with self.subTest(input=input_name):
                result = sanitize_filename(input_name)
                self.assertEqual(result, expected)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_bucket_name(self):
        """Test behavior when S3_BUCKET_NAME is not set"""
        with patch('dotenv.load_dotenv'):
            # Import after patching environment
            import upload_to_s3
            import importlib
            importlib.reload(upload_to_s3)
            
            with patch('builtins.print') as mock_print:
                upload_to_s3.upload_videos('/fake/path')
                mock_print.assert_any_call("❌ S3_BUCKET_NAME environment variable not set")

if __name__ == '__main__':
    unittest.main()