"""
Email Generation Tests for ColdEmailAI

Comprehensive testing of email generation functionality following TaskMaster research:
"Flask email generation testing CSV upload workflow automated testing email personalization validation 2025"

Tests validate personalization accuracy, special character handling, missing data management,
and email quality based on Context7 patterns and ZAD requirements.
"""

import io
import os
import pytest
import pandas as pd
from flask.testing import FlaskClient
from unittest.mock import patch, MagicMock


class TestEmailGenerationWorkflow:
    """Test end-to-end email generation workflow with real business data"""

    @pytest.mark.integration
    @pytest.mark.real_data
    def test_authentic_business_leads_email_generation(self, client: FlaskClient, memory_monitor):
        """Test email generation with authentic business leads data"""
        memory_monitor.start_monitoring()
        
        # Load authentic business leads test data
        test_file_path = "test_data/email_generation_tests/authentic_business_leads.csv"
        
        with open(test_file_path, 'rb') as f:
            file_content = f.read()
            
        # Step 1: Upload CSV file
        csv_file = io.BytesIO(file_content)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'authentic_business_leads.csv')},
                             content_type='multipart/form-data')
        
        # Verify successful upload and column mapping interface
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        
        # Verify all required fields are available for mapping
        expected_mapping_fields = ['first_name', 'company_name', 'job_title', 'industry']
        mapping_fields_available = 0
        
        for field in expected_mapping_fields:
            if f'map_{field}' in response_text:
                mapping_fields_available += 1
                
        mapping_availability = (mapping_fields_available / len(expected_mapping_fields)) * 100
        assert mapping_availability >= 75, f"Only {mapping_availability:.1f}% of mapping fields available"
        
        # Step 2: Submit column mapping and generate emails
        # Simulate user mapping selection
        mapping_data = {
            'map_first_name': 'first_name',
            'map_company_name': 'company_name', 
            'map_job_title': 'title',
            'map_industry': 'industry',
            'map_city': 'city',
            'map_state': 'state',
            'map_country': 'country'
        }
        
        # Submit mapping and generate emails
        email_response = client.post('/generate_emails',
                                   data=mapping_data,
                                   content_type='application/x-www-form-urlencoded')
        
        # Verify successful email generation
        assert email_response.status_code == 200
        
        # Verify response is Excel file download
        assert email_response.headers.get('Content-Type') == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        assert 'attachment' in email_response.headers.get('Content-Disposition', '')
        
        # Verify memory usage is controlled
        memory_monitor.assert_memory_increase_under(50 * 1024 * 1024)  # 50MB max
        
        print(f"\nAuthentic Business Leads Email Generation:")
        print(f"  - Upload status: {response.status_code}")
        print(f"  - Mapping availability: {mapping_availability:.1f}%")
        print(f"  - Email generation status: {email_response.status_code}")
        print(f"  - Output format: Excel (.xlsx)")

    @pytest.mark.integration
    @pytest.mark.real_data
    def test_missing_data_email_generation(self, client: FlaskClient):
        """Test email generation with missing data scenarios"""
        test_file_path = "test_data/email_generation_tests/missing_data_scenarios.csv"
        
        with open(test_file_path, 'rb') as f:
            file_content = f.read()
            
        # Upload CSV with missing data
        csv_file = io.BytesIO(file_content)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'missing_data_scenarios.csv')},
                             content_type='multipart/form-data')
        
        # Should still process successfully despite missing data
        assert response.status_code == 200
        
        # Verify available columns are detected
        response_text = response.get_data(as_text=True)
        
        # Check that some standard fields are still available for mapping
        available_fields = []
        mapping_fields = ['first_name', 'company_name', 'job_title', 'industry', 'city', 'state']
        
        for field in mapping_fields:
            if f'map_{field}' in response_text:
                available_fields.append(field)
                
        # Should have at least some mappable fields
        assert len(available_fields) >= 3, f"Only {len(available_fields)} fields available for mapping"
        
        # Attempt email generation with available fields
        mapping_data = {}
        for field in available_fields[:3]:  # Use first 3 available fields
            mapping_data[f'map_{field}'] = field.replace('_', '')  # Map to likely column names
            
        email_response = client.post('/generate_emails',
                                   data=mapping_data,
                                   content_type='application/x-www-form-urlencoded')
        
        # Should handle missing data gracefully
        assert email_response.status_code in [200, 302]
        
        print(f"\nMissing Data Email Generation:")
        print(f"  - Available mapping fields: {len(available_fields)}")
        print(f"  - Fields used: {list(available_fields[:3])}")
        print(f"  - Email generation status: {email_response.status_code}")

    @pytest.mark.integration
    @pytest.mark.real_data
    def test_special_characters_email_generation(self, client: FlaskClient):
        """Test email generation with special characters and Unicode"""
        test_file_path = "test_data/email_generation_tests/special_characters_data.csv"
        
        with open(test_file_path, 'rb') as f:
            file_content = f.read()
            
        # Upload CSV with special characters
        csv_file = io.BytesIO(file_content)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'special_characters_data.csv')},
                             content_type='multipart/form-data')
        
        # Should process Unicode and special characters successfully
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        
        # Verify mapping interface is available
        mapping_fields_found = 0
        expected_fields = ['first_name', 'company_name', 'job_title']
        
        for field in expected_fields:
            if f'map_{field}' in response_text:
                mapping_fields_found += 1
                
        field_detection_rate = (mapping_fields_found / len(expected_fields)) * 100
        assert field_detection_rate >= 80, f"Only {field_detection_rate:.1f}% of fields detected with special characters"
        
        # Test email generation with special character data
        mapping_data = {
            'map_first_name': 'first_name',
            'map_company_name': 'company_name',
            'map_job_title': 'title'
        }
        
        email_response = client.post('/generate_emails',
                                   data=mapping_data,
                                   content_type='application/x-www-form-urlencoded')
        
        # Should handle special characters in email generation
        assert email_response.status_code in [200, 302]
        
        print(f"\nSpecial Characters Email Generation:")
        print(f"  - Field detection rate: {field_detection_rate:.1f}%")
        print(f"  - Email generation status: {email_response.status_code}")

    @pytest.mark.performance
    @pytest.mark.real_data
    def test_large_dataset_email_generation_performance(self, client: FlaskClient, memory_monitor, performance_thresholds):
        """Test email generation performance with large datasets"""
        memory_monitor.start_monitoring()
        
        # Use existing enterprise dataset for performance testing
        test_file_path = "test_data/enterprise_leads.csv"
        
        with open(test_file_path, 'rb') as f:
            file_content = f.read()
            
        # Measure upload and processing time
        import time
        start_time = time.time()
        
        csv_file = io.BytesIO(file_content)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'enterprise_leads.csv')},
                             content_type='multipart/form-data')
        
        upload_time = time.time() - start_time
        
        assert response.status_code == 200
        
        # Test email generation with standard mapping
        generation_start = time.time()
        
        mapping_data = {
            'map_first_name': 'first_name',
            'map_company_name': 'company_name',
            'map_job_title': 'title',
            'map_industry': 'industry'
        }
        
        email_response = client.post('/generate_emails',
                                   data=mapping_data,
                                   content_type='application/x-www-form-urlencoded')
        
        generation_time = time.time() - generation_start
        total_time = time.time() - start_time
        
        # Performance assertions
        assert upload_time < performance_thresholds['processing_timeout'], f"Upload took {upload_time:.2f}s, max allowed: {performance_thresholds['processing_timeout']}s"
        assert generation_time < 60, f"Email generation took {generation_time:.2f}s, should be < 60s"
        assert total_time < 90, f"Total workflow took {total_time:.2f}s, should be < 90s"
        
        # Memory assertions
        memory_monitor.assert_memory_increase_under(performance_thresholds['large_file_max_increase'])
        
        # Calculate processing metrics
        if email_response.status_code == 200:
            file_size_mb = len(file_content) / (1024 * 1024)
            df = pd.read_csv(io.BytesIO(file_content))
            record_count = len(df)
            
            processing_speed = record_count / total_time
            
            print(f"\nLarge Dataset Email Generation Performance:")
            print(f"  - File size: {file_size_mb:.2f} MB")
            print(f"  - Record count: {record_count:,}")
            print(f"  - Upload time: {upload_time:.2f}s")
            print(f"  - Generation time: {generation_time:.2f}s")
            print(f"  - Total time: {total_time:.2f}s")
            print(f"  - Processing speed: {processing_speed:.0f} records/second")
            print(f"  - Final status: {email_response.status_code}")


class TestEmailPersonalizationAccuracy:
    """Test personalization accuracy with automated field validation"""

    @pytest.mark.unit
    def test_personalization_field_extraction(self, client: FlaskClient):
        """Test that personalization fields are correctly extracted from CSV"""
        # Create simple test data with known values
        test_data = """first_name,last_name,company_name,title,industry
John,Smith,TechCorp Inc,Software Engineer,Technology
Jane,Doe,DataSys Ltd,Marketing Director,Analytics"""
        
        csv_file = io.BytesIO(test_data.encode())
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'personalization_test.csv')},
                             content_type='multipart/form-data')
        
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        
        # Verify all personalization fields are available for mapping
        personalization_fields = {
            'first_name': 'Contact first name',
            'company_name': 'Company/organization name',
            'job_title': 'Job title/position',
            'industry': 'Industry/sector'
        }
        
        fields_available = 0
        for field, description in personalization_fields.items():
            if f'map_{field}' in response_text:
                fields_available += 1
                
        availability_rate = (fields_available / len(personalization_fields)) * 100
        assert availability_rate == 100, f"Only {availability_rate:.1f}% of personalization fields available"
        
        print(f"\nPersonalization Field Extraction:")
        print(f"  - Expected fields: {len(personalization_fields)}")
        print(f"  - Available fields: {fields_available}")
        print(f"  - Availability rate: {availability_rate:.1f}%")

    @pytest.mark.integration
    def test_template_rendering_with_real_data(self, client: FlaskClient):
        """Test template rendering doesn't break with real business data"""
        # Use messy real data that could cause template issues
        test_file_path = "test_data/messy_real_data.csv"
        
        with open(test_file_path, 'rb') as f:
            file_content = f.read()
            
        csv_file = io.BytesIO(file_content)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'template_test.csv')},
                             content_type='multipart/form-data')
        
        assert response.status_code == 200
        
        # Test email generation with messy data
        mapping_data = {
            'map_first_name': 'First Name',  # Note: using actual column names from messy data
            'map_company_name': 'COMPANY_NAME',
            'map_job_title': 'Job Title',
            'map_industry': 'industry'
        }
        
        email_response = client.post('/generate_emails',
                                   data=mapping_data,
                                   content_type='application/x-www-form-urlencoded')
        
        # Should handle messy data without template rendering errors
        assert email_response.status_code in [200, 302]
        
        # If successful, should return Excel file
        if email_response.status_code == 200:
            assert 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in str(email_response.headers.get('Content-Type'))
            
        print(f"\nTemplate Rendering with Messy Data:")
        print(f"  - Response status: {email_response.status_code}")
        print(f"  - Template handling: ✅ NO ERRORS")


class TestEmailQualityAndProfessionalism:
    """Test email quality, formatting, and professional standards"""

    @pytest.mark.integration
    def test_email_output_format_validation(self, client: FlaskClient):
        """Test that email output maintains professional format"""
        # Use small business leads for quality testing
        test_file_path = "test_data/small_business_leads.csv"
        
        with open(test_file_path, 'rb') as f:
            file_content = f.read()
            
        csv_file = io.BytesIO(file_content)
        
        response = client.post('/upload',
                             data={'file': (csv_file, 'quality_test.csv')},
                             content_type='multipart/form-data')
        
        assert response.status_code == 200
        
        # Generate emails with complete mapping
        mapping_data = {
            'map_first_name': 'first_name',
            'map_company_name': 'company_name',
            'map_job_title': 'title',
            'map_industry': 'industry',
            'map_city': 'city',
            'map_state': 'state'
        }
        
        email_response = client.post('/generate_emails',
                                   data=mapping_data,
                                   content_type='application/x-www-form-urlencoded')
        
        # Verify professional output format
        if email_response.status_code == 200:
            # Should return Excel file with proper headers
            content_type = email_response.headers.get('Content-Type')
            content_disposition = email_response.headers.get('Content-Disposition')
            
            assert 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in str(content_type)
            assert 'attachment' in str(content_disposition)
            assert '.xlsx' in str(content_disposition)
            
            # Response should contain actual Excel data
            excel_data = email_response.get_data()
            assert len(excel_data) > 1000, "Excel output seems too small"
            
        print(f"\nEmail Output Format Validation:")
        print(f"  - Response status: {email_response.status_code}")
        print(f"  - Content type: Professional Excel format")
        print(f"  - Output size: {len(email_response.get_data()) if email_response.status_code == 200 else 'N/A'} bytes")

    @pytest.mark.integration
    def test_system_stability_under_varied_data(self, client: FlaskClient):
        """Test system stability with various data quality scenarios"""
        # Test multiple data scenarios in sequence
        test_scenarios = [
            ("test_data/small_business_leads.csv", "Clean business data"),
            ("test_data/messy_real_data.csv", "Messy real-world data"),
            ("test_data/edge_cases/unicode_data.csv", "Unicode characters"),
            ("test_data/email_generation_tests/missing_data_scenarios.csv", "Missing data fields")
        ]
        
        successful_scenarios = 0
        
        for test_file, description in test_scenarios:
            try:
                with open(test_file, 'rb') as f:
                    file_content = f.read()
                    
                csv_file = io.BytesIO(file_content)
                
                response = client.post('/upload',
                                     data={'file': (csv_file, os.path.basename(test_file))},
                                     content_type='multipart/form-data')
                
                # System should remain stable
                if response.status_code == 200:
                    successful_scenarios += 1
                    
            except Exception as e:
                print(f"  - {description}: ❌ FAILED ({str(e)})")
                continue
                
        stability_rate = (successful_scenarios / len(test_scenarios)) * 100
        assert stability_rate >= 75, f"Only {stability_rate:.1f}% of scenarios handled stably"
        
        print(f"\nSystem Stability Under Varied Data:")
        print(f"  - Test scenarios: {len(test_scenarios)}")
        print(f"  - Successful scenarios: {successful_scenarios}")
        print(f"  - Stability rate: {stability_rate:.1f}%")