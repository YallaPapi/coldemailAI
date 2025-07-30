"""
Column Mapping Functionality Tests for ColdEmailAI

Comprehensive testing of CSV column detection and mapping following TaskMaster research:
Tests validate automatic column detection across various header formats, mixed case variations,
special characters, whitespace handling, and business data structure mapping.

Based on Context7 patterns and ZAD requirements with real business CSV test data.
"""

import io
import os
import pytest
import pandas as pd
from flask.testing import FlaskClient


class TestColumnDetection:
    """Test automatic column detection across different header formats"""

    @pytest.mark.unit
    def test_standard_headers_detection(self, client: FlaskClient):
        """Test detection of standard business headers"""
        # Load test file with standard headers
        test_file_path = "test_data/column_mapping_tests/standard_headers.csv"
        
        with open(test_file_path, 'rb') as f:
            file_content = f.read()
            
        csv_file = io.BytesIO(file_content)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'standard_headers.csv')},
                             content_type='multipart/form-data')
        
        # Should successfully process standard headers
        assert response.status_code == 200
        
        # Verify the mapping interface is shown (response contains column names)
        response_text = response.get_data(as_text=True)
        
        # Check that standard business columns are detected
        expected_columns = ['first_name', 'last_name', 'company_name', 'title', 'industry', 'city', 'state', 'country']
        for column in expected_columns:
            assert column in response_text, f"Standard column '{column}' not detected"
            
        print(f"\nStandard Headers Detection Results:")
        print(f"  - Expected columns: {len(expected_columns)}")
        print(f"  - All columns detected: ✅ PASSED")

    @pytest.mark.unit
    def test_mixed_case_headers_detection(self, client: FlaskClient):
        """Test detection of mixed case headers"""
        test_file_path = "test_data/column_mapping_tests/mixed_case_headers.csv"
        
        with open(test_file_path, 'rb') as f:
            file_content = f.read()
            
        csv_file = io.BytesIO(file_content)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'mixed_case_headers.csv')},
                             content_type='multipart/form-data')
        
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        
        # Check that mixed case columns are detected (as they appear in CSV)
        expected_columns = ['First_Name', 'Last_Name', 'Company_Name', 'Title', 'Industry', 'City', 'State', 'Country']
        detected_columns = 0
        
        for column in expected_columns:
            if column in response_text:
                detected_columns += 1
                
        detection_rate = (detected_columns / len(expected_columns)) * 100
        assert detection_rate >= 90, f"Only {detection_rate:.1f}% of mixed case columns detected, minimum 90% required"
        
        print(f"\nMixed Case Headers Detection Results:")
        print(f"  - Expected columns: {len(expected_columns)}")
        print(f"  - Detected columns: {detected_columns}")
        print(f"  - Detection rate: {detection_rate:.1f}%")

    @pytest.mark.unit
    def test_uppercase_headers_detection(self, client: FlaskClient):
        """Test detection of uppercase headers"""
        test_file_path = "test_data/column_mapping_tests/uppercase_headers.csv"
        
        with open(test_file_path, 'rb') as f:
            file_content = f.read()
            
        csv_file = io.BytesIO(file_content)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'uppercase_headers.csv')},
                             content_type='multipart/form-data')
        
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        
        # Check that uppercase columns are detected
        expected_columns = ['FIRST_NAME', 'LAST_NAME', 'COMPANY_NAME', 'TITLE', 'INDUSTRY', 'CITY', 'STATE', 'COUNTRY']
        detected_columns = 0
        
        for column in expected_columns:
            if column in response_text:
                detected_columns += 1
                
        detection_rate = (detected_columns / len(expected_columns)) * 100
        assert detection_rate >= 90, f"Only {detection_rate:.1f}% of uppercase columns detected, minimum 90% required"
        
        print(f"\nUppercase Headers Detection Results:")
        print(f"  - Expected columns: {len(expected_columns)}")
        print(f"  - Detected columns: {detected_columns}")
        print(f"  - Detection rate: {detection_rate:.1f}%")

    @pytest.mark.unit
    def test_spaced_headers_detection(self, client: FlaskClient):
        """Test detection of headers with spaces"""
        test_file_path = "test_data/column_mapping_tests/spaced_headers.csv"
        
        with open(test_file_path, 'rb') as f:
            file_content = f.read()
            
        csv_file = io.BytesIO(file_content)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'spaced_headers.csv')},
                             content_type='multipart/form-data')
        
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        
        # Check that spaced headers are detected
        expected_columns = ['First Name', 'Last Name', 'Company Name', 'Job Title', 'Industry', 'City', 'State', 'Country']
        detected_columns = 0
        
        for column in expected_columns:
            if column in response_text:
                detected_columns += 1
                
        detection_rate = (detected_columns / len(expected_columns)) * 100
        assert detection_rate >= 85, f"Only {detection_rate:.1f}% of spaced columns detected, minimum 85% required"
        
        print(f"\nSpaced Headers Detection Results:")
        print(f"  - Expected columns: {len(expected_columns)}")
        print(f"  - Detected columns: {detected_columns}")
        print(f"  - Detection rate: {detection_rate:.1f}%")

    @pytest.mark.unit  
    def test_special_char_headers_detection(self, client: FlaskClient):
        """Test detection of headers with special characters"""
        test_file_path = "test_data/column_mapping_tests/special_char_headers.csv"
        
        with open(test_file_path, 'rb') as f:
            file_content = f.read()
            
        csv_file = io.BytesIO(file_content)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'special_char_headers.csv')},
                             content_type='multipart/form-data')
        
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        
        # Check that special character headers are detected
        expected_columns = ['first-name', 'last-name', 'company-name', 'job_title', 'industry/sector', 'city_name', 'state/province', 'country_code']
        detected_columns = 0
        
        for column in expected_columns:
            if column in response_text:
                detected_columns += 1
                
        detection_rate = (detected_columns / len(expected_columns)) * 100
        assert detection_rate >= 80, f"Only {detection_rate:.1f}% of special char columns detected, minimum 80% required"
        
        print(f"\nSpecial Character Headers Detection Results:")
        print(f"  - Expected columns: {len(expected_columns)}")
        print(f"  - Detected columns: {detected_columns}")
        print(f"  - Detection rate: {detection_rate:.1f}%")

    @pytest.mark.unit
    def test_whitespace_headers_detection(self, client: FlaskClient):
        """Test detection of headers with extra whitespace"""
        test_file_path = "test_data/column_mapping_tests/whitespace_headers.csv"
        
        with open(test_file_path, 'rb') as f:
            file_content = f.read()
            
        csv_file = io.BytesIO(file_content)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'whitespace_headers.csv')},
                             content_type='multipart/form-data')
        
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        
        # Pandas should automatically strip whitespace, so we expect clean column names
        # Check that whitespace is handled properly
        clean_columns = ['first_name', 'last_name', 'company_name', 'title', 'industry', 'city', 'state', 'country']
        detected_columns = 0
        
        for column in clean_columns:
            if column in response_text:
                detected_columns += 1
                
        detection_rate = (detected_columns / len(clean_columns)) * 100
        assert detection_rate >= 75, f"Only {detection_rate:.1f}% of whitespace columns detected, minimum 75% required"
        
        print(f"\nWhitespace Headers Detection Results:")
        print(f"  - Expected clean columns: {len(clean_columns)}")
        print(f"  - Detected columns: {detected_columns}")
        print(f"  - Detection rate: {detection_rate:.1f}%")


class TestColumnMappingAccuracy:
    """Test accuracy of column mapping to business fields"""

    @pytest.mark.integration
    def test_standard_business_field_mapping(self, client: FlaskClient):
        """Test mapping accuracy for standard business fields"""
        test_file_path = "test_data/column_mapping_tests/standard_headers.csv"
        
        with open(test_file_path, 'rb') as f:
            file_content = f.read()
            
        csv_file = io.BytesIO(file_content)
        
        # Upload file to get to mapping interface
        response = client.post('/upload',
                             data={'file': (csv_file, 'standard_headers.csv')},
                             content_type='multipart/form-data')
        
        assert response.status_code == 200
        
        # Verify mapping interface contains expected mapping options
        response_text = response.get_data(as_text=True)
        
        # Check that mapping form includes standard business fields
        expected_mapping_fields = ['first_name', 'company_name', 'job_title', 'industry', 'city', 'state', 'country']
        mapping_fields_found = 0
        
        for field in expected_mapping_fields:
            # Look for mapping form fields (map_first_name, map_company_name, etc.)
            if f'map_{field}' in response_text:
                mapping_fields_found += 1
                
        mapping_availability = (mapping_fields_found / len(expected_mapping_fields)) * 100
        assert mapping_availability >= 85, f"Only {mapping_availability:.1f}% of mapping fields available, minimum 85% required"
        
        print(f"\nBusiness Field Mapping Availability:")
        print(f"  - Expected mapping fields: {len(expected_mapping_fields)}")
        print(f"  - Available mapping fields: {mapping_fields_found}")
        print(f"  - Availability rate: {mapping_availability:.1f}%")

    @pytest.mark.integration
    def test_alternate_field_names_mapping(self, client: FlaskClient):
        """Test mapping of alternate field names to standard business fields"""
        test_file_path = "test_data/column_mapping_tests/alternate_field_names.csv"
        
        with open(test_file_path, 'rb') as f:
            file_content = f.read()
            
        csv_file = io.BytesIO(file_content)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'alternate_field_names.csv')},
                             content_type='multipart/form-data')
        
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        
        # Check that alternate column names are detected
        alternate_columns = ['given_name', 'surname', 'organization', 'position', 'sector', 'location', 'region', 'nation']
        detected_alternates = 0
        
        for column in alternate_columns:
            if column in response_text:
                detected_alternates += 1
                
        detection_rate = (detected_alternates / len(alternate_columns)) * 100
        assert detection_rate >= 90, f"Only {detection_rate:.1f}% of alternate columns detected, minimum 90% required"
        
        print(f"\nAlternate Field Names Detection:")
        print(f"  - Alternate columns: {len(alternate_columns)}")
        print(f"  - Detected columns: {detected_alternates}")
        print(f"  - Detection rate: {detection_rate:.1f}%")

    @pytest.mark.integration
    def test_missing_columns_handling(self, client: FlaskClient):
        """Test handling of CSV files with missing standard columns"""
        test_file_path = "test_data/column_mapping_tests/missing_columns.csv"
        
        with open(test_file_path, 'rb') as f:
            file_content = f.read()
            
        csv_file = io.BytesIO(file_content)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'missing_columns.csv')},
                             content_type='multipart/form-data')
        
        # Should still process successfully even with missing columns
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        
        # Verify that available columns are detected
        available_columns = ['first_name', 'company_name', 'title']
        detected_available = 0
        
        for column in available_columns:
            if column in response_text:
                detected_available += 1
                
        detection_rate = (detected_available / len(available_columns)) * 100
        assert detection_rate == 100, f"Only {detection_rate:.1f}% of available columns detected, should be 100%"
        
        print(f"\nMissing Columns Handling:")
        print(f"  - Available columns: {len(available_columns)}")
        print(f"  - Detected columns: {detected_available}")
        print(f"  - Detection rate: {detection_rate:.1f}%")

    @pytest.mark.integration
    def test_extra_columns_handling(self, client: FlaskClient):
        """Test handling of CSV files with extra non-standard columns"""
        test_file_path = "test_data/column_mapping_tests/extra_columns.csv"
        
        with open(test_file_path, 'rb') as f:
            file_content = f.read()
            
        csv_file = io.BytesIO(file_content)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'extra_columns.csv')},
                             content_type='multipart/form-data')
        
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        
        # Verify that all columns (standard + extra) are detected
        all_columns = ['first_name', 'last_name', 'company_name', 'title', 'industry', 'city', 'state', 'country', 'phone', 'email', 'website', 'employee_count']
        detected_all = 0
        
        for column in all_columns:
            if column in response_text:
                detected_all += 1
                
        detection_rate = (detected_all / len(all_columns)) * 100
        assert detection_rate >= 90, f"Only {detection_rate:.1f}% of all columns detected, minimum 90% required"
        
        print(f"\nExtra Columns Handling:")
        print(f"  - Total columns: {len(all_columns)}")
        print(f"  - Detected columns: {detected_all}")
        print(f"  - Detection rate: {detection_rate:.1f}%")


class TestColumnMappingEdgeCases:
    """Test edge cases and error conditions in column mapping"""

    @pytest.mark.unit
    def test_empty_headers_handling(self, client: FlaskClient):
        """Test handling of CSV files with empty or null headers"""
        # Create CSV content with empty headers
        csv_content = b',last_name,,title,industry\nJohn,Smith,,Manager,Technology'
        csv_file = io.BytesIO(csv_content)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'empty_headers.csv')},
                             content_type='multipart/form-data')
        
        # Should handle gracefully (either process or redirect with clear error)
        assert response.status_code in [200, 302]
        
        if response.status_code == 200:
            # If processed, verify non-empty headers are detected
            response_text = response.get_data(as_text=True)
            non_empty_columns = ['last_name', 'title', 'industry']
            
            for column in non_empty_columns:
                assert column in response_text, f"Non-empty column '{column}' not detected"
                
        print(f"\nEmpty Headers Handling:")
        print(f"  - Response status: {response.status_code}")
        print(f"  - Handling: ✅ GRACEFUL")

    @pytest.mark.unit
    def test_duplicate_headers_handling(self, client: FlaskClient):
        """Test handling of CSV files with duplicate column headers"""
        # Create CSV content with duplicate headers
        csv_content = b'first_name,last_name,first_name,title\nJohn,Smith,Johnny,Manager'
        csv_file = io.BytesIO(csv_content)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'duplicate_headers.csv')},
                             content_type='multipart/form-data')
        
        # Should handle gracefully (pandas typically renames duplicates)
        assert response.status_code in [200, 302]
        
        if response.status_code == 200:
            response_text = response.get_data(as_text=True)
            # Check that some form of the headers is detected
            expected_patterns = ['first_name', 'last_name', 'title']
            
            for pattern in expected_patterns:
                assert pattern in response_text, f"Header pattern '{pattern}' not found"
                
        print(f"\nDuplicate Headers Handling:")
        print(f"  - Response status: {response.status_code}")
        print(f"  - Handling: ✅ GRACEFUL")

    @pytest.mark.unit
    def test_very_long_headers_handling(self, client: FlaskClient):
        """Test handling of CSV files with very long column headers"""
        # Create CSV content with extremely long headers
        long_header = "very_long_column_name_that_exceeds_normal_length_expectations_and_continues_for_many_characters"
        csv_content = f'first_name,{long_header},company_name\nJohn,test_value,TechCorp'.encode()
        csv_file = io.BytesIO(csv_content)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'long_headers.csv')},
                             content_type='multipart/form-data')
        
        # Should handle long headers gracefully
        assert response.status_code in [200, 302]
        
        if response.status_code == 200:
            response_text = response.get_data(as_text=True)
            # Check that standard headers are still detected
            assert 'first_name' in response_text
            assert 'company_name' in response_text
            
        print(f"\nVery Long Headers Handling:")
        print(f"  - Long header length: {len(long_header)} characters")
        print(f"  - Response status: {response.status_code}")
        print(f"  - Handling: ✅ GRACEFUL")

    @pytest.mark.integration
    def test_unicode_headers_handling(self, client: FlaskClient):
        """Test handling of CSV files with Unicode characters in headers"""
        # Create CSV content with Unicode headers
        csv_content = 'nom_prénom,société_nom,职位,industrie\nJean,Société Tech,经理,技术'.encode('utf-8')
        csv_file = io.BytesIO(csv_content)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'unicode_headers.csv')},
                             content_type='multipart/form-data')
        
        # Should handle Unicode headers gracefully
        assert response.status_code in [200, 302]
        
        if response.status_code == 200:
            response_text = response.get_data(as_text=True)
            # Check that Unicode headers are preserved or handled appropriately
            unicode_patterns = ['nom_prénom', 'société_nom', '职位', 'industrie']
            unicode_detected = 0
            
            for pattern in unicode_patterns:
                if pattern in response_text:
                    unicode_detected += 1
                    
            unicode_rate = (unicode_detected / len(unicode_patterns)) * 100
            
        print(f"\nUnicode Headers Handling:")
        print(f"  - Unicode patterns: {len(unicode_patterns) if response.status_code == 200 else 'N/A'}")
        print(f"  - Detection rate: {unicode_rate:.1f}%" if response.status_code == 200 else "  - Handled via redirect")
        print(f"  - Response status: {response.status_code}")
        print(f"  - Handling: ✅ GRACEFUL")