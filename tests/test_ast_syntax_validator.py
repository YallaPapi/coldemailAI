#!/usr/bin/env python3
"""
Test Suite for AST Syntax Validator

Task Reference: 13.2 - Validation tests for AST-based syntax checker
Purpose: Ensure the AST syntax validator correctly detects and reports
         dictionary syntax errors in pytest files.

Author: TaskMaster Research Implementation  
Created: 2025-07-30
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch

# Add scripts directory to path to import validator
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from ast_syntax_validator import ASTSyntaxValidator, ErrorSeverity, SyntaxValidationError


class TestASTSyntaxValidator:
    """Test suite for AST syntax validator functionality"""
    
    @pytest.fixture
    def validator(self):
        """Create a validator instance for testing"""
        return ASTSyntaxValidator(debug_mode=False)
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_validator_initialization(self, validator):
        """Test validator initializes correctly"""
        assert isinstance(validator, ASTSyntaxValidator)
        assert validator.debug_mode is False
        assert validator.validation_errors == []
        assert validator.files_processed == 0
        assert validator.files_with_errors == 0
    
    def test_valid_python_file_parsing(self, validator, temp_dir):
        """Test validator correctly handles valid Python files"""
        # Create a valid Python file
        valid_content = '''
import pytest

def test_valid_function():
    """A valid test function"""
    test_data = {
        "name": "John",
        "age": 30,
        "email": "john@example.com"
    }
    assert test_data["name"] == "John"

@pytest.mark.parametrize("input_val,expected", [
    (1, 2),
    (2, 4),
    (3, 6)
])
def test_parametrized_function(input_val, expected):
    """Valid parametrized test"""
    result = input_val * 2
    assert result == expected
'''
        
        valid_file = os.path.join(temp_dir, "test_valid.py")
        with open(valid_file, 'w') as f:
            f.write(valid_content)
        
        # Validate the file
        errors = validator.validate_file(valid_file)
        
        # Should have no syntax errors
        assert len(errors) == 0
        assert validator.files_processed == 1
        assert validator.files_with_errors == 0
    
    def test_unclosed_dictionary_detection(self, validator, temp_dir):
        """Test detection of unclosed dictionary braces"""
        # Create file with unclosed dictionary
        invalid_content = '''
import pytest

def test_unclosed_dict():
    """Test with unclosed dictionary"""
    test_data = {
        "name": "John",
        "age": 30,
        "settings": {
            "theme": "dark",
            "notifications": True
        # Missing closing brace here
    assert test_data["name"] == "John"
'''
        
        invalid_file = os.path.join(temp_dir, "test_unclosed.py")
        with open(invalid_file, 'w') as f:
            f.write(invalid_content)
        
        # Validate the file
        errors = validator.validate_file(invalid_file)
        
        # Should detect unclosed dictionary error
        assert len(errors) == 1
        error = errors[0]
        assert error.error_category == "UNCLOSED_DICTIONARY"
        assert error.severity == ErrorSeverity.CRITICAL
        assert "'{' was never closed" in error.error_message
        assert "Add missing closing brace" in error.suggested_fix
        assert validator.files_with_errors == 1
    
    def test_mismatched_braces_detection(self, validator, temp_dir):
        """Test detection of mismatched braces and brackets"""
        # Create file with mismatched braces
        invalid_content = '''
import pytest

@pytest.mark.parametrize("test_case", [
    {
        "data": ["item1", "item2"],
        "expected": {"count": 2]  # Should be }
    }
])
def test_mismatched_braces(test_case):
    """Test with mismatched braces"""
    pass
'''
        
        invalid_file = os.path.join(temp_dir, "test_mismatched.py")
        with open(invalid_file, 'w') as f:
            f.write(invalid_content)
        
        # Validate the file
        errors = validator.validate_file(invalid_file)
        
        # Should detect mismatched braces error
        assert len(errors) == 1
        error = errors[0]
        assert error.error_category == "MISMATCHED_BRACES"
        assert error.severity == ErrorSeverity.HIGH
        assert "closing parenthesis" in error.error_message
    
    def test_string_termination_detection(self, validator, temp_dir):
        """Test detection of unterminated string literals"""
        # Create file with unterminated string
        invalid_content = '''
import pytest

def test_unterminated_string():
    """Test with unterminated string"""
    test_data = {
        "message": "This string is not terminated properly
        "name": "John"
    }
    assert test_data["name"] == "John"
'''
        
        invalid_file = os.path.join(temp_dir, "test_string.py")
        with open(invalid_file, 'w') as f:
            f.write(invalid_content)
        
        # Validate the file
        errors = validator.validate_file(invalid_file)
        
        # Should detect string termination error
        assert len(errors) == 1
        error = errors[0]
        assert error.error_category == "STRING_TERMINATION"
        assert error.severity == ErrorSeverity.HIGH
        assert "EOL while scanning string literal" in error.error_message
    
    def test_general_syntax_error_detection(self, validator, temp_dir):
        """Test detection of general syntax errors"""
        # Create file with missing colon
        invalid_content = '''
import pytest

def test_missing_colon():
    """Test with missing colon in dictionary"""
    test_data = {
        "name" "John",  # Missing colon
        "age": 30
    }
    assert test_data["name"] == "John"
'''
        
        invalid_file = os.path.join(temp_dir, "test_syntax.py")
        with open(invalid_file, 'w') as f:
            f.write(invalid_content)
        
        # Validate the file
        errors = validator.validate_file(invalid_file)
        
        # Should detect general syntax error
        assert len(errors) == 1
        error = errors[0]
        assert error.error_category == "GENERAL_SYNTAX"
        assert error.severity == ErrorSeverity.MEDIUM
        assert "invalid syntax" in error.error_message
    
    def test_directory_validation(self, validator, temp_dir):
        """Test validation of entire directory"""
        # Create multiple test files
        files_data = {
            "test_valid1.py": '''
def test_valid():
    data = {"key": "value"}
    assert data["key"] == "value"
''',
            "test_valid2.py": '''
import pytest

@pytest.fixture
def sample_data():
    return {"name": "Test", "value": 42}

def test_fixture_usage(sample_data):
    assert sample_data["name"] == "Test"
''',
            "test_invalid.py": '''
def test_invalid():
    data = {
        "key": "value",
        "missing": "brace"
    # Missing closing brace
    assert data["key"] == "value"
'''
        }
        
        # Write test files
        for filename, content in files_data.items():
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)
        
        # Validate directory
        errors = validator.validate_directory(temp_dir, "test_*.py")
        
        # Should find one error from invalid file
        assert len(errors) == 1
        assert validator.files_processed == 3
        assert validator.files_with_errors == 1
        
        # The error should be from the invalid file
        error = errors[0]
        assert "test_invalid.py" in error.file_path
        assert error.error_category == "UNCLOSED_DICTIONARY"
    
    def test_nonexistent_directory_handling(self, validator):
        """Test handling of nonexistent directories"""
        nonexistent_dir = "/path/that/does/not/exist"
        
        errors = validator.validate_directory(nonexistent_dir)
        
        assert len(errors) == 1
        error = errors[0]
        assert error.error_type == "DIRECTORY_NOT_FOUND"
        assert error.severity == ErrorSeverity.CRITICAL
        assert nonexistent_dir in error.error_message
    
    def test_file_read_error_handling(self, validator, temp_dir):
        """Test handling of file read errors"""
        # Create a file and then simulate read error by patching open
        test_file = os.path.join(temp_dir, "test_read_error.py")
        with open(test_file, 'w') as f:
            f.write("# Test file")
        
        # Mock file reading to raise an exception
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            errors = validator.validate_file(test_file)
        
        assert len(errors) == 1
        error = errors[0]
        assert error.error_type == "FILE_READ_ERROR"
        assert error.severity == ErrorSeverity.HIGH
        assert "Failed to read file" in error.error_message
    
    def test_code_context_extraction(self, validator):
        """Test code context extraction functionality"""
        file_content = '''Line 1
Line 2
Line 3 - Error here
Line 4
Line 5'''
        
        context = validator._extract_code_context(file_content, 3, context_lines=2)
        
        # Should show lines around the error
        assert "1: Line 1" in context
        assert "2: Line 2" in context
        assert " --> 3: Line 3 - Error here" in context  # Error line marked
        assert "4: Line 4" in context
        assert "5: Line 5" in context
    
    def test_error_categorization(self, validator):
        """Test error message categorization"""
        test_cases = [
            ("'{' was never closed", ("UNCLOSED_DICTIONARY", ErrorSeverity.CRITICAL)),
            ("closing parenthesis ']' does not match opening parenthesis '{'", ("MISMATCHED_BRACES", ErrorSeverity.HIGH)),
            ("EOL while scanning string literal", ("STRING_TERMINATION", ErrorSeverity.HIGH)),
            ("invalid syntax", ("GENERAL_SYNTAX", ErrorSeverity.MEDIUM)),
            ("unknown error message", ("UNKNOWN", ErrorSeverity.MEDIUM))
        ]
        
        for error_msg, expected in test_cases:
            category, severity = validator._categorize_error(error_msg)
            assert category == expected[0]
            assert severity == expected[1]
    
    def test_fix_suggestion_generation(self, validator):
        """Test generation of fix suggestions"""
        test_cases = [
            ("UNCLOSED_DICTIONARY", "Add missing closing brace"),
            ("MISMATCHED_BRACES", "Check bracket/brace pairing"),
            ("STRING_TERMINATION", "Add missing closing quote"),
            ("GENERAL_SYNTAX", "Review syntax around the error location"),
            ("UNKNOWN", "Review the syntax error message")
        ]
        
        for error_category, expected_keyword in test_cases:
            suggestion = validator._generate_fix_suggestion("test error", error_category)
            assert expected_keyword in suggestion
    
    def test_validation_report_generation(self, validator, temp_dir):
        """Test comprehensive validation report generation"""
        # Create files with different types of errors
        invalid_content = '''
def test_multiple_issues():
    data1 = {
        "key": "value"
    # Missing closing brace
    
    data2 = {
        "string": "unterminated
        "number": 42
    }
'''
        
        invalid_file = os.path.join(temp_dir, "test_multiple.py")
        with open(invalid_file, 'w') as f:
            f.write(invalid_content)
        
        # Validate and generate report
        validator.validate_file(invalid_file)
        report = validator.generate_report()
        
        # Verify report contains expected sections
        assert "AST SYNTAX VALIDATION REPORT" in report
        assert "SUMMARY:" in report
        assert "ERROR CATEGORIES:" in report
        assert "ERROR SEVERITY:" in report
        assert "DETAILED ERRORS:" in report
        
        # Check summary data
        summary = validator.get_error_summary()
        assert summary["files_processed"] == 1
        assert summary["files_with_errors"] == 1
        assert summary["total_errors"] >= 1
        assert isinstance(summary["errors_by_category"], dict)
        assert isinstance(summary["errors_by_severity"], dict)
    
    def test_pytest_specific_validation(self, validator, temp_dir):
        """Test pytest-specific validation features"""
        # Create file with pytest.mark.parametrize issues
        pytest_content = '''
import pytest

@pytest.mark.parametrize("param")  # Missing values argument
def test_incomplete_parametrize(param):
    pass

@pytest.mark.parametrize("input_val,expected", [
    (1, 2),
    (2, 4)
])
def test_proper_parametrize(input_val, expected):
    assert input_val * 2 == expected
'''
        
        pytest_file = os.path.join(temp_dir, "test_pytest.py")
        with open(pytest_file, 'w') as f:
            f.write(pytest_content)
        
        # Validate file
        errors = validator.validate_file(pytest_file)
        
        # Should detect pytest parametrize issue
        pytest_errors = [e for e in errors if e.error_category == "PYTEST_USAGE"]
        assert len(pytest_errors) == 1
        assert "parametrize requires at least 2 arguments" in pytest_errors[0].error_message
    
    def test_dictionary_node_validation(self, validator, temp_dir):
        """Test AST-level dictionary node validation"""
        # This test validates the deeper AST analysis
        # Create a valid file to test AST node validation
        valid_content = '''
import pytest

def test_dict_validation():
    """Test dictionary validation at AST level"""
    normal_dict = {"key1": "value1", "key2": "value2"}
    
    # Dictionary comprehension
    comp_dict = {f"key_{i}": f"value_{i}" for i in range(3)}
    
    assert len(normal_dict) == 2
    assert len(comp_dict) == 3
'''
        
        valid_file = os.path.join(temp_dir, "test_ast_nodes.py")
        with open(valid_file, 'w') as f:
            f.write(valid_content)
        
        # Validate file - should pass AST validation
        errors = validator.validate_file(valid_file)
        
        # Should have no errors for valid AST structure
        assert len(errors) == 0
    
    def test_error_severity_handling(self, validator, temp_dir):
        """Test different error severity levels are handled correctly"""
        # Create files with different severity errors
        critical_content = '''
def test_critical():
    data = {
        "key": "value"
    # Missing closing brace - CRITICAL
'''
        
        high_content = '''
def test_high():
    data = {
        "key": "value"
        "unterminated_string": "this string never ends
    }
'''
        
        medium_content = '''
def test_medium():
    data = {
        "key" "value"  # Missing colon - MEDIUM
    }
'''
        
        test_files = [
            ("test_critical.py", critical_content),
            ("test_high.py", high_content),
            ("test_medium.py", medium_content)
        ]
        
        for filename, content in test_files:
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)
        
        # Validate directory
        validator.validate_directory(temp_dir, "test_*.py")
        
        # Check that different severities are captured
        summary = validator.get_error_summary()
        assert summary["has_critical_errors"] is True
        
        # Verify we have errors of different severities
        severity_counts = summary["errors_by_severity"]
        assert "CRITICAL" in severity_counts
        assert "HIGH" in severity_counts or "MEDIUM" in severity_counts


class TestASTValidatorCommandLine:
    """Test command-line interface functionality"""
    
    def test_main_function_with_valid_directory(self, tmp_path):
        """Test main function with valid directory"""
        # Create a valid test file
        valid_content = '''
def test_simple():
    assert True
'''
        
        test_file = os.path.join(str(tmp_path), "test_simple.py")
        with open(test_file, 'w') as f:
            f.write(valid_content)
        
        # Test main function via sys.argv mocking
        test_args = ["ast_syntax_validator.py", str(tmp_path), "--pattern", "test_*.py"]
        
        with patch.object(sys, 'argv', test_args):
            with patch('sys.exit') as mock_exit:
                # Import and run main
                from ast_syntax_validator import main
                main()
                
                # Should exit with code 0 (no errors)
                mock_exit.assert_called_with(0)
    
    def test_main_function_with_errors(self, tmp_path):
        """Test main function with syntax errors"""
        # Create an invalid test file
        invalid_content = '''
def test_invalid():
    data = {
        "key": "value"
    # Missing closing brace
'''
        
        test_file = os.path.join(str(tmp_path), "test_invalid.py")
        with open(test_file, 'w') as f:
            f.write(invalid_content)
        
        # Test main function
        test_args = ["ast_syntax_validator.py", str(tmp_path), "--pattern", "test_*.py"]
        
        with patch.object(sys, 'argv', test_args):
            with patch('sys.exit') as mock_exit:
                from ast_syntax_validator import main
                main()
                
                # Should exit with non-zero code (errors found)
                assert mock_exit.called
                exit_code = mock_exit.call_args[0][0] 
                assert exit_code > 0  # Either 1 for errors or 2 for critical errors


if __name__ == "__main__":
    pytest.main([__file__, "-v"])