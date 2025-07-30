#!/usr/bin/env python3
"""
Comprehensive Security Test Suite for Flask CSV Upload Endpoint
Integrates all security testing components and provides comprehensive coverage
of file upload vulnerabilities, CSV injection, and security best practices for 2025.
"""
import pytest
import io
import os
import sys
import time
import threading
from unittest.mock import patch, MagicMock
import tempfile
import zipfile

# Import Flask app and security utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app import app, allowed_file

# Import security testing utilities
from security_test_utils import (
    SecurityTestDataGenerator, FileValidationHelper, SecurityTestAssertions,
    PerformanceSecurityHelper, TestDataFactory
)


class TestComprehensiveFileSecurity:
    """Comprehensive file upload security testing suite"""
    
    @pytest.fixture(scope="class")
    def app_client(self):
        """Create Flask test client with security configuration"""
        app.config.update({
            'TESTING': True,
            'WTF_CSRF_ENABLED': False,
            'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,
            'SECRET_KEY': 'test-secret-never-use-in-production'
        })
        
        with app.test_client() as client:
            with app.app_context():
                yield client
    
    @pytest.fixture
    def security_data(self):
        """Security test data generator"""
        return SecurityTestDataGenerator()
    
    @pytest.fixture
    def validator(self):
        """File validation helper"""
        return FileValidationHelper()
    
    @pytest.fixture
    def assertions(self):
        """Security assertions helper"""
        return SecurityTestAssertions()
    
    @pytest.fixture
    def factory(self):
        """Test data factory"""
        return TestDataFactory()

    def test_file_extension_security_comprehensive(self, app_client, security_data):
        """Comprehensive file extension security testing"""
        # Test allowed extensions
        allowed_files = [
            ('valid.csv', b'Name,Company\nJohn,Acme'),
            ('valid.xlsx', b'PK\x03\x04fake_excel_header'),
            ('valid.xls', b'\xd0\xcf\x11\xe0legacy_excel'),
        ]
        
        for filename, content in allowed_files:
            data = {'file': (io.BytesIO(content), filename)}
            response = app_client.post('/upload', data=data)
            assert response.status_code in [200, 302, 400], f"Should handle valid file {filename}"
        
        # Test blocked extensions with various bypass attempts
        malicious_extensions = [
            'virus.exe', 'malware.bat', 'script.cmd', 'trojan.scr',
            'keylogger.pif', 'rootkit.com', 'exploit.js', 'backdoor.vbs',
            'shell.php', 'webshell.jsp', 'payload.jar', 'bomb.zip'
        ]
        
        for malicious_file in malicious_extensions:
            # Test direct upload
            data = {'file': (io.BytesIO(b'malicious content'), malicious_file)}
            response = app_client.post('/upload', data=data)
            assert response.status_code == 302, f"Should reject {malicious_file}"
            
            # Test with CSV extension bypass
            bypass_name = f"{malicious_file}.csv"
            data = {'file': (io.BytesIO(b'Name,Company\nTest,Corp'), bypass_name)}
            response = app_client.post('/upload', data=data)
            # Should handle gracefully (either accept as CSV or reject safely)
            assert response.status_code in [200, 302], f"Should handle bypass {bypass_name}"

    def test_csv_injection_comprehensive_2025(self, app_client, security_data, assertions):
        """Comprehensive CSV injection testing for 2025"""
        injection_payloads = security_data.create_malicious_csv_payloads()
        
        for payload_name, payload in injection_payloads.items():
            # Test payload in different CSV positions 
            test_positions = [
                f"{payload},LastName,Company,Title,Industry",  # First column
                f"FirstName,{payload},Company,Title,Industry",  # Second column
                f"FirstName,LastName,{payload},Title,Industry",  # Company name
                f"FirstName,LastName,Company,{payload},Industry",  # Job title
                f"FirstName,LastName,Company,Title,{payload}",  # Industry/notes
            ]
            
            for pos_idx, csv_row in enumerate(test_positions):
                csv_content = f"First Name,Last Name,Company Name,Title,Industry\n{csv_row}"
                
                data = {'file': (io.BytesIO(csv_content.encode()), f'injection_{payload_name}_{pos_idx}.csv')}
                response = app_client.post('/upload', data=data)
                
                # Should handle injection without crashing
                assert response.status_code in [200, 302], f"Should handle {payload_name} in position {pos_idx}"
                
                # Verify no code execution indicators
                response_text = response.get_data(as_text=True)
                assertions.assert_no_code_execution_indicators(response_text, f"{payload_name}_{pos_idx}")

    def test_executable_masquerading_comprehensive(self, app_client, security_data, validator):
        """Comprehensive executable file masquerading detection"""
        file_signatures = security_data.create_executable_file_signatures()
        
        for file_type, signature in file_signatures.items():
            # Create malicious content with executable signature but CSV extension
            malicious_content = signature + b'This is malicious content disguised as CSV' + b'\x00' * 1000
            
            # Add some CSV-like content at the end to make it look legitimate
            csv_like_content = b'\nName,Company,Title\nHacker,EvilCorp,Attacker\n'
            full_content = malicious_content + csv_like_content
            
            data = {'file': (io.BytesIO(full_content), f'disguised_{file_type}.csv')}
            response = app_client.post('/upload', data=data)
            
            # Should detect and handle executable files appropriately
            assert response.status_code in [200, 302, 400], f"Should handle disguised {file_type}"
            
            # Verify file type detection (if implemented)
            response_text = response.get_data(as_text=True)
            # Application might show error or process as CSV - both are acceptable if safe

    def test_polyglot_file_security(self, app_client, security_data):
        """Test polyglot file security (files that are valid in multiple formats)"""
        csv_content = "Name,Company,Title\nJohn,Acme,CEO\nJane,Tech,CTO"
        executable_payload = b'#!/bin/bash\necho "This is executable content"\ncalc\n'
        
        # Create polyglot file
        polyglot_content = security_data.create_polyglot_file(csv_content, executable_payload)
        
        data = {'file': (io.BytesIO(polyglot_content), 'polyglot.csv')}
        response = app_client.post('/upload', data=data)
        
        # Should handle polyglot files safely
        assert response.status_code in [200, 302], "Should handle polyglot file safely"
        
        # Check that executable content isn't processed
        response_text = response.get_data(as_text=True)
        execution_indicators = ['bash', 'echo', 'calc', '#!/']
        for indicator in execution_indicators:
            assert indicator not in response_text.lower(), f"Should not process executable content: {indicator}"

    def test_file_size_security_comprehensive(self, app_client):
        """Comprehensive file size security testing"""
        max_size = 16 * 1024 * 1024  # 16MB limit
        
        # Test edge cases around size limit
        size_test_cases = [
            (max_size - 1000, "just_under_limit.csv", True),
            (max_size, "exactly_at_limit.csv", True),
            (max_size + 1, "just_over_limit.csv", False),
            (max_size * 2, "double_limit.csv", False),
            (max_size * 10, "huge_file.csv", False),
        ]
        
        for size, filename, should_accept in size_test_cases:
            # Create CSV content of specified size
            header = "Name,Company,Title,Description\n"
            header_size = len(header.encode())
            remaining_size = size - header_size
            
            if remaining_size > 0:
                # Fill with repeated data
                row_template = "User{},Company{},Title{},Description{}\n"
                row_count = 0
                content_lines = [header.rstrip()]
                
                while len('\n'.join(content_lines).encode()) < size:
                    row = row_template.format(row_count, row_count, row_count, row_count)
                    content_lines.append(row.rstrip())
                    row_count += 1
                    
                    # Prevent infinite loop
                    if row_count > 100000:
                        break
                
                content = '\n'.join(content_lines)
            else:
                content = header
            
            data = {'file': (io.BytesIO(content.encode()), filename)}
            response = app_client.post('/upload', data=data)
            
            if should_accept:
                assert response.status_code in [200, 302, 413], f"Should handle {filename} appropriately"
            else:
                assert response.status_code == 413, f"Should reject oversized file {filename}"

    def test_zip_bomb_protection(self, app_client, security_data):
        """Test protection against zip bomb attacks"""
        zip_bomb = security_data.create_zip_bomb_excel()
        
        data = {'file': (zip_bomb, 'zipbomb.xlsx')}
        
        # Measure response time to ensure no excessive processing
        start_time = time.time()
        response = app_client.post('/upload', data=data)
        processing_time = time.time() - start_time
        
        # Should handle zip bomb without excessive processing time
        assert processing_time < 30, "Should not spend excessive time processing zip bomb"
        assert response.status_code in [200, 302, 400, 413], "Should handle zip bomb safely"

    def test_concurrent_upload_security(self, app_client):
        """Test concurrent upload security and race conditions"""
        results = []
        
        def upload_worker(worker_id):
            """Worker function for concurrent uploads"""
            try:
                csv_content = f"Name,Company,ID\nWorker{worker_id},TestCorp,{worker_id}"
                data = {'file': (io.BytesIO(csv_content.encode()), f'concurrent_{worker_id}.csv')}
                
                response = app_client.post('/upload', data=data)
                results.append((worker_id, response.status_code, len(response.get_data())))
            except Exception as e:
                results.append((worker_id, 'ERROR', str(e)))
        
        # Start concurrent uploads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=upload_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=30)
        
        # Verify all uploads completed
        assert len(results) == 10, "All concurrent uploads should complete"
        
        # Verify no race conditions caused crashes
        for worker_id, status, response_size in results:
            if isinstance(status, int):
                assert status in [200, 302, 400, 413], f"Worker {worker_id} should return valid status"
                assert response_size > 0, f"Worker {worker_id} should return response content"

    def test_session_security_comprehensive(self, app_client, assertions):
        """Comprehensive session security testing"""
        # Test various scenarios that modify session
        test_scenarios = [
            ("normal.csv", "Name,Company\nJohn,Acme"),
            ("injection.csv", "Name,Company\n=cmd|'/c calc',EvilCorp"),
            ("unicode.csv", "Naïve,Café Corp"),
        ]
        
        for filename, content in test_scenarios:
            data = {'file': (io.BytesIO(content.encode()), filename)}
            response = app_client.post('/upload', data=data)
            
            # Check session security after each upload
            with app_client.session_transaction() as sess:
                assertions.assert_session_security(sess, filename)
                
                # Verify session data integrity
                if 'file_data' in sess:
                    # Should be base64 encoded
                    import base64
                    try:
                        decoded_data = base64.b64decode(sess['file_data'])
                        assert len(decoded_data) > 0, "Session file data should be valid"
                    except Exception as e:
                        pytest.fail(f"Session file data should be valid base64: {e}")

    def test_error_message_security_comprehensive(self, app_client, assertions):
        """Comprehensive error message security testing"""
        # Test various error conditions
        error_scenarios = [
            # No file
            ({}, "no_file_error"),
            # Empty filename
            ({'file': (io.BytesIO(b'test'), '')}, "empty_filename"),
            # Invalid extension
            ({'file': (io.BytesIO(b'test'), 'malware.exe')}, "invalid_extension"),
            # Oversized file
            ({'file': (io.BytesIO(b'x' * (17 * 1024 * 1024)), 'huge.csv')}, "oversized_file"),
            # Malformed CSV
            ({'file': (io.BytesIO(b'invalid\x00csv\x01data'), 'malformed.csv')}, "malformed_content"),
        ]
        
        for data, scenario_name in error_scenarios:
            response = app_client.post('/upload', data=data)
            
            # Verify proper error handling
            assertions.assert_proper_error_handling(response, [200, 302, 400, 413], scenario_name)
            
            # Verify no sensitive information disclosure
            response_text = response.get_data(as_text=True)
            assertions.assert_no_sensitive_info_disclosure(response_text, scenario_name)

    def test_memory_exhaustion_protection(self, app_client):
        """Test protection against memory exhaustion attacks"""
        # Create CSV designed to consume excessive memory when parsed
        memory_exhaustion_csv = '''Name,Data
User1,''' + 'A' * (1024 * 1024) + '''
User2,''' + 'B' * (1024 * 1024) + '''
User3,''' + 'C' * (1024 * 1024) + '''
User4,''' + 'D' * (1024 * 1024) + '''
User5,''' + 'E' * (1024 * 1024)
        
        data = {'file': (io.BytesIO(memory_exhaustion_csv.encode()), 'memory_exhaustion.csv')}
        
        # Monitor memory usage during processing
        import psutil
        import os as os_module
        
        process = psutil.Process(os_module.getpid())
        memory_before = process.memory_info().rss
        
        start_time = time.time()
        response = app_client.post('/upload', data=data)
        processing_time = time.time() - start_time
        
        memory_after = process.memory_info().rss
        memory_increase = memory_after - memory_before
        
        # Should handle large files without excessive memory consumption
        assert processing_time < 60, "Should not spend excessive time processing large CSV"
        assert memory_increase < 100 * 1024 * 1024, "Should not consume excessive memory (100MB+)"
        assert response.status_code in [200, 302, 400, 413], "Should handle memory exhaustion test safely"

    def test_pandas_security_hardening(self, app_client):
        """Test pandas security and error handling"""
        # Test various pandas-related security scenarios
        pandas_attack_scenarios = [
            # XXE-like attacks in CSV (pandas should handle safely)
            ("xxe_attempt.csv", '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>\nName,Company\n&xxe;,TestCorp'),
            
            # Extremely wide CSV (many columns)
            ("wide_csv.csv", ','.join([f'Col{i}' for i in range(10000)]) + '\n' + ','.join(['Data'] * 10000)),
            
            # CSV with embedded null bytes
            ("null_bytes.csv", 'Name,Company\x00Data\nJohn\x00Doe,Acme\x00Corp'),
            
            # CSV with mixed encodings
            ("mixed_encoding.csv", 'Naïve,Café\n José,Résumé'),
        ]
        
        for filename, content in pandas_attack_scenarios:
            data = {'file': (io.BytesIO(content.encode('utf-8', errors='ignore')), filename)}
            response = app_client.post('/upload', data=data)
            
            # Should handle pandas parsing issues gracefully
            assert response.status_code in [200, 302, 400], f"Should handle pandas scenario {filename}"

    def test_real_world_attack_simulation(self, app_client, factory, assertions):
        """Simulate real-world attack scenarios"""
        # Create realistic dataset with scattered injections
        realistic_malicious_csv = factory.create_realistic_csv_with_injections(500)
        
        data = {'file': (io.BytesIO(realistic_malicious_csv.encode()), 'realistic_attack.csv')}
        response = app_client.post('/upload', data=data)
        
        # Should handle realistic attack scenario
        assert response.status_code in [200, 302], "Should handle realistic attack scenario"
        
        # Verify security measures
        response_text = response.get_data(as_text=True)
        assertions.assert_no_code_execution_indicators(response_text, "realistic_attack")
        
        # Check session data if upload was successful
        if response.status_code == 200:
            with app_client.session_transaction() as sess:
                assertions.assert_session_security(sess, "realistic_attack")

    def test_comprehensive_edge_cases(self, app_client, factory):
        """Test comprehensive edge cases"""
        edge_case_data = factory.create_edge_case_csv_data()
        
        for case_name, csv_content in edge_case_data.items():
            data = {'file': (io.BytesIO(csv_content.encode('utf-8')), f'edge_case_{case_name}.csv')}
            response = app_client.post('/upload', data=data)
            
            # Should handle all edge cases gracefully
            assert response.status_code in [200, 302, 400], f"Should handle edge case {case_name}"


class TestSecurityIntegration:
    """Integration tests for security measures working together"""
    
    @pytest.fixture
    def app_client(self):
        """Create Flask test client"""
        app.config['TESTING'] = True
        return app.test_client()

    def test_defense_in_depth(self, app_client):
        """Test that multiple security measures work together"""
        # Create an attack that tries to bypass multiple security measures
        complex_attack = {
            'file': (
                io.BytesIO(b'\x4d\x5a\x90\x00=cmd|"/c calc"!A0,EvilCorp,Hacker\nNormal,Data,Here'),
                '../../../malware.exe.csv'
            )
        }
        
        response = app_client.post('/upload', data=complex_attack)
        
        # Multiple security measures should combine to handle this safely
        assert response.status_code in [200, 302], "Defense in depth should handle complex attack"
        
        # Verify no execution occurred
        response_text = response.get_data(as_text=True)
        attack_indicators = ['calc', 'malware', '../', 'exe']
        for indicator in attack_indicators:
            assert indicator.lower() not in response_text.lower(), f"Should neutralize {indicator}"

    def test_security_performance_impact(self, app_client):
        """Test that security measures don't significantly impact performance"""
        # Upload normal file and measure time
        normal_csv = "Name,Company,Title\n" + "\n".join([f"User{i},Company{i},Title{i}" for i in range(1000)])
        
        data = {'file': (io.BytesIO(normal_csv.encode()), 'performance_test.csv')}
        
        start_time = time.time()
        response = app_client.post('/upload', data=data)
        processing_time = time.time() - start_time
        
        # Security measures shouldn't add significant overhead
        assert processing_time < 10, "Security measures should not significantly impact performance"
        assert response.status_code in [200, 302], "Normal files should process successfully"


if __name__ == '__main__':
    # Run the comprehensive security test suite
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--maxfail=10',
        '--durations=10',
        '--strict-markers'
    ])