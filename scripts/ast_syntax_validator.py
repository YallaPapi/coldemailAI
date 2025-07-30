#!/usr/bin/env python3
"""
AST-Based Syntax Validation for Pytest Files

Task Reference: 13.2 - Develop AST-Based Syntax Validation
Purpose: Parse pytest files using ast.parse() to detect and report syntax errors,
         with special focus on dictionary-related issues.

Author: TaskMaster Research Implementation
Created: 2025-07-30  
"""

import ast
import sys
import os
import traceback
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels for syntax validation"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH" 
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class SyntaxValidationError:
    """Structured representation of syntax validation errors"""
    file_path: str
    line_number: int
    column_number: int
    error_type: str
    error_message: str
    severity: ErrorSeverity
    suggested_fix: Optional[str] = None
    code_context: Optional[str] = None
    error_category: str = "GENERAL"


class ASTSyntaxValidator:
    """
    AST-based syntax validator specifically designed for pytest files.
    
    Focuses on detecting dictionary syntax errors and other common pytest
    code patterns that are prone to syntax issues.
    """
    
    def __init__(self, debug_mode: bool = False):
        """Initialize the AST syntax validator"""
        self.debug_mode = debug_mode
        self.validation_errors: List[SyntaxValidationError] = []
        self.files_processed = 0
        self.files_with_errors = 0
        
        # Dictionary error patterns to detect
        self.dict_error_patterns = {
            "unclosed_brace": "'{' was never closed",
            "mismatched_brace": "closing parenthesis",
            "missing_colon": "invalid syntax",
            "missing_comma": "invalid syntax",
            "malformed_comprehension": "invalid syntax",
            "string_termination": "EOL while scanning string literal"
        }
    
    def validate_file(self, file_path: str) -> List[SyntaxValidationError]:
        """
        Validate a single Python file using AST parsing
        
        Args:
            file_path: Path to the Python file to validate
            
        Returns:
            List of SyntaxValidationError objects found in the file
        """
        file_errors = []
        
        try:
            if self.debug_mode:
                print(f"[DEBUG] Validating file: {file_path}")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # Attempt AST parsing
            try:
                ast_tree = ast.parse(file_content, filename=file_path)
                
                # If parsing succeeds, perform deeper validation
                file_errors.extend(self._validate_ast_structure(ast_tree, file_path, file_content))
                
                if self.debug_mode:
                    print(f"[DEBUG] AST parsing successful for {file_path}")
                    
            except SyntaxError as e:
                # Capture and analyze syntax errors
                syntax_error = self._analyze_syntax_error(e, file_path, file_content)
                file_errors.append(syntax_error)
                
                if self.debug_mode:
                    print(f"[DEBUG] Syntax error detected in {file_path}: {e}")
            
            self.files_processed += 1
            if file_errors:
                self.files_with_errors += 1
            
            # Add file errors to instance validation errors
            self.validation_errors.extend(file_errors)
                
        except Exception as e:
            # Handle file reading errors or other unexpected issues
            error = SyntaxValidationError(
                file_path=file_path,
                line_number=0,
                column_number=0,
                error_type="FILE_READ_ERROR",
                error_message=f"Failed to read file: {str(e)}",
                severity=ErrorSeverity.HIGH,
                error_category="FILE_ACCESS"
            )
            file_errors.append(error)
            
            if self.debug_mode:
                print(f"[DEBUG] File read error for {file_path}: {e}")
        
        return file_errors
    
    def _analyze_syntax_error(self, syntax_error: SyntaxError, file_path: str, file_content: str) -> SyntaxValidationError:
        """
        Analyze a SyntaxError and create a structured validation error
        
        Args:
            syntax_error: The SyntaxError exception caught during parsing
            file_path: Path to the file where error occurred
            file_content: Content of the file for context analysis
            
        Returns:
            SyntaxValidationError with detailed analysis
        """
        error_msg = str(syntax_error.msg)
        line_num = syntax_error.lineno or 0
        col_num = syntax_error.offset or 0
        
        # Determine error category and severity
        error_category, severity = self._categorize_error(error_msg)
        
        # Enhanced analysis for dictionary-specific errors
        enhanced_analysis = self._analyze_dictionary_context(file_content, line_num, col_num, error_msg)
        
        # Generate enhanced suggested fix based on context analysis
        suggested_fix = self._generate_enhanced_fix_suggestion(
            error_msg, error_category, enhanced_analysis, file_content, line_num
        )
        
        # Extract code context with enhanced formatting
        code_context = self._extract_enhanced_code_context(file_content, line_num, enhanced_analysis)
        
        return SyntaxValidationError(
            file_path=file_path,
            line_number=line_num,
            column_number=col_num,
            error_type="SYNTAX_ERROR",
            error_message=f"{error_msg} {enhanced_analysis.get('context_info', '')}".strip(),
            severity=severity,
            suggested_fix=suggested_fix,
            code_context=code_context,
            error_category=error_category
        )
    
    def _categorize_error(self, error_message: str) -> Tuple[str, ErrorSeverity]:
        """
        Categorize error based on message patterns
        
        Args:
            error_message: The error message from SyntaxError
            
        Returns:
            Tuple of (error_category, severity)
        """
        error_msg_lower = error_message.lower()
        
        # Dictionary-specific error patterns
        if "'{' was never closed" in error_message:
            return ("UNCLOSED_DICTIONARY", ErrorSeverity.CRITICAL)
        elif "closing parenthesis" in error_msg_lower and ("does not match" in error_msg_lower):
            return ("MISMATCHED_BRACES", ErrorSeverity.HIGH)
        elif "eol while scanning string literal" in error_msg_lower:
            return ("STRING_TERMINATION", ErrorSeverity.HIGH)
        elif "unterminated string literal" in error_msg_lower:
            return ("STRING_TERMINATION", ErrorSeverity.HIGH)
        elif "invalid syntax" in error_msg_lower:
            # Could be missing colon, comma, or other syntax issue
            return ("GENERAL_SYNTAX", ErrorSeverity.MEDIUM)
        else:
            return ("UNKNOWN", ErrorSeverity.MEDIUM)
    
    def _generate_fix_suggestion(self, error_message: str, error_category: str) -> str:
        """
        Generate actionable fix suggestions based on error category
        
        Args:
            error_message: The original error message
            error_category: Categorized error type
            
        Returns:
            Human-readable fix suggestion
        """
        suggestions = {
            "UNCLOSED_DICTIONARY": "Add missing closing brace '}' to complete dictionary definition. Check for proper nesting and alignment.",
            "MISMATCHED_BRACES": "Check bracket/brace pairing. Ensure '{', '[', '(' are properly matched with '}', ']', ')'.",
            "STRING_TERMINATION": "Add missing closing quote to terminate string literal. Check for escaped quotes within strings.",
            "GENERAL_SYNTAX": "Review syntax around the error location. Common issues: missing colons in dictionaries, missing commas between items.",
            "UNKNOWN": "Review the syntax error message and check Python documentation for correct syntax patterns."
        }
        
        return suggestions.get(error_category, "Review syntax at the indicated location and consult Python documentation.")
    
    def _extract_code_context(self, file_content: str, line_number: int, context_lines: int = 3) -> str:
        """
        Extract code context around the error line
        
        Args:
            file_content: Full content of the file
            line_number: Line where error occurred
            context_lines: Number of lines to show before/after error line
            
        Returns:
            Code context as formatted string
        """
        if line_number <= 0:
            return "No line context available"
        
        lines = file_content.split('\n')
        start_line = max(0, line_number - context_lines - 1)
        end_line = min(len(lines), line_number + context_lines)
        
        context_lines_list = []
        for i in range(start_line, end_line):
            line_num = i + 1
            line_content = lines[i] if i < len(lines) else ""
            
            # Mark the error line
            marker = " --> " if line_num == line_number else "     "
            context_lines_list.append(f"{marker}{line_num}: {line_content}")
        
        return "\n".join(context_lines_list)
    
    def _analyze_dictionary_context(self, file_content: str, line_number: int, col_number: int, error_msg: str) -> Dict[str, Any]:
        """
        Analyze the code context around dictionary syntax errors for enhanced reporting
        
        Args:
            file_content: Full content of the file
            line_number: Line where error occurred
            col_number: Column where error occurred
            error_msg: Original error message
            
        Returns:
            Dictionary containing enhanced analysis information
        """
        lines = file_content.split('\n')
        analysis = {
            'context_info': '',
            'likely_cause': '',
            'brace_analysis': {},
            'pytest_context': False,
            'dictionary_depth': 0,
            'line_patterns': []
        }
        
        if line_number <= 0 or line_number > len(lines):
            return analysis
        
        # Analyze brace/bracket balance in the file
        analysis['brace_analysis'] = self._analyze_brace_balance(file_content, line_number)
        
        # Detect pytest-specific contexts
        analysis['pytest_context'] = self._detect_pytest_context(lines, line_number)
        
        # Analyze dictionary nesting depth
        analysis['dictionary_depth'] = self._calculate_dictionary_depth(lines, line_number)
        
        # Find patterns around the error line
        analysis['line_patterns'] = self._analyze_line_patterns(lines, line_number)
        
        # Generate context-specific information
        if "'{' was never closed" in error_msg:
            analysis['context_info'] = self._analyze_unclosed_brace_context(lines, line_number, analysis)
        elif "closing parenthesis" in error_msg.lower():
            analysis['context_info'] = self._analyze_mismatched_brace_context(lines, line_number, analysis)
        elif "eol while scanning" in error_msg.lower():
            analysis['context_info'] = self._analyze_string_context(lines, line_number, analysis)
        
        return analysis
    
    def _analyze_brace_balance(self, file_content: str, error_line: int) -> Dict[str, Any]:
        """Analyze brace balance in the file"""
        lines = file_content.split('\n')
        balance = {'open_braces': 0, 'open_brackets': 0, 'open_parens': 0, 'unmatched_positions': []}
        
        for i, line in enumerate(lines[:error_line], 1):
            for j, char in enumerate(line):
                if char == '{':
                    balance['open_braces'] += 1
                elif char == '}':
                    balance['open_braces'] -= 1
                elif char == '[':
                    balance['open_brackets'] += 1
                elif char == ']':
                    balance['open_brackets'] -= 1
                elif char == '(':
                    balance['open_parens'] += 1  
                elif char == ')':
                    balance['open_parens'] -= 1
                
                # Track unmatched opening positions
                if balance['open_braces'] < 0 or balance['open_brackets'] < 0 or balance['open_parens'] < 0:
                    balance['unmatched_positions'].append((i, j, char))
        
        return balance
    
    def _detect_pytest_context(self, lines: List[str], line_number: int) -> bool:
        """Detect if error occurs in pytest-specific context"""
        context_start = max(0, line_number - 10)
        context_end = min(len(lines), line_number + 5)
        
        context_lines = lines[context_start:context_end]
        pytest_indicators = [
            '@pytest.mark.parametrize',
            '@pytest.fixture',
            'def test_',
            'assert ',
            'pytest.raises'
        ]
        
        return any(indicator in '\n'.join(context_lines) for indicator in pytest_indicators)
    
    def _calculate_dictionary_depth(self, lines: List[str], line_number: int) -> int:
        """Calculate the nesting depth of dictionaries at the error line"""
        depth = 0
        for i in range(line_number):
            if i < len(lines):
                line = lines[i]
                depth += line.count('{') - line.count('}')
        return max(0, depth)
    
    def _analyze_line_patterns(self, lines: List[str], line_number: int) -> List[str]:
        """Analyze patterns around the error line"""
        patterns = []
        if line_number > 0 and line_number <= len(lines):
            current_line = lines[line_number - 1]
            
            # Check for common patterns
            if ':' not in current_line and '=' in current_line:
                patterns.append('missing_colon')
            if current_line.strip().endswith(',') and '{' in current_line:
                patterns.append('incomplete_dict_item')
            if '"' in current_line and current_line.count('"') % 2 != 0:
                patterns.append('unmatched_quotes')
            if "'" in current_line and current_line.count("'") % 2 != 0:
                patterns.append('unmatched_quotes')
        
        return patterns
    
    def _analyze_unclosed_brace_context(self, lines: List[str], line_number: int, analysis: Dict) -> str:
        """Generate context-specific information for unclosed brace errors"""
        info_parts = []
        
        if analysis['pytest_context']:
            info_parts.append("(in pytest context)")
        
        if analysis['dictionary_depth'] > 2:
            info_parts.append(f"(nested {analysis['dictionary_depth']} levels deep)")
        
        brace_count = analysis['brace_analysis']['open_braces']
        if brace_count > 1:
            info_parts.append(f"({brace_count} unclosed braces detected)")
        
        return " ".join(info_parts)
    
    def _analyze_mismatched_brace_context(self, lines: List[str], line_number: int, analysis: Dict) -> str:
        """Generate context-specific information for mismatched brace errors"""
        info_parts = []
        
        if analysis['pytest_context']:
            info_parts.append("(in pytest parametrize context)")
        
        unmatched = analysis['brace_analysis']['unmatched_positions']
        if unmatched:
            info_parts.append(f"(bracket mismatch detected at {len(unmatched)} locations)")
        
        return " ".join(info_parts)
    
    def _analyze_string_context(self, lines: List[str], line_number: int, analysis: Dict) -> str:
        """Generate context-specific information for string termination errors"""
        info_parts = []
        
        if 'unmatched_quotes' in analysis['line_patterns']:
            info_parts.append("(unmatched quote characters detected)")
        
        if analysis['pytest_context']:
            info_parts.append("(in test data string)")
        
        return " ".join(info_parts)
    
    def _generate_enhanced_fix_suggestion(self, error_message: str, error_category: str, 
                                        enhanced_analysis: Dict, file_content: str, line_number: int) -> str:
        """
        Generate enhanced fix suggestions based on context analysis
        
        Args:
            error_message: Original error message
            error_category: Categorized error type  
            enhanced_analysis: Enhanced context analysis
            file_content: Full file content
            line_number: Line where error occurred
            
        Returns:
            Enhanced fix suggestion with specific guidance
        """
        base_suggestion = self._generate_fix_suggestion(error_message, error_category)
        
        # Add context-specific enhancements
        enhancements = []
        
        if error_category == "UNCLOSED_DICTIONARY":
            if enhanced_analysis['dictionary_depth'] > 2:
                enhancements.append(
                    f"Check dictionary nesting - {enhanced_analysis['dictionary_depth']} levels deep. "
                    "Use proper indentation to align closing braces with their opening counterparts."
                )
            
            brace_count = enhanced_analysis['brace_analysis']['open_braces']
            if brace_count > 1:
                enhancements.append(f"Add {brace_count} closing braces '}}' to balance the structure.")
            
            if enhanced_analysis['pytest_context']:
                enhancements.append(
                    "In pytest context: Ensure test data dictionaries are properly closed. "
                    "Consider using trailing commas for easier maintenance."
                )
        
        elif error_category == "MISMATCHED_BRACES":
            if enhanced_analysis['pytest_context']:
                enhancements.append(
                    "In pytest.mark.parametrize: Ensure dictionary values use '{}' and "
                    "list parameters use '[]'. Check nested structures carefully."
                )
            
            unmatched = enhanced_analysis['brace_analysis']['unmatched_positions']
            if unmatched:
                enhancements.append(
                    f"Bracket mismatches found at {len(unmatched)} positions. "
                    "Review each opening bracket for its proper closing counterpart."
                )
        
        elif error_category == "STRING_TERMINATION":
            if 'unmatched_quotes' in enhanced_analysis['line_patterns']:
                enhancements.append(
                    "Quote mismatch detected. Use consistent quote types (\" or ') and escape "
                    "quotes within strings with backslash (\\\" or \\')."
                )
            
            if enhanced_analysis['pytest_context']:
                enhancements.append(
                    "In test data: Consider using triple quotes for multi-line strings or "
                    "raw strings (r'...') for strings containing special characters."
                )
        
        elif error_category == "GENERAL_SYNTAX":
            if 'missing_colon' in enhanced_analysis['line_patterns']:
                enhancements.append(
                    "Missing colon detected in dictionary definition. "
                    "Ensure all key-value pairs use 'key: value' format."
                )
        
        # Combine base suggestion with enhancements
        if enhancements:
            return f"{base_suggestion}\n\nSpecific guidance:\n• " + "\n• ".join(enhancements)
        else:
            return base_suggestion
    
    def _extract_enhanced_code_context(self, file_content: str, line_number: int, 
                                     enhanced_analysis: Dict, context_lines: int = 5) -> str:
        """
        Extract enhanced code context with annotations based on analysis
        
        Args:
            file_content: Full content of the file
            line_number: Line where error occurred
            enhanced_analysis: Enhanced context analysis
            context_lines: Number of lines to show before/after error
            
        Returns:
            Enhanced code context with annotations
        """
        if line_number <= 0:
            return "No line context available"
        
        lines = file_content.split('\n')
        start_line = max(0, line_number - context_lines - 1)
        end_line = min(len(lines), line_number + context_lines)
        
        context_lines_list = []
        brace_balance = 0
        
        for i in range(start_line, end_line):
            line_num = i + 1
            line_content = lines[i] if i < len(lines) else ""
            
            # Track brace balance for annotations
            brace_balance += line_content.count('{') - line_content.count('}')
            
            # Mark the error line and add annotations
            if line_num == line_number:
                marker = " --> "
                # Add specific annotations based on analysis
                annotations = []
                if enhanced_analysis['dictionary_depth'] > 0:
                    annotations.append(f"[Dict depth: {enhanced_analysis['dictionary_depth']}]")
                if brace_balance > 0:
                    annotations.append(f"[{brace_balance} unclosed braces above]")
                
                annotation_str = " ".join(annotations)
                context_lines_list.append(f"{marker}{line_num}: {line_content}")
                if annotation_str:
                    context_lines_list.append(f"      {annotation_str}")
            else:
                marker = "     "
                context_lines_list.append(f"{marker}{line_num}: {line_content}")
        
        # Add summary if helpful
        if enhanced_analysis['brace_analysis']['open_braces'] > 0:
            context_lines_list.append("")
            context_lines_list.append(
                f"   Summary: {enhanced_analysis['brace_analysis']['open_braces']} unclosed braces detected"
            )
        
        return "\n".join(context_lines_list)
    
    def _validate_ast_structure(self, ast_tree: ast.AST, file_path: str, file_content: str) -> List[SyntaxValidationError]:
        """
        Perform deeper validation on successfully parsed AST
        
        Args:
            ast_tree: Parsed AST tree
            file_path: Path to the file being validated
            file_content: Original file content
            
        Returns:
            List of validation errors found in AST structure
        """
        validation_errors = []
        
        # Walk through AST nodes to find potential issues
        for node in ast.walk(ast_tree):
            # Check dictionary nodes for potential issues
            if isinstance(node, ast.Dict):
                dict_errors = self._validate_dictionary_node(node, file_path)
                validation_errors.extend(dict_errors)
            
            # Check dictionary comprehensions
            elif isinstance(node, ast.DictComp):
                comp_errors = self._validate_dict_comprehension(node, file_path)
                validation_errors.extend(comp_errors)
            
            # Check function calls that might be pytest.mark.parametrize
            elif isinstance(node, ast.Call):
                call_errors = self._validate_pytest_calls(node, file_path)
                validation_errors.extend(call_errors)
        
        return validation_errors
    
    def _validate_dictionary_node(self, dict_node: ast.Dict, file_path: str) -> List[SyntaxValidationError]:
        """
        Validate dictionary AST node for potential issues
        
        Args:
            dict_node: Dictionary AST node
            file_path: Path to the file containing the dictionary
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check for key-value mismatch (shouldn't happen in valid AST, but good to check)
        if len(dict_node.keys) != len(dict_node.values):
            error = SyntaxValidationError(
                file_path=file_path,
                line_number=getattr(dict_node, 'lineno', 0),
                column_number=getattr(dict_node, 'col_offset', 0),
                error_type="DICT_STRUCTURE_ERROR",
                error_message="Dictionary has mismatched number of keys and values",
                severity=ErrorSeverity.HIGH,
                error_category="DICTIONARY_STRUCTURE"
            )
            errors.append(error)
        
        # Check for None keys (which indicate syntax issues in comprehensions)
        none_key_count = sum(1 for key in dict_node.keys if key is None)
        if none_key_count > 0:
            error = SyntaxValidationError(
                file_path=file_path,
                line_number=getattr(dict_node, 'lineno', 0),
                column_number=getattr(dict_node, 'col_offset', 0),
                error_type="DICT_NONE_KEY_ERROR",
                error_message=f"Dictionary contains {none_key_count} None keys, indicating potential syntax issues",
                severity=ErrorSeverity.MEDIUM,
                error_category="DICTIONARY_KEYS"
            )
            errors.append(error)
        
        return errors
    
    def _validate_dict_comprehension(self, comp_node: ast.DictComp, file_path: str) -> List[SyntaxValidationError]:
        """
        Validate dictionary comprehension for common syntax issues
        
        Args:
            comp_node: Dictionary comprehension AST node
            file_path: Path to the file containing the comprehension
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check if key and value expressions exist
        if comp_node.key is None or comp_node.value is None:
            error = SyntaxValidationError(
                file_path=file_path,
                line_number=getattr(comp_node, 'lineno', 0),
                column_number=getattr(comp_node, 'col_offset', 0),
                error_type="DICT_COMP_STRUCTURE_ERROR",
                error_message="Dictionary comprehension missing key or value expression",
                severity=ErrorSeverity.HIGH,
                error_category="DICTIONARY_COMPREHENSION"
            )
            errors.append(error)
        
        return errors
    
    def _validate_pytest_calls(self, call_node: ast.Call, file_path: str) -> List[SyntaxValidationError]:
        """
        Validate pytest-specific function calls for common issues
        
        Args:
            call_node: Function call AST node
            file_path: Path to the file containing the call
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check if this is a pytest.mark.parametrize call
        if (hasattr(call_node.func, 'attr') and 
            call_node.func.attr == 'parametrize' and
            hasattr(call_node.func.value, 'attr') and
            call_node.func.value.attr == 'mark'):
            
            # Validate parametrize arguments - should have at least 2 args
            if len(call_node.args) < 2:
                error = SyntaxValidationError(
                    file_path=file_path,
                    line_number=getattr(call_node, 'lineno', 0),
                    column_number=getattr(call_node, 'col_offset', 0),
                    error_type="PYTEST_PARAMETRIZE_ERROR",
                    error_message="pytest.mark.parametrize requires at least 2 arguments (parameter names and values)",
                    severity=ErrorSeverity.MEDIUM,
                    error_category="PYTEST_USAGE"
                )
                errors.append(error)
        
        return errors
    
    def validate_directory(self, directory_path: str, pattern: str = "test_*.py") -> List[SyntaxValidationError]:
        """
        Validate all pytest files in a directory
        
        Args:
            directory_path: Path to directory containing pytest files
            pattern: File pattern to match (default: test_*.py)
            
        Returns:
            Combined list of all validation errors found
        """
        all_errors = []
        
        if self.debug_mode:
            print(f"[DEBUG] Scanning directory: {directory_path} for pattern: {pattern}")
        
        try:
            directory = Path(directory_path)
            if not directory.exists():
                error = SyntaxValidationError(
                    file_path=directory_path,
                    line_number=0,
                    column_number=0,
                    error_type="DIRECTORY_NOT_FOUND",
                    error_message=f"Directory does not exist: {directory_path}",
                    severity=ErrorSeverity.CRITICAL,
                    error_category="FILE_ACCESS"
                )
                return [error]
            
            # Find all matching files
            test_files = list(directory.glob(pattern))
            
            if self.debug_mode:
                print(f"[DEBUG] Found {len(test_files)} files matching pattern")
            
            # Validate each file
            for test_file in test_files:
                file_errors = self.validate_file(str(test_file))
                all_errors.extend(file_errors)
                self.validation_errors.extend(file_errors)
            
        except Exception as e:
            error = SyntaxValidationError(
                file_path=directory_path,
                line_number=0,
                column_number=0,
                error_type="DIRECTORY_SCAN_ERROR",
                error_message=f"Failed to scan directory: {str(e)}",
                severity=ErrorSeverity.HIGH,
                error_category="FILE_ACCESS"
            )
            all_errors.append(error)
        
        return all_errors
    
    def generate_report(self) -> str:
        """
        Generate a comprehensive validation report
        
        Returns:
            Formatted validation report as string
        """
        report_lines = []
        
        # Header
        report_lines.append("=" * 80)
        report_lines.append("AST SYNTAX VALIDATION REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # Summary statistics
        report_lines.append("SUMMARY:")
        report_lines.append(f"  Files processed: {self.files_processed}")
        report_lines.append(f"  Files with errors: {self.files_with_errors}")
        report_lines.append(f"  Total errors found: {len(self.validation_errors)}")
        report_lines.append("")
        
        # Error breakdown by category
        category_counts = {}
        severity_counts = {}
        
        for error in self.validation_errors:
            category_counts[error.error_category] = category_counts.get(error.error_category, 0) + 1
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
        
        if category_counts:
            report_lines.append("ERROR CATEGORIES:")
            for category, count in sorted(category_counts.items()):
                report_lines.append(f"  {category}: {count}")
            report_lines.append("")
        
        if severity_counts:
            report_lines.append("ERROR SEVERITY:")
            for severity, count in sorted(severity_counts.items()):
                report_lines.append(f"  {severity}: {count}")
            report_lines.append("")
        
        # Detailed error list
        if self.validation_errors:
            report_lines.append("DETAILED ERRORS:")
            report_lines.append("-" * 80)
            
            for i, error in enumerate(self.validation_errors, 1):
                report_lines.append(f"\n{i}. {error.error_category} [{error.severity.value}]")
                report_lines.append(f"   File: {error.file_path}")
                report_lines.append(f"   Location: Line {error.line_number}, Column {error.column_number}")
                report_lines.append(f"   Error: {error.error_message}")
                
                if error.suggested_fix:
                    report_lines.append(f"   Suggested Fix: {error.suggested_fix}")
                
                if error.code_context:
                    report_lines.append("   Code Context:")
                    for context_line in error.code_context.split('\n'):
                        report_lines.append(f"   {context_line}")
                
                report_lines.append("")
        else:
            report_lines.append("No validation errors found! ✅")
        
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get a structured summary of validation results
        
        Returns:
            Dictionary containing validation summary data
        """
        return {
            "files_processed": self.files_processed,
            "files_with_errors": self.files_with_errors,
            "total_errors": len(self.validation_errors),
            "errors_by_category": self._group_errors_by_category(),
            "errors_by_severity": self._group_errors_by_severity(),
            "has_critical_errors": any(e.severity == ErrorSeverity.CRITICAL for e in self.validation_errors)
        }
    
    def _group_errors_by_category(self) -> Dict[str, int]:
        """Group validation errors by category"""
        category_counts = {}
        for error in self.validation_errors:
            category_counts[error.error_category] = category_counts.get(error.error_category, 0) + 1
        return category_counts
    
    def _group_errors_by_severity(self) -> Dict[str, int]:
        """Group validation errors by severity"""
        severity_counts = {}
        for error in self.validation_errors:
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
        return severity_counts


def main():
    """
    Main entry point for AST syntax validation script
    
    Usage:
        python ast_syntax_validator.py [directory_path] [--debug] [--pattern PATTERN]
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AST-based syntax validator for pytest files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ast_syntax_validator.py tests/                    # Validate all test_*.py files in tests/
  python ast_syntax_validator.py . --pattern "*.py"       # Validate all .py files in current directory  
  python ast_syntax_validator.py tests/ --debug           # Enable debug output
        """
    )
    
    parser.add_argument(
        "directory",
        nargs="?",
        default="tests",
        help="Directory to scan for pytest files (default: tests)"
    )
    
    parser.add_argument(
        "--pattern",
        default="test_*.py",
        help="File pattern to match (default: test_*.py)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )
    
    parser.add_argument(
        "--output",
        help="Output file for validation report (default: stdout)"
    )
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = ASTSyntaxValidator(debug_mode=args.debug)
    
    # Validate directory
    print(f"Starting AST syntax validation for: {args.directory}")
    print(f"File pattern: {args.pattern}")
    print("-" * 80)
    
    errors = validator.validate_directory(args.directory, args.pattern)
    
    # Generate and display report
    report = validator.generate_report()
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Validation report saved to: {args.output}")
    else:
        print(report)
    
    # Exit with appropriate code
    summary = validator.get_error_summary()
    if summary["has_critical_errors"]:
        sys.exit(2)  # Critical errors found
    elif summary["total_errors"] > 0:
        sys.exit(1)  # Non-critical errors found
    else:
        sys.exit(0)  # No errors found


if __name__ == "__main__":
    main()