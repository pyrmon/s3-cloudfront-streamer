#!/usr/bin/env python3
import unittest
import os
import subprocess

class TestTerraform(unittest.TestCase):
    
    def setUp(self):
        self.terraform_dir = os.path.join(os.path.dirname(__file__), '..', 'terraform')
    
    def test_terraform_validate(self):
        """Test Terraform configuration validation"""
        try:
            # Initialize terraform
            subprocess.run(['terraform', 'init'], 
                         cwd=self.terraform_dir, 
                         check=True, 
                         capture_output=True)
            
            # Validate configuration
            result = subprocess.run(['terraform', 'validate'], 
                                  cwd=self.terraform_dir, 
                                  capture_output=True)
            
            self.assertEqual(result.returncode, 0, f"Terraform validation failed: {result.stderr.decode()}")
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.skipTest("Terraform not available")

if __name__ == '__main__':
    unittest.main()