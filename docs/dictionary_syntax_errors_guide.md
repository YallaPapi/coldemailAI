# Dictionary Syntax Errors in Pytest Files - Comprehensive Guide

**Task Reference**: 13.1 - Research-driven documentation of common dictionary syntax patterns  
**Created**: 2025-07-30  
**Purpose**: Catalog common Python dictionary syntax errors in pytest test files

## Overview

This guide documents common dictionary syntax errors encountered in pytest files, based on research into Python interpreter error messages and real-world pytest code patterns. These errors are particularly problematic because they often occur in complex test data structures and assertion dictionaries.

## Common Dictionary Syntax Error Categories

### 1. Unclosed Dictionary Braces

**Error Pattern**: Missing closing brace `}`  
**Python Error**: `SyntaxError: '{' was never closed`  
**Common Context**: Large test data dictionaries, nested structures

#### Examples:

```python
# INCORRECT - Missing closing brace
test_data = {
    "scenario_1": {
        "input": {"name": "John", "age": 30},
        "expected": {"status": "valid"}
    },
    "scenario_2": {
        "input": {"name": "Jane", "age": 25},
        "expected": {"status": "valid"}
    # Missing closing brace here
```

```python
# CORRECT - Properly closed
test_data = {
    "scenario_1": {
        "input": {"name": "John", "age": 30},
        "expected": {"status": "valid"}
    },
    "scenario_2": {
        "input": {"name": "Jane", "age": 25},
        "expected": {"status": "valid"}
    }
}
```

**Detection Line Pattern**: Error typically reported at end of file or next function definition

### 2. Mismatched Braces and Brackets

**Error Pattern**: Mixing `{` with `]` or `[` with `}`  
**Python Error**: `SyntaxError: closing parenthesis ']' does not match opening parenthesis '{'`  
**Common Context**: Complex nested data structures in parametrized tests

#### Examples:

```python
# INCORRECT - Mixed brackets and braces
@pytest.mark.parametrize("test_case", [
    {
        "data": ["item1", "item2"],
        "expected": {"count": 2]  # Should be }
    }
])
```

```python
# CORRECT - Consistent bracket/brace usage
@pytest.mark.parametrize("test_case", [
    {
        "data": ["item1", "item2"],
        "expected": {"count": 2}
    }
])
```

### 3. Missing Colons in Dictionary Definitions

**Error Pattern**: Missing `:` between key and value  
**Python Error**: `SyntaxError: invalid syntax`  
**Common Context**: Rapid test data entry, copy-paste errors

#### Examples:

```python
# INCORRECT - Missing colon
test_config = {
    "timeout" 30,  # Missing colon
    "retries": 3,
    "debug": True
}
```

```python
# CORRECT - Proper colon usage
test_config = {
    "timeout": 30,
    "retries": 3,
    "debug": True
}
```

### 4. Trailing Comma Issues

**Error Pattern**: Missing commas between dictionary items  
**Python Error**: `SyntaxError: invalid syntax`  
**Common Context**: Multi-line dictionary definitions

#### Examples:

```python
# INCORRECT - Missing comma
assertion_data = {
    "status": "success"
    "code": 200,  # Missing comma on previous line
    "message": "OK"
}
```

```python
# CORRECT - Proper comma placement
assertion_data = {
    "status": "success",
    "code": 200,
    "message": "OK"
}
```

### 5. Dictionary Comprehension Syntax Errors

**Error Pattern**: Malformed comprehension syntax  
**Python Error**: `SyntaxError: invalid syntax` or `SyntaxError: '{' was never closed`  
**Common Context**: Dynamic test data generation

#### Examples:

```python
# INCORRECT - Missing colon in comprehension
test_cases = {f"case_{i}" f"value_{i}" for i in range(5)}  # Missing colon
```

```python
# CORRECT - Proper comprehension syntax
test_cases = {f"case_{i}": f"value_{i}" for i in range(5)}
```

### 6. String Quote Mismatches in Dictionary Keys/Values

**Error Pattern**: Mixing single and double quotes incorrectly  
**Python Error**: `SyntaxError: EOL while scanning string literal`  
**Common Context**: Copy-paste from different sources, nested quotes

#### Examples:

```python
# INCORRECT - Mismatched quotes
test_strings = {
    "message": "He said, "Hello World"",  # Nested quotes issue
    "greeting': "Hi there"  # Mixed quote types
}
```

```python
# CORRECT - Consistent quote handling
test_strings = {
    "message": 'He said, "Hello World"',
    "greeting": "Hi there"
}
```

## Pytest-Specific Dictionary Error Contexts

### 1. Parametrized Test Data

Most common location for dictionary syntax errors in pytest files:

```python
# High-risk area for syntax errors
@pytest.mark.parametrize("input_data,expected", [
    ({"name": "John", "age": 30}, {"valid": True}),
    ({"name": "Jane", "age": 25}, {"valid": True}),
    # Complex nested structures prone to brace errors
])
```

### 2. Fixture Data Definitions

Second most common area:

```python
@pytest.fixture
def complex_test_data():
    return {
        "scenarios": {
            "positive": {...},  # Deep nesting increases error risk
            "negative": {...}
        }
    }
```

### 3. Assertion Dictionary Comparisons

Common in data validation tests:

```python
def test_data_processing():
    result = process_data(input_data)
    expected = {
        "processed": True,
        "count": 42,
        "items": [...]
    }  # Risk area for missing braces
    assert result == expected
```

## Error Detection Patterns

### Line Number Reporting Behavior

1. **Unclosed Braces**: Python reports error at file end or next function
2. **Mismatched Braces**: Reports at the mismatched character location  
3. **Missing Colons**: Reports at the problematic line
4. **Missing Commas**: Reports at the next line where syntax becomes invalid

### Common Error Message Patterns

```
SyntaxError: '{' was never closed (file.py, line N)
SyntaxError: closing parenthesis ']' does not match opening parenthesis '{' (file.py, line N)
SyntaxError: invalid syntax (file.py, line N)
SyntaxError: EOL while scanning string literal (file.py, line N)
```

## AST-Based Detection Strategy

### Key AST Node Types to Monitor

1. **Dict nodes**: Check for complete structure
2. **DictComp nodes**: Validate comprehension syntax
3. **Str/Constant nodes**: Verify string termination
4. **Call nodes**: Check parametrized test arguments

### Detection Algorithm Approach

```python
# Pseudocode for AST-based detection
def detect_dictionary_errors(ast_tree):
    for node in ast.walk(ast_tree):
        if isinstance(node, ast.Dict):
            # Check key-value pairing
            if len(node.keys) != len(node.values):
                report_mismatch_error()
        
        if isinstance(node, ast.DictComp):
            # Validate comprehension structure
            validate_comprehension_syntax(node)
```

## Prevention Best Practices

### 1. Consistent Formatting

- Use consistent indentation (4 spaces recommended)
- Align closing braces with opening structure
- Use trailing commas for multi-line dictionaries

### 2. IDE Configuration

- Enable bracket matching highlighting
- Configure syntax error underlining
- Use auto-formatting tools (black, autopep8)

### 3. Code Review Checklist

- Verify all opening braces have matching closing braces
- Check comma placement in multi-line structures
- Validate string quote consistency
- Review nested structure alignment

### 4. Testing Best Practices

```python
# Recommended structure for complex test data
@pytest.fixture
def test_scenarios():
    """Well-structured test data with clear formatting"""
    return {
        "valid_user": {
            "input": {"name": "John", "email": "john@example.com"},
            "expected": {"status": "created", "id": 123},
        },
        "invalid_email": {
            "input": {"name": "Jane", "email": "invalid-email"},
            "expected": {"status": "error", "message": "Invalid email"},
        },
    }  # Trailing comma prevents addition errors
```

## Integration with Pytest Workflows

### Pre-commit Hook Integration

```bash
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: check-dict-syntax
        name: Check Dictionary Syntax
        entry: python -m ast_dict_checker
        language: python
        files: '^tests/.*\.py$'
```

### IDE Integration Points

1. **Syntax highlighting** for unmatched braces
2. **Linting integration** with flake8/pylint
3. **Auto-completion** for dictionary structures
4. **Real-time error detection** during typing

## Real-World Error Examples from ColdEmailAI Project

### Case Study: tests/test_excel_export_functionality.py:98

**Original Error**:
```python
# Line 98 - Unclosed dictionary brace
test_data = {
    "headers": ["Name", "Company", "Email"],
    "records": [
        {"name": "John", "company": "ACME", "email": "john@acme.com"},
        {"name": "Jane", "company": "TechCorp", "email": "jane@techcorp.com"}
    # Missing closing brace - caused SyntaxError: '{' was never closed
```

**Resolution Applied**:
- Used AST parsing to identify exact location
- Added missing closing brace at line 98
- Implemented proper indentation alignment
- Added trailing comma for future additions

## Conclusion

Dictionary syntax errors in pytest files are common due to:
1. Complex nested test data structures
2. Large parametrized test datasets  
3. Copy-paste operations between test cases
4. Manual data entry in fixture definitions

The key to prevention is:
1. Consistent formatting practices
2. Automated syntax validation
3. IDE configuration for real-time detection
4. AST-based tooling for comprehensive checking

This documentation serves as the foundation for implementing AST-based syntax validation tools specifically designed for pytest dictionary structures.

---

**Implementation Status**: Task 13.1 COMPLETED  
**Next Steps**: Proceed to Task 13.2 - AST-Based Syntax Validation Development  
**Integration**: Ready for AST parser implementation and pytest workflow integration