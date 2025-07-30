#!/usr/bin/env python3
"""
Test Suite for Enhanced AST Error Reporting

Task Reference: 13.3 - Validation tests for enhanced dictionary error reporting
Purpose: Ensure the enhanced AST syntax validator provides detailed, actionable
         error messages with context-specific analysis and suggestions.

Author: TaskMaster Research Implementation  
Created: 2025-07-30
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path

# Add scripts directory to path to import validator
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from ast_syntax_validator import ASTSyntaxValidator, ErrorSeverity


class TestEnhancedASTErrorReporting:
    """Test suite for enhanced error reporting functionality"""
    
    @pytest.fixture
    def validator(self):
        """Create a validator instance for testing"""
        return ASTSyntaxValidator(debug_mode=False)
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_enhanced_unclosed_dictionary_reporting(self, validator, temp_dir):
        """Test enhanced reporting for unclosed dictionary errors"""
        # Create file with deeply nested unclosed dictionary in pytest context
        nested_content = '''
import pytest

@pytest.mark.parametrize("test_case", [
    {
        "input_data": {
            "user": {
                "profile": {
                    "name": "John",
                    "settings": {
                        "theme": "dark",
                        "notifications": True
                    # Missing 4 closing braces here
        "expected": {"success": True}
    }
])
def test_nested_dict(test_case):
    """Test with deeply nested dictionary"""
    pass
'''
        
        test_file = os.path.join(temp_dir, "test_nested.py")
        with open(test_file, 'w') as f:
            f.write(nested_content)
        
        # Validate the file
        errors = validator.validate_file(test_file)
        
        # Should detect enhanced error information
        assert len(errors) == 1
        error = errors[0]
        
        # Check enhanced error message contains context info
        assert error.error_category == "UNCLOSED_DICTIONARY"
        assert "pytest context" in error.error_message or "pytest" in error.suggested_fix
        
        # Check enhanced suggestions contain specific guidance
        assert "Specific guidance:" in error.suggested_fix
        assert "pytest context" in error.suggested_fix or "test data" in error.suggested_fix
        
        # Check enhanced code context contains annotations
        assert "Dict depth:" in error.code_context or "unclosed braces" in error.code_context
    
    def test_enhanced_mismatched_braces_reporting(self, validator, temp_dir):
        """Test enhanced reporting for mismatched brace errors"""
        # Create file with mismatched braces in pytest parametrize
        mismatched_content = '''
import pytest

@pytest.mark.parametrize("input_val,expected", [
    {
        "data": ["item1", "item2"],
        "nested": {
            "level1": {"level2": "value"]  # Should be }
        },
        "result": "success"
    }
])
def test_mismatched_in_parametrize(input_val, expected):
    """Test with mismatched braces in parametrize"""
    pass
'''
        
        test_file = os.path.join(temp_dir, "test_mismatched.py")
        with open(test_file, 'w') as f:
            f.write(mismatched_content)
        
        # Validate the file
        errors = validator.validate_file(test_file)
        
        # Should detect enhanced error information
        assert len(errors) == 1
        error = errors[0]
        
        # Check enhanced context detection
        assert error.error_category == "MISMATCHED_BRACES"
        assert "parametrize" in error.error_message or "parametrize" in error.suggested_fix
        
        # Check enhanced suggestions for pytest context
        assert "pytest.mark.parametrize" in error.suggested_fix or "parametrize" in error.suggested_fix
    
    def test_enhanced_string_termination_reporting(self, validator, temp_dir):
        """Test enhanced reporting for string termination errors"""
        # Create file with unterminated string in test data
        string_content = '''
import pytest

def test_string_data():
    """Test with unterminated string in test data"""
    test_messages = {
        "greeting": "Hello World",
        "farewell": "Goodbye, see you later!
        "status": "incomplete"
    }
    assert test_messages["greeting"] == "Hello World"
'''
        
        test_file = os.path.join(temp_dir, "test_string.py")
        with open(test_file, 'w') as f:
            f.write(string_content)
        
        # Validate the file
        errors = validator.validate_file(test_file)
        
        # Should detect enhanced error information
        assert len(errors) == 1
        error = errors[0]
        
        # Check enhanced analysis for string issues
        assert error.error_category == "STRING_TERMINATION"
        
        # Check enhanced suggestions mention test context
        if "test data" in error.suggested_fix:
            assert "triple quotes" in error.suggested_fix or "raw strings" in error.suggested_fix
    
    def test_enhanced_general_syntax_reporting(self, validator, temp_dir):
        """Test enhanced reporting for general syntax errors"""
        # Create file with missing colon in dictionary
        syntax_content = '''
import pytest

def test_missing_colon():
    """Test with missing colon in dictionary"""
    config_data = {
        "timeout" 30,  # Missing colon
        "retries": 5,
        "debug": True
    }
    assert config_data["timeout"] == 30
'''
        
        test_file = os.path.join(temp_dir, "test_colon.py")
        with open(test_file, 'w') as f:
            f.write(syntax_content)
        
        # Validate the file
        errors = validator.validate_file(test_file)
        
        # Should detect enhanced error information
        assert len(errors) == 1
        error = errors[0]
        
        # Check enhanced pattern detection
        assert error.error_category == "GENERAL_SYNTAX"
        
        # Check enhanced suggestions mention missing colon specifically
        if "missing colon" in error.suggested_fix.lower():
            assert "key: value" in error.suggested_fix
    
    def test_dictionary_depth_analysis(self, validator, temp_dir):
        """Test dictionary depth analysis in error reporting"""
        # Create file with very deep nesting
        deep_content = '''
def test_very_deep_nesting():
    """Test with extremely deep dictionary nesting"""
    data = {
        "level1": {
            "level2": {
                "level3": {
                    "level4": {
                        "level5": {
                            "value": "deep"
                        # Missing 5 closing braces
    result = data["level1"]["level2"]["level3"]["level4"]["level5"]["value"]
    assert result == "deep"
'''
        
        test_file = os.path.join(temp_dir, "test_deep.py")
        with open(test_file, 'w') as f:
            f.write(deep_content)
        
        # Validate the file
        errors = validator.validate_file(test_file)
        
        # Should detect deep nesting in error analysis
        assert len(errors) == 1
        error = errors[0]
        
        # Check that depth analysis is included
        assert "levels deep" in error.error_message or "levels deep" in error.suggested_fix
        assert "5" in error.suggested_fix or "nesting" in error.suggested_fix
    
    def test_brace_balance_analysis(self, validator, temp_dir):
        """Test brace balance analysis in error reporting"""
        # Create file with multiple unclosed braces
        unbalanced_content = '''
def test_multiple_unclosed():
    """Test with multiple unclosed dictionaries"""
    data1 = {
        "section1": {
            "item1": "value1"
        # Missing 2 closing braces
    
    data2 = {
        "section2": {
            "item2": "value2"
        # Missing 2 more closing braces
    
    assert data1["section1"]["item1"] == "value1"
'''
        
        test_file = os.path.join(temp_dir, "test_unbalanced.py")
        with open(test_file, 'w') as f:
            f.write(unbalanced_content)
        
        # Validate the file
        errors = validator.validate_file(test_file)
        
        # Should detect multiple unclosed braces
        assert len(errors) == 1
        error = errors[0]
        
        # Check that brace count analysis is included
        assert ("closing braces" in error.suggested_fix or 
                "unclosed braces" in error.code_context or
                "unclosed braces" in error.error_message)
    
    def test_pytest_context_detection(self, validator, temp_dir):
        """Test pytest context detection accuracy"""
        # Create various pytest contexts
        pytest_contexts = {
            "fixture_context.py": '''
@pytest.fixture
def sample_data():
    return {
        "test_value": "sample"
    # Missing closing brace in fixture
''',
            "parametrize_context.py": '''
@pytest.mark.parametrize("param", [
    {"key": "value"
    # Missing closing brace in parametrize
])
def test_param(param):
    pass
''',
            "test_function_context.py": '''
def test_assertion():
    expected = {
        "result": "success"
    # Missing closing brace in test function
    assert expected["result"] == "success"
''',
            "non_pytest_context.py": '''
def regular_function():
    config = {
        "setting": "value"
    # Missing closing brace in regular function
    return config
'''
        }
        
        for filename, content in pytest_contexts.items():
            test_file = os.path.join(temp_dir, filename)
            with open(test_file, 'w') as f:
                f.write(content)
        
        # Validate all files
        errors = validator.validate_directory(temp_dir, "*.py")
        
        # Check that pytest contexts are detected appropriately
        pytest_errors = []
        non_pytest_errors = []
        
        for error in errors:
            if "pytest" in error.error_message or "pytest" in error.suggested_fix:
                pytest_errors.append(error)
            else:
                non_pytest_errors.append(error)
        
        # Should detect pytest context in fixture, parametrize, and test function files
        assert len(pytest_errors) >= 2  # At least fixture and parametrize contexts
        
        # Non-pytest context should not mention pytest
        for error in non_pytest_errors:
            if "non_pytest_context.py" in error.file_path:
                assert "pytest" not in error.suggested_fix.lower()
    
    def test_line_pattern_analysis(self, validator, temp_dir):
        """Test line pattern analysis for specific error types"""
        # Create file with various line patterns
        pattern_content = '''
def test_patterns():
    """Test various line patterns that cause errors"""
    
    # Missing colon pattern
    config1 = {
        "timeout" 30,  # Missing colon detected
        "enabled": True
    }
    
    # Unmatched quotes pattern  
    config2 = {
        "message": "This string has unmatched quotes,
        "status": "error"
    }
    
    # Incomplete dictionary item pattern
    config3 = {
        "item1": "value1",
        "item2": {  # Incomplete item with missing closing
'''
        
        test_file = os.path.join(temp_dir, "test_patterns.py")
        with open(test_file, 'w') as f:
            f.write(pattern_content)
        
        # Validate the file
        errors = validator.validate_file(test_file)
        
        # Should detect pattern-specific enhancements
        assert len(errors) >= 1
        
        # Check that specific patterns are detected in suggestions
        for error in errors:
            if error.error_category == "UNCLOSED_DICTIONARY":
                # Should have enhanced suggestions based on patterns
                assert len(error.suggested_fix) > 100  # Should be enhanced
    
    def test_enhanced_code_context_annotations(self, validator, temp_dir):
        """Test enhanced code context with annotations"""
        # Create file with complex structure for context analysis
        complex_content = '''
def test_complex_structure():
    """Test complex nested structure with annotations"""
    complex_data = {
        "users": [
            {
                "id": 1,
                "profile": {
                    "settings": {
                        "preferences": {
                            "theme": "dark",
                            "language": "en"
                        },
                        "notifications": True
                    },
                    "metadata": {
                        "created": "2023-01-01",
                        "updated": "2023-12-31"
                    # Missing multiple closing braces - should show annotations
                }
            }
        ]
    # This will cause unclosed dictionary error with deep nesting
'''
        
        test_file = os.path.join(temp_dir, "test_complex.py")
        with open(test_file, 'w') as f:
            f.write(complex_content)
        
        # Validate the file
        errors = validator.validate_file(test_file)
        
        # Should have enhanced context with annotations
        assert len(errors) == 1
        error = errors[0]
        
        # Check for enhanced context annotations
        context_lines = error.code_context.split('\n')
        annotation_lines = [line for line in context_lines if '[' in line and ']' in line and 'Dict depth:' in line]
        
        # Should have at least one annotation line
        assert len(annotation_lines) > 0 or "Summary:" in error.code_context
    
    def test_enhanced_suggestions_comprehensiveness(self, validator, temp_dir):
        """Test that enhanced suggestions are comprehensive and actionable"""
        # Create file with multiple types of issues
        comprehensive_content = '''
import pytest

@pytest.mark.parametrize("test_data", [
    {
        "scenario": "success",
        "input": {
            "user_data": {
                "name": "John Doe",
                "preferences": {
                    "theme": "dark",
                    "notifications": True
                # Multiple missing closing braces in pytest context
            }
        },
        "expected": {"status": "valid"}
    }
])
def test_comprehensive_case(test_data):
    """Comprehensive test case"""
    pass
'''
        
        test_file = os.path.join(temp_dir, "test_comprehensive.py")
        with open(test_file, 'w') as f:
            f.write(comprehensive_content)
        
        # Validate the file
        errors = validator.validate_file(test_file)
        
        # Should have comprehensive enhanced suggestions
        assert len(errors) == 1
        error = errors[0]
        
        # Check comprehensiveness of suggestions
        suggestion_parts = error.suggested_fix.split('\n')
        
        # Should have base suggestion plus specific guidance
        assert any("Specific guidance:" in part for part in suggestion_parts)
        
        # Should mention pytest context
        assert any("pytest" in part.lower() for part in suggestion_parts)
        
        # Should mention nesting or depth
        assert any("nesting" in part.lower() or "levels" in part.lower() for part in suggestion_parts)
        
        # Should provide actionable advice
        assert any("closing braces" in part.lower() for part in suggestion_parts)


class TestEnhancedReportGeneration:
    """Test enhanced report generation features"""
    
    @pytest.fixture
    def validator_with_errors(self, temp_dir):
        """Create validator with multiple enhanced errors for testing"""
        validator = ASTSyntaxValidator(debug_mode=False)
        
        # Create multiple files with different error types
        error_files = {
            "unclosed_dict.py": '''
def test():
    data = {"key": "value"  # Missing closing brace
''',
            "mismatched_braces.py": '''
@pytest.mark.parametrize("x", [{"a": "b"]})  # Mixed braces
def test(x): pass
''',
            "string_error.py": '''
def test():
    msg = "unterminated string
    assert msg == "complete"
'''
        }
        
        for filename, content in error_files.items():
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)
        
        # Validate all files to populate errors
        validator.validate_directory(temp_dir, "*.py")
        
        return validator
    
    def test_enhanced_report_contains_analysis(self, validator_with_errors):
        """Test that enhanced report contains detailed analysis"""
        report = validator_with_errors.generate_report()
        
        # Should contain enhanced error information
        assert "SUMMARY:" in report
        assert "ERROR CATEGORIES:" in report
        assert "DETAILED ERRORS:" in report
        
        # Should contain enhanced suggestions
        assert "Specific guidance:" in report or "pytest" in report.lower()
        
        # Should contain enhanced context
        assert "Dict depth:" in report or "unclosed braces" in report.lower()
    
    def test_enhanced_error_summary(self, validator_with_errors):
        """Test enhanced error summary information"""
        summary = validator_with_errors.get_error_summary()
        
        # Should have comprehensive summary
        assert "total_errors" in summary
        assert "errors_by_category" in summary
        assert "errors_by_severity" in summary
        assert "has_critical_errors" in summary
        
        # Should detect multiple error categories
        assert len(summary["errors_by_category"]) >= 1
        assert len(summary["errors_by_severity"]) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])