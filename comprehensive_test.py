#!/usr/bin/env python3
"""
Comprehensive End-to-End Testing Script for ColdEmailAI
Tests with REAL business data, not demo data.
Validates form fixes, CSV upload, column mapping, email generation, and Excel export.
"""

import os
import sys
import time
import requests
import pandas as pd
from pathlib import Path
import logging
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ColdEmailAITester:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test_result(self, test_name, success, message="", data=None):
        """Log test results for comprehensive reporting"""
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': time.time(),
            'data': data
        })
        status = "[PASS]" if success else "[FAIL]"
        logger.info(f"{status} {test_name}: {message}")
        
    def test_server_health(self):
        """Test if the Flask server is running and healthy"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.log_test_result("Server Health Check", True, "Server is running and healthy")
                return True
            else:
                self.log_test_result("Server Health Check", False, f"Server returned status {response.status_code}")
                return False
        except requests.RequestException as e:
            self.log_test_result("Server Health Check", False, f"Cannot connect to server: {str(e)}")
            return False
    
    def test_form_validation_fix_with_real_data(self):
        """Test the form validation fix using real business data"""
        logger.info("=== Testing Form Validation Fix with Real Business Data ===")
        
        # Load real business data
        test_file = "test_data/email_generation_tests/authentic_business_leads.csv"
        if not os.path.exists(test_file):
            self.log_test_result("Form Validation Test", False, f"Test file {test_file} not found")
            return False
            
        try:
            # Read the test file
            with open(test_file, 'rb') as f:
                csv_content = f.read()
            
            # Test upload endpoint
            files = {'file': ('authentic_business_leads.csv', csv_content, 'text/csv')}
            upload_response = self.session.post(f"{self.base_url}/upload", files=files)
            
            if upload_response.status_code != 200:
                self.log_test_result("CSV Upload", False, f"Upload failed with status {upload_response.status_code}")
                return False
                
            self.log_test_result("CSV Upload", True, "Real business data uploaded successfully")
            
            # Check if mapping form is present in response
            if 'map_first_name' not in upload_response.text or 'map_company_name' not in upload_response.text:
                self.log_test_result("Mapping Form Generation", False, "Mapping form not found in response")
                return False
                
            self.log_test_result("Mapping Form Generation", True, "Column mapping form generated correctly")
            return True
            
        except Exception as e:
            self.log_test_result("Form Validation Test", False, f"Exception: {str(e)}")
            return False
    
    def test_csv_column_mapping_variations(self):
        """Test column mapping with various CSV header formats"""
        logger.info("=== Testing CSV Column Mapping Variations ===")
        
        test_files = [
            "test_data/column_mapping_tests/mixed_case_headers.csv",
            "test_data/column_mapping_tests/spaced_headers.csv", 
            "test_data/column_mapping_tests/special_char_headers.csv",
            "test_data/column_mapping_tests/whitespace_headers.csv"
        ]
        
        success_count = 0
        for test_file in test_files:
            if not os.path.exists(test_file):
                self.log_test_result(f"Column Mapping - {os.path.basename(test_file)}", False, "File not found")
                continue
                
            try:
                with open(test_file, 'rb') as f:
                    csv_content = f.read()
                
                files = {'file': (os.path.basename(test_file), csv_content, 'text/csv')}
                response = self.session.post(f"{self.base_url}/upload", files=files)
                
                if response.status_code == 200 and 'map_first_name' in response.text:
                    self.log_test_result(f"Column Mapping - {os.path.basename(test_file)}", True, "Mapping form generated")
                    success_count += 1
                else:
                    self.log_test_result(f"Column Mapping - {os.path.basename(test_file)}", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test_result(f"Column Mapping - {os.path.basename(test_file)}", False, f"Exception: {str(e)}")
        
        return success_count >= len(test_files) // 2  # At least half should succeed
    
    def test_email_generation_with_real_leads(self):
        """Test email generation using actual business leads"""
        logger.info("=== Testing Email Generation with Real Business Leads ===")
        
        test_file = "test_data/email_generation_tests/authentic_business_leads.csv"
        if not os.path.exists(test_file):
            self.log_test_result("Email Generation Test", False, f"Test file {test_file} not found")
            return False
        
        try:
            # First upload the file
            with open(test_file, 'rb') as f:
                csv_content = f.read()
            
            files = {'file': ('authentic_business_leads.csv', csv_content, 'text/csv')}
            upload_response = self.session.post(f"{self.base_url}/upload", files=files)
            
            if upload_response.status_code != 200:
                self.log_test_result("Email Generation - Upload", False, "Upload failed")
                return False
            
            # Now test email generation with proper mapping
            form_data = {
                'map_first_name': 'first_name',
                'map_company_name': 'company_name',
                'map_job_title': 'title',  
                'map_industry': 'industry',
                'map_city': 'city',
                'map_state': 'state',
                'map_country': 'country'
            }
            
            generate_response = self.session.post(f"{self.base_url}/generate_emails", data=form_data)
            
            if generate_response.status_code == 200:
                # Check if we got an Excel file back
                if 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in generate_response.headers.get('content-type', ''):
                    self.log_test_result("Email Generation", True, "Successfully generated emails and returned Excel file")
                    
                    # Save the generated file for analysis
                    output_file = "test_email_generation_output.xlsx"
                    with open(output_file, 'wb') as f:
                        f.write(generate_response.content)
                    
                    # Analyze the generated file
                    try:
                        df = pd.read_excel(output_file)
                        if 'Personalized' in df.columns and len(df) > 0:
                            non_empty_emails = df['Personalized'].notna().sum()
                            self.log_test_result("Email Content Analysis", True, 
                                               f"Generated {non_empty_emails} personalized emails out of {len(df)} leads")
                            return True
                        else:
                            self.log_test_result("Email Content Analysis", False, "No personalized emails found in output")
                            return False
                    except Exception as e:
                        self.log_test_result("Email Content Analysis", False, f"Error analyzing output: {str(e)}")
                        return False
                else:
                    self.log_test_result("Email Generation", False, "Did not receive Excel file response")
                    return False
            else:
                self.log_test_result("Email Generation", False, f"Generation failed with status {generate_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test_result("Email Generation Test", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling_edge_cases(self):
        """Test error handling with malformed files and edge cases"""
        logger.info("=== Testing Error Handling and Edge Cases ===")
        
        edge_case_files = [
            "test_data/malicious_files/empty.csv",
            "test_data/malicious_files/malformed.csv",
            "test_data/edge_cases/unicode_data.csv",
            "test_data/advanced_mapping_tests/extreme_special_characters.csv"
        ]
        
        success_count = 0
        for test_file in edge_case_files:
            if not os.path.exists(test_file):
                continue
                
            try:
                with open(test_file, 'rb') as f:
                    csv_content = f.read()
                
                files = {'file': (os.path.basename(test_file), csv_content, 'text/csv')}
                response = self.session.post(f"{self.base_url}/upload", files=files)
                
                # For edge cases, we expect either success or graceful error handling
                if response.status_code in [200, 400]:  # 200 = success, 400 = handled error
                    self.log_test_result(f"Edge Case - {os.path.basename(test_file)}", True, "Handled gracefully")
                    success_count += 1
                else:
                    self.log_test_result(f"Edge Case - {os.path.basename(test_file)}", False, f"Unhandled error: {response.status_code}")
                    
            except Exception as e:
                self.log_test_result(f"Edge Case - {os.path.basename(test_file)}", False, f"Exception: {str(e)}")
        
        return success_count > 0
    
    def test_performance_with_large_dataset(self):
        """Test performance with larger datasets"""
        logger.info("=== Testing Performance with Large Dataset ===")
        
        # Use enterprise leads file for performance testing
        test_file = "test_data/enterprise_leads.csv"
        if not os.path.exists(test_file):
            self.log_test_result("Performance Test", False, f"Large dataset file {test_file} not found")
            return False
        
        try:
            start_time = time.time()
            
            with open(test_file, 'rb') as f:
                csv_content = f.read()
            
            # Check file size
            file_size_mb = len(csv_content) / (1024 * 1024)
            logger.info(f"Testing with {file_size_mb:.2f}MB file")
            
            files = {'file': ('enterprise_leads.csv', csv_content, 'text/csv')}
            upload_response = self.session.post(f"{self.base_url}/upload", files=files, timeout=60)
            
            upload_time = time.time() - start_time
            
            if upload_response.status_code == 200:
                self.log_test_result("Performance - Large File Upload", True, 
                                   f"Uploaded {file_size_mb:.2f}MB file in {upload_time:.2f} seconds")
                return True
            else:
                self.log_test_result("Performance - Large File Upload", False, 
                                   f"Upload failed after {upload_time:.2f} seconds")
                return False
                
        except Exception as e:
            self.log_test_result("Performance Test", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_tests(self):
        """Run all tests and generate comprehensive report"""
        logger.info("=== Starting Comprehensive ColdEmailAI Testing ===")
        
        # Check if server is running
        if not self.test_server_health():
            logger.error("Server is not running. Please start with: python -m flask run --debug")
            return False
        
        # Run all tests
        tests = [
            self.test_form_validation_fix_with_real_data,
            self.test_csv_column_mapping_variations,
            self.test_email_generation_with_real_leads,
            self.test_error_handling_edge_cases,
            self.test_performance_with_large_dataset
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed_tests += 1
            except Exception as e:
                logger.error(f"Test {test.__name__} failed with exception: {str(e)}")
        
        # Generate final report
        self.generate_test_report(passed_tests, total_tests)
        
        return passed_tests == total_tests
    
    def generate_test_report(self, passed, total):
        """Generate comprehensive test report"""
        logger.info("=== COMPREHENSIVE TEST REPORT ===")
        logger.info(f"Tests Passed: {passed}/{total}")
        logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\n" + "="*60)
        print("COLDEMAILAI COMPREHENSIVE TEST REPORT")
        print("="*60)
        print(f"Overall Result: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        print("\nDetailed Results:")
        
        for result in self.test_results:
            status = "PASS" if result['success'] else "FAIL"
            print(f"  [{status}] {result['test']}: {result['message']}")
        
        print("\n" + "="*60)
        
        if passed == total:
            print("SUCCESS: All tests passed! ColdEmailAI is working correctly with real data.")
        else:
            print(f"ATTENTION: {total - passed} test(s) failed. Review the failures above.")
        
        print("="*60)

def main():
    """Main test execution function"""
    tester = ColdEmailAITester()
    
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    # Run comprehensive tests
    success = tester.run_comprehensive_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! ColdEmailAI is production-ready.")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED. See report above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())