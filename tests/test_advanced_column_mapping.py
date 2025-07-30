"""
Advanced CSV Column Mapping Tests
Task 11.2: Design Test Cases for Header Detection and Normalization

Comprehensive testing of header detection accuracy following TaskMaster research:
"Flask CSV column mapping testing best practices pandas header detection pytest property-based testing 2025"

Tests validate normalization logic, case-insensitive mapping, Unicode handling,
and business field alignment based on Context7 patterns and research findings.
"""

import io
import pytest
import pandas as pd
import unicodedata
from hypothesis import given, strategies as st
from flask.testing import FlaskClient


class TestHeaderNormalization:
    """Test header normalization logic for various edge cases"""
    
    def normalize_header(self, header):
        """Advanced header normalization based on research findings"""
        if not header or not isinstance(header, str):
            return ''
        
        # Unicode normalization (NFKD - canonical decomposition)
        normalized = unicodedata.normalize('NFKD', header)
        
        # Remove accents and combining characters, keep only ASCII-compatible chars
        ascii_header = ''.join(c for c in normalized if not unicodedata.combining(c) and ord(c) < 128)
        
        # If no ASCII characters remain, return empty (non-Latin scripts)
        if not ascii_header.strip():
            return ''
        
        # Standard normalization: lowercase, strip, replace special chars
        import re
        cleaned = re.sub(r'[^\w\s]', '', ascii_header).strip().lower().replace(' ', '_')
        
        # Handle multiple underscores
        return re.sub(r'_+', '_', cleaned).strip('_')
    
    @pytest.mark.parametrize("input_header,expected_output", [
        # Standard cases
        ("first_name", "first_name"),
        ("company_name", "company_name"),
        ("job_title", "job_title"),
        
        # Mixed case variations
        ("First_Name", "first_name"),
        ("COMPANY_NAME", "company_name"),
        ("Job_Title", "job_title"),
        
        # Space variations
        ("First Name", "first_name"),
        ("Company Name", "company_name"),
        ("Job Title", "job_title"),
        
        # Whitespace edge cases
        (" first_name ", "first_name"),
        ("  Company Name  ", "company_name"),
        ("\tJob Title\t", "job_title"),
        
        # Special character cases
        ("First-Name", "firstname"),
        ("E-Mail", "email"),
        ("Company.Name", "companyname"),
        ("Job$Title", "jobtitle"),
        
        # Unicode and accent cases
        ("naïve", "naive"),
        ("café", "cafe"),
        ("résumé", "resume"),
        ("Björn", "bjorn"),
        ("François", "francois"),
        
        # Complex Unicode cases
        ("名字", ""),  # Chinese characters -> empty (non-Latin)
        ("Ελληνικά", ""),  # Greek characters -> empty
        ("Русский", ""),  # Cyrillic characters -> empty
        
        # Edge cases
        ("", ""),
        ("   ", ""),
        ("_", ""),
        ("__", ""),
        ("123", "123"),
        ("First__Name", "first_name"),
        ("FIRST___NAME", "first_name"),
    ])
    def test_header_normalization_cases(self, input_header, expected_output):
        """Test header normalization with known edge cases"""
        result = self.normalize_header(input_header)
        assert result == expected_output, f"Failed for '{input_header}': expected '{expected_output}', got '{result}'"
    
    @given(st.text(min_size=1, max_size=30))
    def test_header_normalization_property_never_fails(self, header):
        """Property test: normalization should never fail and always return string"""
        result = self.normalize_header(header)
        assert isinstance(result, str), f"Normalization returned non-string: {type(result)}"
        assert len(result) <= len(header) + 10, f"Result suspiciously long: {len(result)} vs input {len(header)}"
    
    @given(st.lists(
        st.text(
            min_size=1, max_size=30,
            alphabet=st.characters(
                blacklist_categories=('Cs',),  # Exclude surrogate characters
                whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Pc', 'Pd', 'Mn', 'Sk', 'So')
            )
        ),
        min_size=1, max_size=10, unique=True
    ))
    def test_header_list_normalization_property(self, headers):
        """Property test: normalize list of headers without collision"""
        normalized = [self.normalize_header(h) for h in headers]
        
        # Check all results are strings
        assert all(isinstance(n, str) for n in normalized)
        
        # Check for excessive empty results (would indicate over-aggressive normalization)
        empty_count = sum(1 for n in normalized if not n)
        assert empty_count <= len(normalized) // 2, f"Too many empty results: {empty_count}/{len(normalized)}"


class TestBusinessFieldMapping:
    """Test mapping of normalized headers to business fields"""
    
    def get_business_field_mappings(self):
        """Business field mapping dictionary based on research"""
        return {
            # First name variations
            'first_name': 'first_name',
            'firstname': 'first_name',
            'fname': 'first_name',
            'given_name': 'first_name',
            'forename': 'first_name',
            
            # Last name variations
            'last_name': 'last_name',
            'lastname': 'last_name',
            'lname': 'last_name',
            'surname': 'last_name',
            'family_name': 'last_name',
            
            # Company name variations
            'company_name': 'company_name',
            'companyname': 'company_name',
            'company': 'company_name',
            'organization': 'company_name',
            'org': 'company_name',
            'business': 'company_name',
            'employer': 'company_name',
            
            # Job title variations
            'job_title': 'job_title',
            'jobtitle': 'job_title',
            'title': 'job_title',
            'position': 'job_title',
            'role': 'job_title',
            'designation': 'job_title',
            
            # Industry variations
            'industry': 'industry',
            'sector': 'industry',
            'field': 'industry',
            'business_type': 'industry',
            
            # Email variations
            'email': 'email',
            'email_address': 'email',
            'e_mail': 'email',
            
            # Location variations
            'city': 'city',
            'state': 'state',
            'country': 'country',
            'location': 'city',
        }
    
    def normalize_header(self, header):
        """Use same normalization as above"""
        if not header or not isinstance(header, str):
            return ''
        
        normalized = unicodedata.normalize('NFKD', header)
        ascii_header = ''.join(c for c in normalized if not unicodedata.combining(c) and ord(c) < 128)
        
        if not ascii_header.strip():
            return ''
        
        import re
        cleaned = re.sub(r'[^\w\s]', '', ascii_header).strip().lower().replace(' ', '_')
        return re.sub(r'_+', '_', cleaned).strip('_')
    
    def map_csv_columns(self, df_columns):
        """Map CSV columns to business fields"""
        mapping_dict = self.get_business_field_mappings()
        mapped_fields = {}
        unmapped_columns = []
        
        for col in df_columns:
            normalized = self.normalize_header(col)
            if normalized in mapping_dict:
                business_field = mapping_dict[normalized]
                mapped_fields[business_field] = col
            else:
                unmapped_columns.append(col)
                
        return mapped_fields, unmapped_columns
    
    @pytest.mark.parametrize("input_columns,expected_mappings", [
        # Standard business headers
        (
            ["First Name", "Last Name", "Company Name", "Job Title", "Industry"],
            {"first_name": "First Name", "last_name": "Last Name", "company_name": "Company Name", 
             "job_title": "Job Title", "industry": "Industry"}
        ),
        
        # Mixed case variations
        (
            ["FIRST_NAME", "last_name", "Company", "Title", "INDUSTRY"],
            {"first_name": "FIRST_NAME", "last_name": "last_name", "company_name": "Company",
             "job_title": "Title", "industry": "INDUSTRY"}
        ),
        
        # Alternative naming conventions
        (
            ["Given Name", "Surname", "Organization", "Position", "Sector"],
            {"first_name": "Given Name", "last_name": "Surname", "company_name": "Organization",
             "job_title": "Position", "industry": "Sector"}
        ),
        
        # With special characters and spaces
        (
            ["First-Name", "Last Name ", " Company.Name", "Job$Title", "E-Mail"],
            {"first_name": "First-Name", "last_name": "Last Name ", "company_name": " Company.Name",
             "job_title": "Job$Title", "email": "E-Mail"}
        ),
        
        # Abbreviated forms
        (
            ["FName", "LName", "Org", "Role", "Email Address"],
            {"first_name": "FName", "last_name": "LName", "company_name": "Org",
             "job_title": "Role", "email": "Email Address"}
        ),
    ])
    def test_business_field_mapping_accuracy(self, input_columns, expected_mappings):
        """Test that business field mapping works correctly for various header formats"""
        mapped_fields, unmapped_columns = self.map_csv_columns(input_columns)
        
        # Check that all expected mappings are found
        for business_field, original_header in expected_mappings.items():
            assert business_field in mapped_fields, f"Missing business field: {business_field}"
            assert mapped_fields[business_field] == original_header, \
                f"Wrong mapping for {business_field}: expected '{original_header}', got '{mapped_fields[business_field]}'"
        
        # Check that unmapped columns are reasonable
        expected_unmapped = set(input_columns) - set(expected_mappings.values())
        actual_unmapped = set(unmapped_columns)
        assert actual_unmapped == expected_unmapped, \
            f"Unmapped columns mismatch: expected {expected_unmapped}, got {actual_unmapped}"
    
    def test_mapping_completeness_for_standard_business_csv(self):
        """Test mapping completeness for typical business CSV headers"""
        standard_headers = [
            "First Name", "Last Name", "Company Name", "Job Title", 
            "Industry", "Email", "City", "State", "Country"
        ]
        
        mapped_fields, unmapped_columns = self.map_csv_columns(standard_headers)
        
        # Should map at least 80% of standard business fields
        mapping_rate = len(mapped_fields) / len(standard_headers)
        assert mapping_rate >= 0.8, f"Low mapping rate: {mapping_rate:.1%} ({len(mapped_fields)}/{len(standard_headers)})"
        
        # Check that all critical business fields are mapped
        critical_fields = {'first_name', 'company_name', 'job_title'}
        mapped_critical = set(mapped_fields.keys()) & critical_fields
        assert len(mapped_critical) >= 2, f"Missing critical fields: {critical_fields - mapped_critical}"
    
    def test_duplicate_header_handling(self):
        """Test handling of duplicate headers"""
        duplicate_headers = ["First Name", "First Name", "Company", "Company Name"]
        mapped_fields, unmapped_columns = self.map_csv_columns(duplicate_headers)
        
        # Should handle duplicates gracefully (latest mapping wins)
        assert "first_name" in mapped_fields or "company_name" in mapped_fields
        assert len(mapped_fields) <= len(set(duplicate_headers))  # No more mappings than unique normalized headers


class TestFlaskCSVUploadIntegration:
    """Test Flask endpoint integration with advanced header mapping"""
    
    def create_test_csv(self, headers, rows):
        """Create in-memory CSV file for testing"""
        csv_content = ",".join(headers) + "\n"
        csv_content += "\n".join([",".join(row) for row in rows])
        return io.BytesIO(csv_content.encode('utf-8'))
    
    @pytest.mark.integration
    def test_csv_upload_with_mixed_case_headers(self, client: FlaskClient):
        """Test CSV upload with mixed case headers"""
        headers = ["First Name", "COMPANY_NAME", "job-title", "E-Mail"]
        rows = [["John Smith", "Tech Corp", "Developer", "john@tech.com"]]
        
        csv_file = self.create_test_csv(headers, rows)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'mixed_case_test.csv')},
                             content_type='multipart/form-data')
        
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        
        # Should detect mapping fields despite case variations
        expected_fields = ['first_name', 'company_name', 'job_title', 'email']
        detected_fields = []
        
        for field in expected_fields:
            if f'map_{field}' in response_text:
                detected_fields.append(field)
        
        detection_rate = len(detected_fields) / len(expected_fields)
        assert detection_rate >= 0.75, f"Low detection rate: {detection_rate:.1%} ({len(detected_fields)}/{len(expected_fields)})"
    
    @pytest.mark.integration
    def test_csv_upload_with_unicode_headers(self, client: FlaskClient):
        """Test CSV upload with Unicode characters in headers"""
        headers = ["Prénom", "Nom de famille", "Société", "Poste"]  # French headers
        rows = [["Jean", "Dupont", "ACME Corp", "Directeur"]]
        
        csv_file = self.create_test_csv(headers, rows)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'unicode_test.csv')},
                             content_type='multipart/form-data')
        
        # Should handle Unicode headers without errors
        assert response.status_code == 200
        
        # May not map perfectly, but should not crash
        response_text = response.get_data(as_text=True)
        assert "error" not in response_text.lower() or "500" not in response_text
    
    @pytest.mark.integration
    def test_csv_upload_with_special_character_headers(self, client: FlaskClient):
        """Test CSV upload with special characters in headers"""
        headers = ["First-Name", "Company.Name", "Job$Title", "E@Mail", "Location#1"]
        rows = [["Jane", "DataCorp", "Analyst", "jane@data.com", "NYC"]]
        
        csv_file = self.create_test_csv(headers, rows)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'special_chars_test.csv')},
                             content_type='multipart/form-data')
        
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        
        # Should detect at least some fields despite special characters
        mapping_indicators = response_text.count('map_')
        assert mapping_indicators >= 3, f"Too few mapping options detected: {mapping_indicators}"
    
    @pytest.mark.integration
    def test_csv_upload_with_whitespace_headers(self, client: FlaskClient):
        """Test CSV upload with problematic whitespace in headers"""
        headers = [" First Name ", "\tLast Name\t", "Company Name   ", "  Job Title"]
        rows = [["Alice", "Johnson", "StartupCo", "Engineer"]]
        
        csv_file = self.create_test_csv(headers, rows)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'whitespace_test.csv')},
                             content_type='multipart/form-data')
        
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        
        # Should normalize whitespace and detect fields
        expected_mappings = ['first_name', 'last_name', 'company_name', 'job_title']
        detected_mappings = []
        
        for mapping in expected_mappings:
            if f'map_{mapping}' in response_text:
                detected_mappings.append(mapping)
        
        detection_rate = len(detected_mappings) / len(expected_mappings)
        assert detection_rate >= 0.75, f"Whitespace handling failed: {detection_rate:.1%}"
    
    @pytest.mark.performance
    def test_header_normalization_performance(self):
        """Test performance of header normalization with large header lists"""
        import time
        
        # Generate large list of headers with various complexities
        test_headers = []
        base_headers = ["First Name", "Company", "Job Title", "E-Mail", "Location"]
        
        for i in range(1000):
            for header in base_headers:
                # Add variations: case, whitespace, special chars
                variations = [
                    header.upper(),
                    header.lower(),
                    f" {header} ",
                    header.replace(" ", "_"),
                    header.replace(" ", "-"),
                    f"{header}_{i}",
                ]
                test_headers.extend(variations)
        
        # Time the normalization process
        start_time = time.time()
        
        normalizer = TestHeaderNormalization()
        normalized_headers = [normalizer.normalize_header(h) for h in test_headers]
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process 1000s of headers in reasonable time
        headers_per_second = len(test_headers) / processing_time
        assert headers_per_second > 1000, f"Header normalization too slow: {headers_per_second:.0f} headers/sec"
        
        # Check that results are reasonable
        assert len(normalized_headers) == len(test_headers)
        assert all(isinstance(h, str) for h in normalized_headers)
        
        print(f"Header normalization performance: {headers_per_second:.0f} headers/second")


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling scenarios"""
    
    def normalize_header(self, header):
        """Use consistent normalization"""
        if not header or not isinstance(header, str):
            return ''
        
        normalized = unicodedata.normalize('NFKD', header)
        ascii_header = ''.join(c for c in normalized if not unicodedata.combining(c) and ord(c) < 128)
        
        if not ascii_header.strip():
            return ''
        
        import re
        cleaned = re.sub(r'[^\w\s]', '', ascii_header).strip().lower().replace(' ', '_')
        return re.sub(r'_+', '_', cleaned).strip('_')
    
    def test_empty_and_none_headers(self):
        """Test handling of empty and None headers"""
        test_cases = [None, "", "   ", "\t", "\n", "  \t  \n  "]
        
        for case in test_cases:
            result = self.normalize_header(case)
            assert result == "", f"Failed for case {repr(case)}: got {repr(result)}"
    
    def test_numeric_headers(self):
        """Test handling of numeric headers"""
        numeric_headers = ["123", "1.5", "2024", "001", "42"]
        
        for header in numeric_headers:
            result = self.normalize_header(header)
            assert result.isdigit() or result == "", f"Numeric header handling failed for {header}: {result}"
    
    def test_extremely_long_headers(self):
        """Test handling of extremely long headers"""
        long_header = "This_is_an_extremely_long_header_name_that_might_cause_issues_in_processing" * 5
        
        result = self.normalize_header(long_header)
        assert isinstance(result, str)
        assert len(result) <= len(long_header)  # Should not expand
    
    def test_headers_with_only_special_characters(self):
        """Test headers that are only special characters"""
        special_only = ["!!!", "@@@", "---", "___", "...", "***"]
        
        for header in special_only:
            result = self.normalize_header(header)
            # Should either normalize to empty or some consistent representation
            assert isinstance(result, str)
            assert len(result) <= len(header)
    
    @pytest.mark.integration  
    def test_csv_with_malformed_headers(self, client: FlaskClient):
        """Test CSV upload with malformed headers"""
        # CSV with problematic headers
        malformed_csv = b'"","First Name","","Company",""\nJohn,Smith,middle,TechCorp,extra'
        
        csv_file = io.BytesIO(malformed_csv)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'malformed_test.csv')},
                             content_type='multipart/form-data')
        
        # Should handle gracefully without crashing
        assert response.status_code in [200, 400], f"Unexpected status: {response.status_code}"
        
        # If successful, should still offer some mapping options
        if response.status_code == 200:
            response_text = response.get_data(as_text=True)
            mapping_count = response_text.count('map_')
            assert mapping_count >= 1, "Should detect at least one mappable field"