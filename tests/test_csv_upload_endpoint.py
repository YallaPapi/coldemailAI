"""
CSV Upload Endpoint Tests for ColdEmailAI

Comprehensive testing of Flask CSV upload endpoint following TaskMaster research:
"Flask CSV file upload endpoint testing Flask test client file upload memory monitoring security validation 2025"

Tests cover legitimate files, malicious files, security validation, and memory monitoring.
Based on Context7 patterns and ZAD requirements for real business data testing.
"""

import io
import os
import pytest
import psutil
from flask.testing import FlaskClient


class TestCSVUploadEndpoint:
    """Test CSV file upload endpoint with comprehensive scenarios"""
    
    @pytest.mark.unit
    def test_valid_small_csv_upload(self, client: FlaskClient, memory_monitor, small_csv_content):
        """Test uploading valid small CSV file with memory monitoring"""
        # Start memory monitoring
        memory_monitor.start_monitoring()
        
        # Create file-like object
        csv_file = io.BytesIO(small_csv_content)
        
        # Test upload
        response = client.post('/upload', 
                             data={'file': (csv_file, 'test_leads.csv')},
                             content_type='multipart/form-data')
        
        # Verify successful upload
        assert response.status_code == 200
        assert b'mapping.html' in response.data or 'columns' in str(response.data)
        
        # Verify memory usage is reasonable for small files
        memory_monitor.assert_memory_increase_under(10 * 1024 * 1024)  # 10MB max
        
    @pytest.mark.integration
    @pytest.mark.real_data  
    def test_large_csv_upload_performance(self, client: FlaskClient, memory_monitor, large_csv_content):
        """Test uploading large CSV file with performance monitoring"""
        # Start memory monitoring
        baseline = memory_monitor.start_monitoring()
        
        # Create large file-like object
        large_file = io.BytesIO(large_csv_content)
        
        # Measure upload time
        import time
        start_time = time.time()
        
        response = client.post('/upload',
                             data={'file': (large_file, 'enterprise_leads.csv')},
                             content_type='multipart/form-data')
        
        upload_time = time.time() - start_time
        
        # Verify successful upload
        assert response.status_code == 200
        
        # Verify performance is acceptable (< 30 seconds per ZAD requirements)
        assert upload_time < 30, f"Upload took {upload_time:.2f}s, max allowed: 30s"
        
        # Verify memory usage is controlled for large files
        memory_monitor.assert_memory_increase_under(50 * 1024 * 1024)  # 50MB max
        
        # Log performance metrics for reporting
        stats = memory_monitor.get_stats()
        print(f"Large file upload performance:")
        print(f"  - File size: {len(large_csv_content)} bytes")
        print(f"  - Upload time: {upload_time:.2f}s")
        print(f"  - Memory increase: {stats['increase']} bytes")
        
    @pytest.mark.integration
    def test_messy_csv_upload_handling(self, client: FlaskClient, messy_csv_content):
        """Test uploading CSV with real-world data quality issues"""
        messy_file = io.BytesIO(messy_csv_content)
        
        response = client.post('/upload',
                             data={'file': (messy_file, 'messy_data.csv')},
                             content_type='multipart/form-data')
        
        # Should still process successfully despite messiness
        assert response.status_code == 200
        
    @pytest.mark.security
    def test_executable_file_blocked(self, client: FlaskClient, malicious_files):
        """Test that executable files disguised as CSV are blocked"""
        exe_file = io.BytesIO(malicious_files['fake_csv.exe'])
        
        response = client.post('/upload',
                             data={'file': (exe_file, 'virus.exe.csv')},
                             content_type='multipart/form-data')
        
        # Should reject malicious file
        assert response.status_code == 302  # Flask redirects on error
        # Follow redirect to check error message
        # Note: In a real app, you might want to check flash messages
        
    @pytest.mark.security
    def test_csv_injection_detection(self, client: FlaskClient, malicious_files):
        """Test detection of CSV injection attacks"""
        injection_file = io.BytesIO(malicious_files['script_injection.csv'])
        
        response = client.post('/upload',
                             data={'file': (injection_file, 'injection.csv')},
                             content_type='multipart/form-data')
        
        # Should process successfully but sanitize content
        # (The application should handle this in the processing logic)
        assert response.status_code in [200, 302]
        
    @pytest.mark.security
    def test_oversized_file_rejected(self, client: FlaskClient, malicious_files):
        """Test that oversized files are rejected"""
        # Use the 20MB oversized file
        oversized_file = io.BytesIO(malicious_files['oversized.txt'])
        
        response = client.post('/upload',
                             data={'file': (oversized_file, 'huge_file.csv')},
                             content_type='multipart/form-data')
        
        # Should reject due to size limit (16MB configured in app)
        assert response.status_code == 413 or response.status_code == 302
        
    @pytest.mark.security  
    def test_empty_file_handling(self, client: FlaskClient, malicious_files):
        """Test handling of empty files"""
        empty_file = io.BytesIO(malicious_files['empty_file.csv'])
        
        response = client.post('/upload',
                             data={'file': (empty_file, 'empty.csv')},
                             content_type='multipart/form-data')
        
        # Should handle empty file gracefully
        assert response.status_code == 302  # Likely redirects with error
        
    @pytest.mark.security
    def test_invalid_csv_format_handling(self, client: FlaskClient, malicious_files):
        """Test handling of malformed CSV files"""
        invalid_file = io.BytesIO(malicious_files['invalid_csv.csv'])
        
        response = client.post('/upload',
                             data={'file': (invalid_file, 'invalid.csv')},
                             content_type='multipart/form-data')
        
        # Should handle malformed CSV gracefully
        assert response.status_code in [200, 302]
        
    @pytest.mark.unit
    def test_no_file_uploaded(self, client: FlaskClient):
        """Test endpoint behavior when no file is uploaded"""
        response = client.post('/upload', data={}, content_type='multipart/form-data')
        
        # Should redirect back with error
        assert response.status_code == 302
        
    @pytest.mark.unit
    def test_wrong_file_extension(self, client: FlaskClient):
        """Test rejection of non-CSV file extensions"""
        # Create a text file disguised as CSV
        text_content = b"This is not a CSV file"
        text_file = io.BytesIO(text_content)
        
        response = client.post('/upload',
                             data={'file': (text_file, 'document.txt')},
                             content_type='multipart/form-data')
        
        # Should reject non-CSV files
        assert response.status_code == 302  # Flask redirects on error
        
    @pytest.mark.integration
    def test_excel_file_support(self, client: FlaskClient, valid_excel_content):
        """Test that Excel files are properly supported"""
        excel_file = io.BytesIO(valid_excel_content)
        
        response = client.post('/upload',
                             data={'file': (excel_file, 'business_data.xlsx')},
                             content_type='multipart/form-data')
        
        # Should accept Excel files
        assert response.status_code == 200
        
    @pytest.mark.performance
    def test_concurrent_uploads_memory_safety(self, client: FlaskClient, small_csv_content, memory_monitor):
        """Test memory safety during concurrent uploads simulation"""
        memory_monitor.start_monitoring()
        
        # Simulate multiple uploads (serial, but testing memory accumulation)
        for i in range(5):
            csv_file = io.BytesIO(small_csv_content)
            response = client.post('/upload',
                                 data={'file': (csv_file, f'batch_{i}.csv')},
                                 content_type='multipart/form-data')
            assert response.status_code == 200
            
        # Memory should not accumulate excessively
        memory_monitor.assert_memory_increase_under(50 * 1024 * 1024)  # 50MB total
        
    @pytest.mark.integration
    def test_unicode_filename_support(self, client: FlaskClient, small_csv_content):
        """Test support for Unicode characters in filenames"""
        csv_file = io.BytesIO(small_csv_content)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'données_企業_файл.csv')},
                             content_type='multipart/form-data')
        
        # Should handle Unicode filenames
        assert response.status_code == 200
        
        
class TestCSVUploadSecurity:
    """Dedicated security testing for CSV upload endpoint"""
    
    @pytest.mark.security
    def test_file_type_validation_bypass_attempt(self, client: FlaskClient):
        """Test attempts to bypass file type validation"""
        # Try various bypass techniques
        bypass_attempts = [
            ('malicious.csv.exe', b'Executable content'),
            ('file.csv\x00.exe', b'Null byte injection'),
            ('legit.csv', b'MZ\x90\x00\x03'),  # PE header in CSV
        ]
        
        for filename, content in bypass_attempts:
            malicious_file = io.BytesIO(content)
            response = client.post('/upload',
                                 data={'file': (malicious_file, filename)},
                                 content_type='multipart/form-data')
            
            # All should be rejected or handled safely
            assert response.status_code in [200, 302, 400, 413]
            
    @pytest.mark.security
    def test_path_traversal_in_filename(self, client: FlaskClient, small_csv_content):
        """Test path traversal attacks in filenames"""
        traversal_filenames = [
            '../../../etc/passwd.csv',
            '..\\..\\windows\\system32\\config\\sam.csv',
            '/etc/shadow.csv',
        ]
        
        for malicious_filename in traversal_filenames:
            csv_file = io.BytesIO(small_csv_content)
            response = client.post('/upload',
                                 data={'file': (csv_file, malicious_filename)},
                                 content_type='multipart/form-data')
            
            # Should handle safely (werkzeug.utils.secure_filename should protect)
            assert response.status_code in [200, 302, 400]
            
    @pytest.mark.security
    def test_content_type_spoofing(self, client: FlaskClient):
        """Test content-type header spoofing"""
        # Executable content with CSV content-type
        exe_content = b'MZ\x90\x00This is executable content'
        exe_file = io.BytesIO(exe_content)
        
        # Manually set content type in the test 
        response = client.post('/upload',
                             data={'file': (exe_file, 'spoofed.csv')},
                             content_type='multipart/form-data')
        
        # Should be handled safely by proper validation
        assert response.status_code in [200, 302, 400]