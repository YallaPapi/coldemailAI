"""
Test environment validation for ColdEmailAI testing framework.

Validates that pytest, memory monitoring, and test fixtures work correctly.
Based on TaskMaster research: "pytest Flask application testing framework setup best practices 2025"
"""

import pytest
import psutil
from app import app as flask_app


class TestEnvironmentSetup:
    """Test the testing environment setup"""
    
    def test_pytest_configuration(self):
        """Verify pytest is properly configured"""
        # This test passing means pytest is working
        assert True
        
    def test_app_fixture(self, app):
        """Verify Flask app fixture works"""
        assert app is not None
        assert app.config['TESTING'] is True
        
    def test_client_fixture(self, client):
        """Verify test client fixture works"""
        assert client is not None
        response = client.get('/health')
        assert response.status_code == 200
        
    def test_memory_monitor_fixture(self, memory_monitor):
        """Verify memory monitoring fixture works"""
        # Start monitoring
        baseline = memory_monitor.start_monitoring()
        assert baseline > 0
        
        # Simulate some memory usage
        data = b'x' * 1024 * 1024  # 1MB
        
        # Check current usage
        current = memory_monitor.get_current_usage()
        assert current >= baseline
        
        # Check stats
        stats = memory_monitor.get_stats()
        assert 'baseline' in stats
        assert 'current' in stats
        assert 'increase' in stats
        
    def test_performance_thresholds_fixture(self, performance_thresholds):
        """Verify performance thresholds are defined"""
        assert 'small_file_max_increase' in performance_thresholds
        assert 'large_file_max_increase' in performance_thresholds
        assert 'processing_timeout' in performance_thresholds
        
    def test_test_data_fixtures(self, small_csv_content, large_csv_content, messy_csv_content):
        """Verify test data fixtures work"""
        # Small CSV
        assert len(small_csv_content) > 0
        assert b'first_name' in small_csv_content
        assert b'TechFlow Solutions' in small_csv_content
        
        # Large CSV
        assert len(large_csv_content) > len(small_csv_content)
        assert b'first_name' in large_csv_content
        
        # Messy CSV
        assert len(messy_csv_content) > 0
        assert b'First Name' in messy_csv_content  # Mixed case header
        
    def test_malicious_files_fixture(self, malicious_files):
        """Verify malicious files fixture works"""
        assert 'fake_csv.exe' in malicious_files
        assert 'script_injection.csv' in malicious_files
        assert 'oversized.txt' in malicious_files
        assert len(malicious_files['oversized.txt']) > 10 * 1024 * 1024  # > 10MB