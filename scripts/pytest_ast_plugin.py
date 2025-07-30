#!/usr/bin/env python3
"""
Pytest Plugin for AST Syntax Validation

Task Reference: 13.4 - Integrate AST-Based Checker into Pytest Workflows
Purpose: Provide pytest integration for AST syntax validation that runs
         before test collection and execution.

Author: TaskMaster Research Implementation
Created: 2025-07-30
"""

import pytest
import sys
import os
from pathlib import Path
from typing import List, Optional

# Import the AST validator
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from ast_syntax_validator import ASTSyntaxValidator, ErrorSeverity


class ASTSyntaxPlugin:
    """Pytest plugin for AST syntax validation"""
    
    def __init__(self, config):
        """Initialize the plugin with pytest config"""
        self.config = config
        self.validator = ASTSyntaxValidator(debug_mode=config.option.verbose > 0)
        self.validation_enabled = True
        self.fail_on_syntax_errors = True
        self.test_directories = ['tests']
        self.file_patterns = ['test_*.py', '*_test.py']
        
        # Configure based on pytest options
        self._configure_from_options()
    
    def _configure_from_options(self):
        """Configure plugin based on pytest command line options"""
        # Check for custom options
        if hasattr(self.config.option, 'skip_ast_validation'):
            self.validation_enabled = not self.config.option.skip_ast_validation
        
        if hasattr(self.config.option, 'ast_fail_on_syntax'):
            self.fail_on_syntax_errors = self.config.option.ast_fail_on_syntax
        
        if hasattr(self.config.option, 'ast_test_dirs'):
            if self.config.option.ast_test_dirs:
                self.test_directories = self.config.option.ast_test_dirs.split(',')
        
        if hasattr(self.config.option, 'ast_file_patterns'):
            if self.config.option.ast_file_patterns:
                self.file_patterns = self.config.option.ast_file_patterns.split(',')
    
    def pytest_collection_modifyitems(self, config, items):
        """Run AST validation before test collection is finalized"""
        if not self.validation_enabled:
            return
        
        # Validate syntax of all test files
        validation_errors = self._validate_test_files()
        
        if validation_errors:
            self._report_validation_errors(validation_errors)
            
            if self.fail_on_syntax_errors:
                # Fail immediately if syntax errors found
                error_count = len(validation_errors)
                critical_count = sum(1 for e in validation_errors if e.severity == ErrorSeverity.CRITICAL)
                
                if critical_count > 0:
                    pytest.exit(
                        f"AST Validation Failed: {critical_count} critical syntax errors found. "
                        f"Fix syntax errors before running tests.",
                        returncode=2
                    )
                else:
                    pytest.exit(
                        f"AST Validation Failed: {error_count} syntax errors found. "
                        f"Fix syntax errors before running tests.",
                        returncode=1
                    )
    
    def _validate_test_files(self) -> List:
        """Validate all test files and return errors"""
        all_errors = []
        
        for test_dir in self.test_directories:
            if os.path.exists(test_dir):
                for pattern in self.file_patterns:
                    errors = self.validator.validate_directory(test_dir, pattern)
                    all_errors.extend(errors)
        
        return all_errors
    
    def _report_validation_errors(self, validation_errors: List):
        """Report validation errors to pytest output"""
        print("\n" + "=" * 80)
        print("AST SYNTAX VALIDATION ERRORS DETECTED")
        print("=" * 80)
        
        # Group errors by file
        errors_by_file = {}
        for error in validation_errors:
            file_path = error.file_path
            if file_path not in errors_by_file:
                errors_by_file[file_path] = []
            errors_by_file[file_path].append(error)
        
        # Report errors by file
        for file_path, file_errors in errors_by_file.items():
            print(f"\n📁 File: {file_path}")
            print("-" * 60)
            
            for i, error in enumerate(file_errors, 1):
                severity_icon = {
                    ErrorSeverity.CRITICAL: "🔴",
                    ErrorSeverity.HIGH: "🟠", 
                    ErrorSeverity.MEDIUM: "🟡",
                    ErrorSeverity.LOW: "🟢"
                }.get(error.severity, "⚪")
                
                print(f"\n{severity_icon} Error {i}: {error.error_category} [{error.severity.value}]")
                print(f"   Location: Line {error.line_number}, Column {error.column_number}")
                print(f"   Message: {error.error_message}")
                
                if error.suggested_fix:
                    print(f"   Fix: {error.suggested_fix.split('Specific guidance:')[0].strip()}")
                
                if error.code_context:
                    print("   Context:")
                    for context_line in error.code_context.split('\n')[:7]:  # Limit context
                        print(f"   {context_line}")
        
        print("\n" + "=" * 80)
        print(f"Total errors found: {len(validation_errors)}")
        critical_count = sum(1 for e in validation_errors if e.severity == ErrorSeverity.CRITICAL)
        if critical_count > 0:
            print(f"Critical errors: {critical_count} (will prevent test execution)")
        print("=" * 80)


def pytest_addoption(parser):
    """Add custom command line options for AST validation"""
    group = parser.getgroup("ast_validation", "AST Syntax Validation")
    
    group.addoption(
        "--skip-ast-validation",
        action="store_true",
        default=False,
        help="Skip AST syntax validation before running tests"
    )
    
    group.addoption(
        "--ast-fail-on-syntax",
        action="store_true", 
        default=True,
        help="Fail test execution if syntax errors are found (default: True)"
    )
    
    group.addoption(
        "--ast-test-dirs",
        action="store",
        default="tests",
        help="Comma-separated list of directories to validate (default: tests)"
    )
    
    group.addoption(
        "--ast-file-patterns",
        action="store",
        default="test_*.py",
        help="Comma-separated list of file patterns to validate (default: test_*.py)"
    )


def pytest_configure(config):
    """Configure the AST validation plugin"""
    # Only enable if not explicitly disabled
    if not config.option.skip_ast_validation:
        config.pluginmanager.register(ASTSyntaxPlugin(config), "ast_syntax_plugin")


def pytest_unconfigure(config):
    """Clean up the AST validation plugin"""
    plugin = config.pluginmanager.get_plugin("ast_syntax_plugin")
    if plugin is not None:
        config.pluginmanager.unregister(plugin)


# Pytest hook implementations for enhanced reporting
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add AST validation summary to terminal output"""
    plugin = config.pluginmanager.get_plugin("ast_syntax_plugin")
    
    if plugin and plugin.validation_enabled:
        # Check if any syntax errors were found during this session
        if hasattr(plugin.validator, 'validation_errors') and plugin.validator.validation_errors:
            error_count = len(plugin.validator.validation_errors)
            critical_count = sum(1 for e in plugin.validator.validation_errors 
                               if e.severity == ErrorSeverity.CRITICAL)
            
            terminalreporter.write_sep("=", "AST Syntax Validation Summary", bold=True)
            terminalreporter.write_line(f"Files validated: {plugin.validator.files_processed}")
            terminalreporter.write_line(f"Files with errors: {plugin.validator.files_with_errors}")
            terminalreporter.write_line(f"Total syntax errors: {error_count}")
            
            if critical_count > 0:
                terminalreporter.write_line(f"Critical errors: {critical_count}", red=True)
            
            terminalreporter.write_line("\nRun 'python scripts/ast_syntax_validator.py tests' for detailed analysis.")


# Alternative implementation as pytest plugin entry point
class ASTValidationPlugin:
    """Alternative pytest plugin implementation for entry point registration"""
    
    def __init__(self):
        self.validator = None
        self.config = None
    
    def pytest_configure(self, config):
        """Configure the plugin"""
        self.config = config
        if not config.option.skip_ast_validation:
            self.validator = ASTSyntaxValidator(debug_mode=config.option.verbose > 0)
    
    def pytest_collection_modifyitems(self, config, items):
        """Validate syntax before test execution"""
        if self.validator is None:
            return
        
        # Extract unique test file paths from collected items
        test_files = set()
        for item in items:
            if hasattr(item, 'fspath'):
                test_files.add(str(item.fspath))
        
        # Validate each test file
        all_errors = []
        for test_file in test_files:
            if test_file.endswith('.py'):
                errors = self.validator.validate_file(test_file)
                all_errors.extend(errors)
        
        # Report and handle errors
        if all_errors:
            self._handle_validation_errors(all_errors, config)
    
    def _handle_validation_errors(self, errors, config):
        """Handle validation errors based on configuration"""
        # Generate and display report
        report = self.validator.generate_report()
        print("\n" + report)
        
        # Determine if we should fail
        fail_on_syntax = getattr(config.option, 'ast_fail_on_syntax', True)
        if fail_on_syntax:
            critical_errors = [e for e in errors if e.severity == ErrorSeverity.CRITICAL]
            if critical_errors:
                pytest.exit("Critical syntax errors found. Fix before running tests.", returncode=2)
            else:
                pytest.exit("Syntax errors found. Fix before running tests.", returncode=1)


# For setuptools entry point
def pytest_plugins():
    """Return list of pytest plugins"""
    return ["scripts.pytest_ast_plugin"]


if __name__ == "__main__":
    # Allow the plugin to be run standalone for testing
    print("AST Syntax Validation Pytest Plugin")
    print("Add to pytest.ini or pyproject.toml:")
    print("  addopts = -p scripts.pytest_ast_plugin")
    print("  or")
    print("  pytest_plugins = ['scripts.pytest_ast_plugin']")