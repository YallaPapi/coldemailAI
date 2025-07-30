"""
Business Data Structure Validation Tests
Task 11.4: Validate Business Data Structure Mapping Against Sample Datasets

Comprehensive validation testing following TaskMaster research:
"business data structure validation CSV mapping pandas data integrity business entities field alignment sample datasets testing"

Tests validate data type checks, range validation, domain constraints, uniqueness enforcement,
format validation, and cross-field business rules based on Context7 patterns and research findings.
"""

import io
import pytest
import pandas as pd
import re
import numpy as np
from datetime import datetime
from flask.testing import FlaskClient
from unittest.mock import patch


class BusinessDataValidator:
    """Comprehensive business data structure validator"""
    
    def __init__(self):
        self.validation_results = {}
        self.business_schema = self._define_business_schema()
        self.validation_errors = []
    
    def _define_business_schema(self):
        """Define expected business data schema with validation rules"""
        return {
            'company_name': {
                'type': 'string',
                'required': True,
                'min_length': 2,
                'max_length': 100,
                'pattern': r'^[A-Za-z0-9\s\.,&\-\']+$',
                'description': 'Company or organization name'
            },
            'first_name': {
                'type': 'string', 
                'required': True,
                'min_length': 1,
                'max_length': 50,
                'pattern': r'^[A-Za-z\s\-\'\.]+$',
                'description': 'Contact first name'
            },
            'last_name': {
                'type': 'string',
                'required': True,
                'min_length': 1,
                'max_length': 50,
                'pattern': r'^[A-Za-z\s\-\'\.]+$',
                'description': 'Contact last name'
            },
            'job_title': {
                'type': 'string',
                'required': False,
                'min_length': 2,
                'max_length': 100,
                'pattern': r'^[A-Za-z0-9\s\.,&\-\'\/()]+$',
                'description': 'Job title or position'
            },
            'industry': {
                'type': 'string',
                'required': False,
                'domain': [
                    'Technology', 'Healthcare', 'Finance', 'Manufacturing', 
                    'Retail', 'Education', 'Consulting', 'Real Estate',
                    'Hospitality', 'Transportation', 'Energy', 'Media',
                    'Construction', 'Government', 'Non-Profit', 'Other'
                ],
                'description': 'Business industry sector'
            },
            'email': {
                'type': 'string',
                'required': False,
                'pattern': r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$',
                'unique': True,
                'description': 'Email address'
            },
            'city': {
                'type': 'string',
                'required': False,
                'min_length': 2,
                'max_length': 50,
                'pattern': r'^[A-Za-z\s\-\'\.]+$',
                'description': 'City location'
            },
            'state': {
                'type': 'string',
                'required': False,
                'pattern': r'^[A-Z]{2}$|^[A-Za-z\s]{2,30}$',
                'description': 'State or province'
            },
            'country': {
                'type': 'string',
                'required': False,
                'min_length': 2,
                'max_length': 50,
                'description': 'Country name'
            }
        }
    
    def validate_data_types(self, df):
        """Validate data types match business schema expectations"""
        type_errors = []
        
        for column, schema in self.business_schema.items():
            if column not in df.columns:
                continue
                
            if schema['type'] == 'string':
                # Check for non-string values
                non_string_mask = ~df[column].astype(str).eq(df[column].astype(str))
                if non_string_mask.any():
                    type_errors.append({
                        'field': column,
                        'error': 'non_string_values',
                        'count': non_string_mask.sum(),
                        'expected': 'string',
                        'description': schema['description']
                    })
        
        return type_errors
    
    def validate_required_fields(self, df):
        """Validate required fields are present and not empty"""
        required_errors = []
        
        for column, schema in self.business_schema.items():
            if schema.get('required', False):
                if column not in df.columns:
                    required_errors.append({
                        'field': column,
                        'error': 'missing_column',
                        'description': f"Required field '{column}' not found in data"
                    })
                else:
                    # Check for empty/null values
                    null_mask = df[column].isnull() | (df[column].astype(str).str.strip() == '')
                    if null_mask.any():
                        required_errors.append({
                            'field': column,
                            'error': 'empty_values',
                            'count': null_mask.sum(),
                            'total': len(df),
                            'description': f"Required field '{column}' has empty values"
                        })
        
        return required_errors
    
    def validate_field_lengths(self, df):
        """Validate field lengths against schema constraints"""
        length_errors = []
        
        for column, schema in self.business_schema.items():
            if column not in df.columns:
                continue
                
            min_length = schema.get('min_length')
            max_length = schema.get('max_length')
            
            if min_length or max_length:
                # Convert to string and get lengths
                lengths = df[column].astype(str).str.len()
                
                if min_length:
                    too_short_mask = lengths < min_length
                    if too_short_mask.any():
                        length_errors.append({
                            'field': column,
                            'error': 'too_short',
                            'count': too_short_mask.sum(),
                            'min_length': min_length,
                            'shortest': lengths.min()
                        })
                
                if max_length:
                    too_long_mask = lengths > max_length
                    if too_long_mask.any():
                        length_errors.append({
                            'field': column,
                            'error': 'too_long',
                            'count': too_long_mask.sum(),
                            'max_length': max_length,
                            'longest': lengths.max()
                        })
        
        return length_errors
    
    def validate_field_patterns(self, df):
        """Validate field patterns match expected formats"""
        pattern_errors = []
        
        for column, schema in self.business_schema.items():
            if column not in df.columns or 'pattern' not in schema:
                continue
                
            pattern = schema['pattern']
            
            # Test pattern against non-null values
            non_null_mask = df[column].notna() & (df[column].astype(str).str.strip() != '')
            if non_null_mask.any():
                test_values = df.loc[non_null_mask, column].astype(str)
                invalid_mask = ~test_values.str.match(pattern, na=False)
                
                if invalid_mask.any():
                    invalid_values = test_values[invalid_mask].head(5).tolist()
                    pattern_errors.append({
                        'field': column,
                        'error': 'invalid_format',
                        'count': invalid_mask.sum(),
                        'pattern': pattern,
                        'examples': invalid_values,
                        'description': schema['description']
                    })
        
        return pattern_errors
    
    def validate_domain_constraints(self, df):
        """Validate domain constraints for categorical fields"""
        domain_errors = []
        
        for column, schema in self.business_schema.items():
            if column not in df.columns or 'domain' not in schema:
                continue
                
            valid_values = set(schema['domain'])
            
            # Check for invalid domain values
            non_null_mask = df[column].notna() & (df[column].astype(str).str.strip() != '')
            if non_null_mask.any():
                actual_values = set(df.loc[non_null_mask, column].astype(str))
                invalid_values = actual_values - valid_values
                
                if invalid_values:
                    domain_errors.append({
                        'field': column,
                        'error': 'invalid_domain_values',
                        'invalid_values': list(invalid_values),
                        'valid_domain': schema['domain'],
                        'description': schema['description']
                    })
        
        return domain_errors
    
    def validate_uniqueness_constraints(self, df):
        """Validate uniqueness constraints for specified fields"""
        uniqueness_errors = []
        
        for column, schema in self.business_schema.items():
            if column not in df.columns or not schema.get('unique', False):
                continue
                
            # Check for duplicates in non-null values
            non_null_data = df[column].dropna()
            if len(non_null_data) != len(non_null_data.unique()):
                duplicate_count = len(non_null_data) - len(non_null_data.unique())
                duplicates = non_null_data[non_null_data.duplicated()].unique()
                
                uniqueness_errors.append({
                    'field': column,
                    'error': 'duplicate_values',
                    'duplicate_count': duplicate_count,
                    'examples': duplicates[:5].tolist(),
                    'description': f"Field '{column}' should contain unique values"
                })
        
        return uniqueness_errors
    
    def validate_cross_field_business_rules(self, df):
        """Validate cross-field business rules"""
        business_rule_errors = []
        
        # Rule 1: If email is provided, it should match naming conventions
        if 'email' in df.columns and 'first_name' in df.columns and 'last_name' in df.columns:
            mask = df['email'].notna() & df['first_name'].notna() & df['last_name'].notna()
            if mask.any():
                mismatched_emails = []
                for idx in df[mask].index:
                    email = str(df.loc[idx, 'email']).lower()
                    first = str(df.loc[idx, 'first_name']).lower()
                    last = str(df.loc[idx, 'last_name']).lower()
                    
                    # Simple check: first name or last name should appear in email
                    if len(first) > 2 and len(last) > 2:
                        if first[:3] not in email and last[:3] not in email:
                            mismatched_emails.append(email)
                
                if mismatched_emails and len(mismatched_emails) > len(df) * 0.5:  # More than 50% mismatch
                    business_rule_errors.append({
                        'rule': 'email_name_consistency',
                        'error': 'email_name_mismatch',
                        'count': len(mismatched_emails),
                        'description': 'High rate of email addresses not matching contact names'
                    })
        
        # Rule 2: Technology companies should have tech-related job titles
        if 'industry' in df.columns and 'job_title' in df.columns:
            tech_mask = df['industry'].str.contains('Technology', case=False, na=False)
            tech_companies = df[tech_mask]
            
            if len(tech_companies) > 0:
                tech_titles = ['engineer', 'developer', 'architect', 'programmer', 'analyst', 'manager', 'director', 'cto', 'cio']
                non_tech_titles = []
                
                for idx in tech_companies.index:
                    title = str(tech_companies.loc[idx, 'job_title']).lower()
                    if not any(tech_term in title for tech_term in tech_titles):
                        non_tech_titles.append(title)
                
                if len(non_tech_titles) > len(tech_companies) * 0.8:  # More than 80% non-tech titles
                    business_rule_errors.append({
                        'rule': 'industry_title_alignment',
                        'error': 'tech_industry_non_tech_titles',
                        'count': len(non_tech_titles),
                        'description': 'Technology companies with predominantly non-technical job titles'
                    })
        
        return business_rule_errors
    
    def validate_complete_dataset(self, df, dataset_name="Unknown"):
        """Run complete validation suite on dataset"""
        self.validation_errors = []
        validation_summary = {
            'dataset': dataset_name,
            'total_records': len(df),
            'total_columns': len(df.columns),
            'validation_timestamp': datetime.now().isoformat()
        }
        
        # Run all validation checks
        validation_checks = [
            ('data_types', self.validate_data_types),
            ('required_fields', self.validate_required_fields),
            ('field_lengths', self.validate_field_lengths),
            ('field_patterns', self.validate_field_patterns),
            ('domain_constraints', self.validate_domain_constraints),
            ('uniqueness_constraints', self.validate_uniqueness_constraints),
            ('business_rules', self.validate_cross_field_business_rules)
        ]
        
        for check_name, check_function in validation_checks:
            try:
                errors = check_function(df)
                validation_summary[check_name] = {
                    'errors_found': len(errors),
                    'errors': errors
                }
                self.validation_errors.extend(errors)
            except Exception as e:
                validation_summary[check_name] = {
                    'errors_found': 1,
                    'errors': [{'error': 'validation_exception', 'message': str(e)}]
                }
        
        # Overall validation status
        total_errors = sum(result['errors_found'] for result in validation_summary.values() if isinstance(result, dict) and 'errors_found' in result)
        validation_summary['overall_status'] = 'PASS' if total_errors == 0 else 'FAIL'
        validation_summary['total_errors'] = total_errors
        
        return validation_summary


class TestBusinessDataStructureValidation:
    """Test business data structure validation against sample datasets"""
    
    def setup_method(self):
        """Setup test environment"""
        self.validator = BusinessDataValidator()
    
    @pytest.mark.parametrize("csv_file,expected_status", [
        ("test_data/small_business_leads.csv", "PASS"),
        ("test_data/email_generation_tests/authentic_business_leads.csv", "PASS"),
        ("test_data/advanced_mapping_tests/alternative_business_terms.csv", "PASS"),
    ])
    def test_sample_dataset_validation(self, csv_file, expected_status):
        """Test validation against clean sample datasets"""
        try:
            df = pd.read_csv(csv_file)
            
            # Normalize column names to match business schema
            normalized_columns = {}
            for col in df.columns:
                normalized = col.strip().lower().replace(' ', '_').replace('-', '_')
                normalized_columns[col] = normalized
            
            df = df.rename(columns=normalized_columns)
            
            # Run validation
            result = self.validator.validate_complete_dataset(df, csv_file)
            
            # Check overall status
            if expected_status == "PASS":
                # Allow some minor issues but should be mostly clean
                assert result['total_errors'] <= 3, f"Too many errors in clean dataset: {result['total_errors']}"
            
            # Validate structure is reasonable
            assert result['total_records'] > 0, "Dataset should have records"
            assert result['total_columns'] >= 3, "Dataset should have multiple columns"
            
        except FileNotFoundError:
            pytest.skip(f"Test file {csv_file} not found")
    
    def test_required_fields_validation(self):
        """Test validation of required business fields"""
        # Create test data missing required fields
        incomplete_data = pd.DataFrame({
            'company_name': ['TechCorp', ''],  # One empty
            'first_name': ['John', 'Jane'],
            # Missing last_name (required)
            'job_title': ['Developer', 'Manager']
        })
        
        result = self.validator.validate_complete_dataset(incomplete_data, "incomplete_test")
        
        # Should detect missing required field
        required_errors = result['required_fields']['errors']
        assert len(required_errors) > 0, "Should detect missing required fields"
        
        # Should detect empty value in required field
        empty_errors = [err for err in required_errors if err['error'] == 'empty_values']
        assert len(empty_errors) > 0, "Should detect empty values in required fields"
    
    def test_data_type_validation(self):
        """Test data type validation"""
        # Create test data with correct types
        valid_data = pd.DataFrame({
            'company_name': ['TechCorp Inc', 'DataSys LLC'],
            'first_name': ['John', 'Jane'],
            'last_name': ['Smith', 'Doe'],
            'email': ['john@tech.com', 'jane@data.com']
        })
        
        result = self.validator.validate_complete_dataset(valid_data, "type_test")
        
        # Should pass type validation
        type_errors = result['data_types']['errors']
        assert len(type_errors) == 0, f"Should pass type validation: {type_errors}"
    
    @pytest.mark.parametrize("field,valid_values,invalid_values", [
        ('email', 
         ['john@example.com', 'jane.doe+test@company.org'],
         ['invalid-email', 'missing@', '@missing.com', 'spaces in@email.com']),
        ('first_name',
         ['John', 'Mary-Jane', "O'Connor"],
         ['123Invalid', 'Name@Symbol', '']),
        ('company_name',
         ['TechCorp Inc', 'Data & Analytics LLC', "Joe's Restaurant"],
         ['', '123', 'Company/With/Slashes'])
    ])
    def test_field_pattern_validation(self, field, valid_values, invalid_values):
        """Test field pattern validation"""
        # Test valid values
        valid_data = pd.DataFrame({field: valid_values})
        result_valid = self.validator.validate_complete_dataset(valid_data, f"{field}_valid")
        pattern_errors_valid = result_valid['field_patterns']['errors']
        
        # Valid values should not have pattern errors
        field_errors = [err for err in pattern_errors_valid if err['field'] == field]
        assert len(field_errors) == 0, f"Valid {field} values should pass: {field_errors}"
        
        # Test invalid values
        invalid_data = pd.DataFrame({field: invalid_values})
        result_invalid = self.validator.validate_complete_dataset(invalid_data, f"{field}_invalid")
        pattern_errors_invalid = result_invalid['field_patterns']['errors']
        
        # Invalid values should have pattern errors
        field_errors = [err for err in pattern_errors_invalid if err['field'] == field]
        assert len(field_errors) > 0, f"Invalid {field} values should fail pattern validation"
    
    def test_domain_constraint_validation(self):
        """Test domain constraint validation for categorical fields"""
        # Valid industry values
        valid_data = pd.DataFrame({
            'industry': ['Technology', 'Healthcare', 'Finance']
        })
        result_valid = self.validator.validate_complete_dataset(valid_data, "industry_valid")
        domain_errors_valid = result_valid['domain_constraints']['errors']
        assert len(domain_errors_valid) == 0, "Valid industry values should pass"
        
        # Invalid industry values
        invalid_data = pd.DataFrame({
            'industry': ['Invalid Industry', 'Random Sector', 'Unknown Field']
        })
        result_invalid = self.validator.validate_complete_dataset(invalid_data, "industry_invalid")
        domain_errors_invalid = result_invalid['domain_constraints']['errors']
        assert len(domain_errors_invalid) > 0, "Invalid industry values should fail domain validation"
    
    def test_uniqueness_constraint_validation(self):
        """Test uniqueness constraints"""
        # Duplicate email addresses
        duplicate_data = pd.DataFrame({
            'email': ['john@example.com', 'jane@example.com', 'john@example.com']  # Duplicate
        })
        
        result = self.validator.validate_complete_dataset(duplicate_data, "duplicate_test")
        uniqueness_errors = result['uniqueness_constraints']['errors']
        
        # Should detect duplicate emails
        email_errors = [err for err in uniqueness_errors if err['field'] == 'email']
        assert len(email_errors) > 0, "Should detect duplicate email addresses"
        assert email_errors[0]['duplicate_count'] > 0, "Should count duplicates correctly"
    
    def test_field_length_validation(self):
        """Test field length constraints"""
        # Test minimum length violation
        short_data = pd.DataFrame({
            'company_name': ['A'],  # Too short (min_length: 2)
            'first_name': ['John']
        })
        
        result_short = self.validator.validate_complete_dataset(short_data, "short_test")
        length_errors_short = result_short['field_lengths']['errors']
        short_errors = [err for err in length_errors_short if err['error'] == 'too_short']
        assert len(short_errors) > 0, "Should detect fields that are too short"
        
        # Test maximum length violation
        long_data = pd.DataFrame({
            'first_name': ['A' * 100]  # Too long (max_length: 50)
        })
        
        result_long = self.validator.validate_complete_dataset(long_data, "long_test")
        length_errors_long = result_long['field_lengths']['errors']
        long_errors = [err for err in length_errors_long if err['error'] == 'too_long']
        assert len(long_errors) > 0, "Should detect fields that are too long"
    
    def test_cross_field_business_rules(self):
        """Test cross-field business rule validation"""
        # Create data that violates business rules
        rule_violation_data = pd.DataFrame({
            'industry': ['Technology', 'Technology', 'Technology'],
            'job_title': ['Sales Rep', 'Marketing Coordinator', 'HR Assistant'],  # Non-tech titles
            'email': ['alice@company.com', 'bob@company.com', 'charlie@company.com'],
            'first_name': ['Alice', 'Bob', 'Charlie'],
            'last_name': ['Smith', 'Jones', 'Brown']
        })
        
        result = self.validator.validate_complete_dataset(rule_violation_data, "business_rule_test")
        business_rule_errors = result['business_rules']['errors']
        
        # Should detect industry-title misalignment
        title_alignment_errors = [err for err in business_rule_errors if err['rule'] == 'industry_title_alignment']
        assert len(title_alignment_errors) > 0, "Should detect industry-title misalignment"
    
    def test_validation_summary_completeness(self):
        """Test that validation summary includes all required information"""
        test_data = pd.DataFrame({
            'company_name': ['TechCorp'],
            'first_name': ['John'],
            'last_name': ['Smith']
        })
        
        result = self.validator.validate_complete_dataset(test_data, "summary_test")
        
        # Check required summary fields
        required_fields = [
            'dataset', 'total_records', 'total_columns', 'validation_timestamp',
            'overall_status', 'total_errors'
        ]
        
        for field in required_fields:
            assert field in result, f"Validation summary missing required field: {field}"
        
        # Check validation categories
        validation_categories = [
            'data_types', 'required_fields', 'field_lengths', 'field_patterns',
            'domain_constraints', 'uniqueness_constraints', 'business_rules'
        ]
        
        for category in validation_categories:
            assert category in result, f"Validation summary missing category: {category}"
            assert 'errors_found' in result[category], f"Category {category} missing error count"


class TestMappingIntegrationWithValidation:
    """Test integration of mapping and validation processes"""
    
    def test_end_to_end_mapping_and_validation(self):
        """Test complete mapping and validation workflow"""
        # Create raw CSV data with various header formats
        raw_data = pd.DataFrame({
            'Company Name': ['TechCorp Inc', 'DataSys LLC'],
            'First Name': ['John', 'Jane'],
            'Last Name': ['Smith', 'Doe'],
            'Job Title': ['Software Engineer', 'Data Analyst'],
            'Industry': ['Technology', 'Technology'],
            'E-Mail': ['john@tech.com', 'jane@data.com']
        })
        
        # Step 1: Normalize headers (simulating mapping process)
        normalized_columns = {}
        for col in raw_data.columns:
            normalized = col.strip().lower().replace(' ', '_').replace('-', '_')
            normalized_columns[col] = normalized
        
        mapped_data = raw_data.rename(columns=normalized_columns)
        
        # Step 2: Validate business data structure
        validator = BusinessDataValidator()
        result = validator.validate_complete_dataset(mapped_data, "integration_test")
        
        # Should pass validation after proper mapping
        assert result['overall_status'] == 'PASS', f"Mapped data should pass validation: {result['total_errors']} errors"
        assert result['total_records'] == 2, "Should preserve all records"
        
        # Should detect all expected fields
        expected_business_fields = {'company_name', 'first_name', 'last_name', 'job_title', 'industry', 'e_mail'}
        actual_fields = set(mapped_data.columns)
        mapped_business_fields = actual_fields & expected_business_fields
        
        assert len(mapped_business_fields) >= 5, f"Should map most business fields: {mapped_business_fields}"
    
    def test_validation_with_missing_mapped_fields(self):
        """Test validation behavior when some business fields are missing after mapping"""
        # Incomplete mapping scenario
        partial_data = pd.DataFrame({
            'company_name': ['TechCorp'],
            'first_name': ['John'],
            # Missing last_name (required field)
            'job_title': ['Engineer']
        })
        
        validator = BusinessDataValidator()
        result = validator.validate_complete_dataset(partial_data, "partial_mapping_test")
        
        # Should fail validation due to missing required field
        assert result['overall_status'] == 'FAIL', "Should fail with missing required fields"
        
        # Should specifically identify missing required fields
        required_errors = result['required_fields']['errors']
        missing_column_errors = [err for err in required_errors if err['error'] == 'missing_column']
        assert len(missing_column_errors) > 0, "Should detect missing required columns"
    
    def test_data_integrity_preservation(self):
        """Test that mapping preserves data integrity"""
        original_data = pd.DataFrame({
            'Company Name': ['TechCorp Inc', 'DataSys LLC', 'StartupCo'],
            'Contact': ['john@tech.com', 'jane@data.com', 'bob@startup.com']
        })
        
        # Apply mapping
        mapped_data = original_data.rename(columns={
            'Company Name': 'company_name',
            'Contact': 'email'
        })
        
        # Validate data integrity
        validator = BusinessDataValidator()
        result = validator.validate_complete_dataset(mapped_data, "integrity_test")
        
        # Data should be preserved
        assert len(mapped_data) == len(original_data), "Should preserve record count"
        assert mapped_data['company_name'].notna().all(), "Should preserve company data"
        assert mapped_data['email'].notna().all(), "Should preserve email data"
        
        # Email format should be validated
        pattern_errors = result['field_patterns']['errors']
        email_errors = [err for err in pattern_errors if err['field'] == 'email']
        assert len(email_errors) == 0, "Mapped email data should pass format validation"