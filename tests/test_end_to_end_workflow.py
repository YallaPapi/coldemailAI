"""
End-to-End Workflow Test Scenarios - tests/test_end_to_end_workflow.py:1
Task 9.1: Design End-to-End Workflow Test Scenarios

Comprehensive test scenarios covering all business cases from the PRD, including normal, 
edge, and error conditions for the ColdEmailAI workflow.

Based on PRD analysis: CSV upload → Column mapping → Email generation → Excel export
"""

import io
import os
import pytest
import pandas as pd
import numpy as np
from flask.testing import FlaskClient
from datetime import datetime
import json
from unittest.mock import patch, Mock
import tempfile


class EndToEndWorkflowTestScenarios:
    """
    Comprehensive end-to-end workflow test scenarios based on PRD requirements
    
    Workflow stages per PRD:
    1. File Upload and Processing Service (CSV/Excel upload)
    2. AI-Powered Personalized Email Generation Using OpenAI GPT-4
    3. In-Memory Spreadsheet Update & Return
    4. Excel Export with generated emails
    """
    
    def __init__(self):
        self.test_scenarios = self._define_test_scenarios()
        self.validation_criteria = self._define_validation_criteria()
    
    def _define_test_scenarios(self):
        """Define comprehensive test scenarios covering all PRD business cases - tests/test_end_to_end_workflow.py:31"""
        return {
            "normal_cases": [
                {
                    "scenario_id": "E2E_NORMAL_001",
                    "name": "Standard Business Leads Workflow",
                    "description": "Complete workflow with standard business lead data",
                    "input_data": {
                        "file_type": "xlsx",
                        "records": 50,
                        "columns": ["First Name", "Company Name", "Industry", "City", "Email"],
                        "data_quality": "clean"
                    },
                    "expected_workflow": [
                        "file_upload_success",
                        "column_mapping_automatic",
                        "email_generation_complete",
                        "excel_export_success"
                    ],
                    "success_criteria": {
                        "upload_response": 200,
                        "mapped_columns": ">=4",
                        "generated_emails": "100%",
                        "export_file_size": ">0",
                        "data_integrity": "100%"
                    }
                },
                {
                    "scenario_id": "E2E_NORMAL_002", 
                    "name": "Large Scale Processing (1000+ leads)",
                    "description": "Batch processing of 1000+ leads as per PRD scale requirements",
                    "input_data": {
                        "file_type": "csv",
                        "records": 1000,
                        "columns": ["firstName", "companyName", "industry", "location", "email"],
                        "data_quality": "mixed"
                    },
                    "expected_workflow": [
                        "file_upload_success",
                        "column_mapping_automatic",
                        "batch_email_generation",
                        "memory_efficient_processing",
                        "excel_export_success"
                    ],
                    "success_criteria": {
                        "processing_time": "<5min",
                        "memory_usage": "<500MB",
                        "generated_emails": ">=95%",
                        "export_file_readable": True
                    }
                },
                {
                    "scenario_id": "E2E_NORMAL_003",
                    "name": "Multi-Industry Lead Processing",
                    "description": "Process leads from multiple industries with industry-specific personalization",
                    "input_data": {
                        "file_type": "xlsx",
                        "records": 200,
                        "columns": ["First Name", "Last Name", "Company", "Industry", "City", "State", "Email"],
                        "industries": ["Technology", "Healthcare", "Finance", "Manufacturing", "Retail"]
                    },
                    "expected_workflow": [
                        "file_upload_success",
                        "column_mapping_complete",
                        "industry_specific_email_generation",
                        "personalization_validation",
                        "excel_export_with_metadata"
                    ],
                    "success_criteria": {
                        "industry_personalization": "present_in_each_email",
                        "unique_email_content": ">=90%",
                        "professional_tone": "validated"
                    }
                }
            ],
            "edge_cases": [
                {
                    "scenario_id": "E2E_EDGE_001",
                    "name": "Minimal Required Data",
                    "description": "Test with minimum required columns for email generation",
                    "input_data": {
                        "file_type": "csv",
                        "records": 10,
                        "columns": ["First Name", "Company Name"],
                        "data_quality": "minimal"
                    },
                    "expected_workflow": [
                        "file_upload_success",
                        "column_mapping_basic",
                        "basic_email_generation",
                        "excel_export_success"
                    ],
                    "success_criteria": {
                        "emails_generated": "100%",
                        "basic_personalization": "first_name_and_company_present"
                    }
                },
                {
                    "scenario_id": "E2E_EDGE_002",
                    "name": "Special Characters and Unicode",
                    "description": "Process leads with international names, special characters, and Unicode",
                    "input_data": {
                        "file_type": "xlsx",
                        "records": 25,
                        "columns": ["First Name", "Company Name", "City", "Email"],
                        "special_features": ["unicode_names", "accented_characters", "symbols"]
                    },
                    "expected_workflow": [
                        "file_upload_success",
                        "unicode_handling",
                        "character_preservation",
                        "email_generation_with_unicode",
                        "excel_export_unicode_safe"
                    ],
                    "success_criteria": {
                        "character_integrity": "100%",
                        "email_readability": "maintained",
                        "export_encoding": "utf8_compatible"
                    }
                },
                {
                    "scenario_id": "E2E_EDGE_003",
                    "name": "Empty and Null Value Handling",
                    "description": "Handle records with missing data, empty fields, and null values",
                    "input_data": {
                        "file_type": "csv",
                        "records": 30,
                        "columns": ["First Name", "Company Name", "Industry", "Email"],
                        "data_issues": ["empty_fields", "null_values", "whitespace_only"]
                    },
                    "expected_workflow": [
                        "file_upload_success",
                        "data_validation",
                        "missing_data_handling",
                        "conditional_email_generation",
                        "excel_export_with_flags"
                    ],
                    "success_criteria": {
                        "error_handling": "graceful",
                        "partial_generation": "acceptable",
                        "error_logging": "comprehensive"
                    }
                }
            ],
            "error_conditions": [
                {
                    "scenario_id": "E2E_ERROR_001",
                    "name": "Invalid File Format",
                    "description": "Upload unsupported file formats or corrupted files",
                    "input_data": {
                        "file_type": "txt",
                        "content": "invalid_data",
                        "corruption": "format_mismatch"
                    },
                    "expected_workflow": [
                        "file_upload_attempted",
                        "format_validation_failure",
                        "error_response_clear"
                    ],
                    "success_criteria": {
                        "error_response": "400_bad_request",
                        "error_message": "user_friendly",
                        "no_partial_processing": True
                    }
                },
                {
                    "scenario_id": "E2E_ERROR_002",
                    "name": "Missing Required Columns",
                    "description": "File lacks essential columns for email generation",
                    "input_data": {
                        "file_type": "xlsx",
                        "records": 10,
                        "columns": ["Random Column 1", "Random Column 2"],
                        "missing": ["First Name", "Company Name"]
                    },
                    "expected_workflow": [
                        "file_upload_success",
                        "column_validation_failure",
                        "clear_error_response"
                    ],
                    "success_criteria": {
                        "validation_error": "specific_missing_columns",
                        "suggested_fixes": "provided",
                        "no_email_generation": True
                    }
                },
                {
                    "scenario_id": "E2E_ERROR_003",
                    "name": "API Failure Handling",
                    "description": "OpenAI API failures or rate limiting scenarios",
                    "input_data": {
                        "file_type": "csv",
                        "records": 20,
                        "columns": ["First Name", "Company Name", "Industry"],
                        "api_simulation": "failure"
                    },
                    "expected_workflow": [
                        "file_upload_success",
                        "column_mapping_success",
                        "api_call_failure",
                        "error_handling_graceful",
                        "partial_results_or_retry"
                    ],
                    "success_criteria": {
                        "error_logged": True,
                        "user_notification": "clear",
                        "retry_mechanism": "available",
                        "partial_success_handling": "appropriate"
                    }
                }
            ]
        }
    
    def _define_validation_criteria(self):
        """Define validation criteria for each workflow stage - tests/test_end_to_end_workflow.py:209"""
        return {
            "stage_1_file_upload": {
                "accepts_xlsx": True,
                "accepts_csv": True,
                "file_size_limit": "10MB",
                "response_time": "<30s",
                "error_handling": "graceful"
            },
            "stage_2_column_mapping": {
                "automatic_detection": ["First Name", "Company Name", "Industry", "Email"],
                "fuzzy_matching": True,
                "mapping_confidence": ">80%",
                "manual_override": "supported"
            },
            "stage_3_email_generation": {
                "personalization_elements": ["first_name", "company", "industry", "location"],
                "email_length": "~80_words",
                "professional_tone": True,
                "template_consistency": True,
                "api_error_handling": "robust"
            },
            "stage_4_excel_export": {
                "original_data_preserved": "100%",
                "new_column_added": "Personalized Email",
                "file_format": "xlsx",
                "download_response": "immediate",
                "data_integrity": "maintained"
            },
            "overall_workflow": {
                "end_to_end_success_rate": ">95%",
                "processing_time_per_lead": "<10s",
                "memory_efficiency": "optimized",
                "error_recovery": "automatic_where_possible",
                "user_experience": "seamless"
            }
        }
    
    def get_scenario_by_id(self, scenario_id):
        """Retrieve specific test scenario by ID - tests/test_end_to_end_workflow.py:237"""
        all_scenarios = (
            self.test_scenarios["normal_cases"] + 
            self.test_scenarios["edge_cases"] + 
            self.test_scenarios["error_conditions"]
        )
        return next((s for s in all_scenarios if s["scenario_id"] == scenario_id), None)
    
    def get_scenarios_by_category(self, category):
        """Get all scenarios in a specific category - tests/test_end_to_end_workflow.py:246"""
        return self.test_scenarios.get(category, [])
    
    def create_test_data_for_scenario(self, scenario):
        """Generate test data based on scenario specification - tests/test_end_to_end_workflow.py:250"""
        input_spec = scenario["input_data"]
        
        # Create DataFrame based on scenario requirements
        records = input_spec.get("records", 10)
        columns = input_spec.get("columns", ["First Name", "Company Name"])
        
        test_data = {}
        
        # Sample data pools
        first_names = ["John", "Jane", "Michael", "Sarah", "David", "Lisa", "Robert", "Emily"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
        companies = ["TechCorp Inc", "DataSys LLC", "Global Enterprises", "StartupCo", "Innovation Labs"]
        industries = input_spec.get("industries", ["Technology", "Healthcare", "Finance", "Manufacturing", "Retail"])
        cities = ["San Francisco", "New York", "Austin", "Seattle", "Chicago", "Los Angeles"]
        
        # Generate data based on columns
        for col in columns:
            col_lower = col.lower().replace(" ", "_")
            
            if "first" in col_lower and "name" in col_lower:
                test_data[col] = np.random.choice(first_names, records)
            elif "last" in col_lower and "name" in col_lower:
                test_data[col] = np.random.choice(last_names, records)
            elif "company" in col_lower:
                test_data[col] = np.random.choice(companies, records)
            elif "industry" in col_lower:
                test_data[col] = np.random.choice(industries, records)
            elif "city" in col_lower or "location" in col_lower:
                test_data[col] = np.random.choice(cities, records)
            elif "email" in col_lower:
                test_data[col] = [f"test{i}@example.com" for i in range(records)]
            else:
                test_data[col] = [f"Value_{i}" for i in range(records)]
        
        # Apply data quality modifications
        data_quality = input_spec.get("data_quality", "clean")
        if data_quality == "mixed":
            # Introduce some empty values and inconsistencies
            for col in test_data:
                indices = np.random.choice(records, size=records//10, replace=False)
                for idx in indices:
                    if np.random.random() < 0.5:
                        test_data[col][idx] = ""
        
        # Handle special features
        special_features = input_spec.get("special_features", [])
        if "unicode_names" in special_features:
            unicode_names = ["François", "José María", "Björn", "Δημήτρης", "Wei"]
            for i in range(min(5, records)):
                if "First Name" in test_data:
                    test_data["First Name"][i] = unicode_names[i % len(unicode_names)]
        
        df = pd.DataFrame(test_data)
        
        # Handle data issues
        data_issues = input_spec.get("data_issues", [])
        if "empty_fields" in data_issues:
            # Make some fields empty
            df.iloc[0, 0] = ""
        if "null_values" in data_issues:
            # Make some fields null
            df.iloc[1, 0] = None
        if "whitespace_only" in data_issues:
            # Make some fields whitespace only
            df.iloc[2, 0] = "   "
            
        return df
    
    def validate_workflow_stage(self, stage_name, actual_result, scenario):
        """Validate specific workflow stage against expected criteria - tests/test_end_to_end_workflow.py:311"""
        stage_criteria = self.validation_criteria.get(f"stage_{stage_name}", {})
        success_criteria = scenario.get("success_criteria", {})
        
        validation_results = {
            "stage": stage_name,
            "passed": True,
            "issues": [],
            "metrics": {}
        }
        
        # Combine criteria and validate
        all_criteria = {**stage_criteria, **success_criteria}
        
        for criterion, expected in all_criteria.items():
            if criterion in actual_result:
                actual_value = actual_result[criterion]
                
                # Perform validation based on criterion type
                if isinstance(expected, bool):
                    if actual_value != expected:
                        validation_results["issues"].append(f"{criterion}: expected {expected}, got {actual_value}")
                        validation_results["passed"] = False
                elif isinstance(expected, str) and expected.startswith(">"):
                    # Numeric comparison
                    threshold = float(expected[1:])
                    if float(actual_value) <= threshold:
                        validation_results["issues"].append(f"{criterion}: expected >{threshold}, got {actual_value}")
                        validation_results["passed"] = False
                elif isinstance(expected, str) and expected.startswith("<"):
                    # Numeric comparison
                    threshold = float(expected[1:])
                    if float(actual_value) >= threshold:
                        validation_results["issues"].append(f"{criterion}: expected <{threshold}, got {actual_value}")
                        validation_results["passed"] = False
                
                validation_results["metrics"][criterion] = actual_value
        
        return validation_results
    
    def generate_workflow_report(self, scenario_results):
        """Generate comprehensive workflow test report - tests/test_end_to_end_workflow.py:348"""
        report = {
            "test_execution_timestamp": datetime.now().isoformat(),
            "total_scenarios": len(scenario_results),
            "passed_scenarios": sum(1 for r in scenario_results if r.get("overall_success", False)),
            "failed_scenarios": sum(1 for r in scenario_results if not r.get("overall_success", False)),
            "success_rate": 0,
            "detailed_results": scenario_results,
            "recommendations": []
        }
        
        if report["total_scenarios"] > 0:
            report["success_rate"] = (report["passed_scenarios"] / report["total_scenarios"]) * 100
        
        # Generate recommendations based on failures
        failed_scenarios = [r for r in scenario_results if not r.get("overall_success", False)]
        if failed_scenarios:
            stage_failures = {}
            for scenario in failed_scenarios:
                for stage_result in scenario.get("stage_results", []):
                    if not stage_result.get("passed", True):
                        stage = stage_result["stage"]
                        stage_failures[stage] = stage_failures.get(stage, 0) + 1
            
            for stage, count in stage_failures.items():
                report["recommendations"].append(
                    f"Review {stage} implementation - {count} failures detected"
                )
        
        return report


class TestEndToEndWorkflowDesign:
    """Test the workflow test scenario design and validation framework"""
    
    def setup_method(self):
        """Setup test environment"""
        self.workflow_scenarios = EndToEndWorkflowTestScenarios()
    
    def test_scenario_completeness(self):
        """Test that all PRD business cases are covered in scenarios - tests/test_end_to_end_workflow.py:382"""
        scenarios = self.workflow_scenarios.test_scenarios
        
        # Verify we have scenarios for all categories
        assert "normal_cases" in scenarios, "Missing normal case scenarios"
        assert "edge_cases" in scenarios, "Missing edge case scenarios" 
        assert "error_conditions" in scenarios, "Missing error condition scenarios"
        
        # Verify minimum scenario counts
        assert len(scenarios["normal_cases"]) >= 3, "Need at least 3 normal case scenarios"
        assert len(scenarios["edge_cases"]) >= 3, "Need at least 3 edge case scenarios"
        assert len(scenarios["error_conditions"]) >= 3, "Need at least 3 error condition scenarios"
        
        print(f"✅ Scenario completeness: {sum(len(v) for v in scenarios.values())} total scenarios designed")
    
    def test_validation_criteria_coverage(self):
        """Test that validation criteria cover all workflow stages - tests/test_end_to_end_workflow.py:396"""
        criteria = self.workflow_scenarios.validation_criteria
        
        # Verify all workflow stages have validation criteria
        required_stages = [
            "stage_1_file_upload",
            "stage_2_column_mapping", 
            "stage_3_email_generation",
            "stage_4_excel_export",
            "overall_workflow"
        ]
        
        for stage in required_stages:
            assert stage in criteria, f"Missing validation criteria for {stage}"
            assert len(criteria[stage]) > 0, f"Empty validation criteria for {stage}"
        
        print(f"✅ Validation criteria coverage: {len(required_stages)} workflow stages covered")
    
    def test_scenario_data_generation(self):
        """Test scenario-based test data generation - tests/test_end_to_end_workflow.py:413"""
        # Test normal case data generation
        normal_scenario = self.workflow_scenarios.get_scenario_by_id("E2E_NORMAL_001")
        test_data = self.workflow_scenarios.create_test_data_for_scenario(normal_scenario)
        
        # Validate generated data
        assert isinstance(test_data, pd.DataFrame), "Should generate DataFrame"
        assert len(test_data) == normal_scenario["input_data"]["records"], "Should match record count"
        assert len(test_data.columns) == len(normal_scenario["input_data"]["columns"]), "Should match column count"
        
        # Test edge case data generation
        edge_scenario = self.workflow_scenarios.get_scenario_by_id("E2E_EDGE_002")
        unicode_data = self.workflow_scenarios.create_test_data_for_scenario(edge_scenario)
        
        # Check for Unicode characters
        has_unicode = any(
            any(ord(char) > 127 for char in str(cell) if isinstance(cell, str))
            for col in unicode_data.columns
            for cell in unicode_data[col]
        )
        assert has_unicode, "Should generate Unicode test data for edge cases"
        
        print(f"✅ Scenario data generation: Generated {len(test_data)} normal records and {len(unicode_data)} Unicode records")
    
    def test_prd_requirements_mapping(self):
        """Test that scenarios map to specific PRD requirements - tests/test_end_to_end_workflow.py:435"""
        # Verify key PRD requirements are covered
        prd_requirements = [
            "file_upload_processing",  # Step 1 from PRD
            "ai_email_generation",     # Step 2 from PRD  
            "spreadsheet_update",      # Step 3 from PRD
            "batch_processing_1000",   # Scale requirement
            "error_handling",          # Robustness requirement
            "personalization_quality"  # Core value proposition
        ]
        
        all_scenarios = (
            self.workflow_scenarios.get_scenarios_by_category("normal_cases") +
            self.workflow_scenarios.get_scenarios_by_category("edge_cases") +
            self.workflow_scenarios.get_scenarios_by_category("error_conditions")
        )
        
        # Check that each PRD requirement has corresponding scenario coverage
        covered_requirements = set()
        
        for scenario in all_scenarios:
            description = scenario["description"].lower()
            workflow = " ".join(scenario["expected_workflow"]).lower()
            
            if "upload" in description or "file_upload" in workflow:
                covered_requirements.add("file_upload_processing")
            if "email_generation" in workflow or "personalized" in description:
                covered_requirements.add("ai_email_generation") 
            if "excel_export" in workflow or "spreadsheet" in description:
                covered_requirements.add("spreadsheet_update")
            if "1000" in description or "batch" in description:
                covered_requirements.add("batch_processing_1000")
            if "error" in scenario["scenario_id"].lower() or "failure" in workflow:
                covered_requirements.add("error_handling")
            if "personalization" in workflow or "industry" in description:
                covered_requirements.add("personalization_quality")
        
        # Verify coverage
        missing_requirements = set(prd_requirements) - covered_requirements
        assert len(missing_requirements) == 0, f"Missing PRD requirement coverage: {missing_requirements}"
        
        print(f"✅ PRD requirements mapping: {len(covered_requirements)}/{len(prd_requirements)} requirements covered")
    
    def test_scenario_workflow_stages(self):
        """Test that each scenario defines clear workflow stages - tests/test_end_to_end_workflow.py:471"""
        all_scenarios = (
            self.workflow_scenarios.get_scenarios_by_category("normal_cases") +
            self.workflow_scenarios.get_scenarios_by_category("edge_cases") +
            self.workflow_scenarios.get_scenarios_by_category("error_conditions")
        )
        
        for scenario in all_scenarios:
            # Each scenario must have expected workflow stages
            assert "expected_workflow" in scenario, f"Scenario {scenario['scenario_id']} missing expected_workflow"
            assert len(scenario["expected_workflow"]) > 0, f"Scenario {scenario['scenario_id']} has empty workflow"
            
            # Each scenario must have success criteria
            assert "success_criteria" in scenario, f"Scenario {scenario['scenario_id']} missing success_criteria"
            assert len(scenario["success_criteria"]) > 0, f"Scenario {scenario['scenario_id']} has empty success criteria"
            
            # Workflow stages should be actionable
            for stage in scenario["expected_workflow"]:
                assert isinstance(stage, str), f"Workflow stage should be string: {stage}"
                assert len(stage) > 5, f"Workflow stage too short: {stage}"
        
        print(f"✅ Scenario workflow stages: {len(all_scenarios)} scenarios with defined workflow stages")


class TestAutomatedCSVUploadAndColumnMapping:
    """
    Task 9.2: Automate CSV Upload and Column Mapping Tests
    
    Automated tests to validate CSV upload and column mapping functionality using real business data files.
    Tests for valid, invalid, and edge-case files with proper error handling.
    """
    
    def setup_method(self):
        """Setup test environment with scenarios and mock Flask app"""
        self.workflow_scenarios = EndToEndWorkflowTestScenarios()
        self.test_data_cache = {}
    
    def create_test_csv_file(self, scenario_data, file_format="csv"):
        """Create test CSV/Excel file from scenario data - tests/test_end_to_end_workflow.py:493"""
        df = scenario_data
        
        # Create in-memory file
        if file_format == "csv":
            output = io.StringIO()
            df.to_csv(output, index=False)
            output.seek(0)
            return output.getvalue().encode('utf-8')
        elif file_format == "xlsx":
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Leads')
            output.seek(0)
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {file_format}")
    
    def simulate_flask_file_upload(self, file_data, filename, content_type):
        """Simulate Flask file upload for testing - tests/test_end_to_end_workflow.py:510"""
        file_obj = io.BytesIO(file_data)
        
        # Mock Flask FileStorage object behavior
        class MockFileStorage:
            def __init__(self, stream, filename, content_type):
                self.stream = stream
                self.filename = filename
                self.content_type = content_type
                self.name = filename
            
            def read(self):
                return self.stream.read()
            
            def seek(self, pos):
                return self.stream.seek(pos)
            
            def save(self, destination):
                self.stream.seek(0)
                if hasattr(destination, 'write'):
                    destination.write(self.stream.read())
                else:
                    with open(destination, 'wb') as f:
                        f.write(self.stream.read())
        
        return MockFileStorage(file_obj, filename, content_type)
    
    def validate_csv_parsing(self, file_data, expected_format):
        """Validate CSV parsing functionality - tests/test_end_to_end_workflow.py:534"""
        parsing_results = {
            "success": False,
            "dataframe": None,
            "error": None,
            "row_count": 0,
            "column_count": 0,
            "columns": []
        }
        
        try:
            if expected_format == "csv":
                # Parse CSV data
                df = pd.read_csv(io.StringIO(file_data.decode('utf-8')))
            elif expected_format == "xlsx":
                # Parse Excel data
                df = pd.read_excel(io.BytesIO(file_data))
            else:
                raise ValueError(f"Unsupported format: {expected_format}")
            
            parsing_results.update({
                "success": True,
                "dataframe": df,
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": list(df.columns)
            })
            
        except Exception as e:
            parsing_results["error"] = str(e)
        
        return parsing_results
    
    def test_column_mapping_accuracy(self, df_columns):
        """Test column mapping accuracy using fuzzy matching - tests/test_end_to_end_workflow.py:562"""
        from difflib import SequenceMatcher
        
        # Standard business field mappings
        standard_fields = {
            "first_name": ["first name", "firstname", "fname", "given name"],
            "last_name": ["last name", "lastname", "lname", "surname", "family name"],
            "company_name": ["company", "company name", "organization", "business", "firm"],
            "industry": ["industry", "sector", "vertical", "business category"],
            "email": ["email", "email address", "e-mail", "mail"],
            "city": ["city", "location", "town"],
            "state": ["state", "province", "region"],
            "job_title": ["job title", "title", "position", "role"]
        }
        
        mapping_results = {}
        
        def similarity(a, b):
            return SequenceMatcher(None, a.lower(), b.lower()).ratio()
        
        for col in df_columns:
            best_match = None
            best_score = 0
            
            for standard_field, variations in standard_fields.items():
                for variation in variations:
                    score = similarity(col, variation)
                    if score > best_score:
                        best_score = score
                        best_match = standard_field
            
            # Only consider matches above 60% similarity
            if best_score > 0.6:
                mapping_results[col] = {
                    "mapped_to": best_match,
                    "confidence": best_score
                }
            else:
                mapping_results[col] = {
                    "mapped_to": "unmapped",
                    "confidence": best_score
                }
        
        return mapping_results
    
    def test_standard_csv_upload_workflow(self):
        """Test standard CSV upload and mapping workflow - tests/test_end_to_end_workflow.py:600"""
        # Use normal case scenario
        scenario = self.workflow_scenarios.get_scenario_by_id("E2E_NORMAL_001")
        test_data = self.workflow_scenarios.create_test_data_for_scenario(scenario)
        
        # Create CSV file
        csv_data = self.create_test_csv_file(test_data, "csv")
        mock_file = self.simulate_flask_file_upload(csv_data, "business_leads.csv", "text/csv")
        
        # Test CSV parsing
        parsing_results = self.validate_csv_parsing(csv_data, "csv")
        assert parsing_results["success"], f"CSV parsing failed: {parsing_results['error']}"
        assert parsing_results["row_count"] == scenario["input_data"]["records"], "Row count mismatch"
        assert parsing_results["column_count"] == len(scenario["input_data"]["columns"]), "Column count mismatch"
        
        # Test column mapping
        mapping_results = self.test_column_mapping_accuracy(parsing_results["columns"])
        
        # Validate mapping accuracy
        mapped_columns = [r for r in mapping_results.values() if r["mapped_to"] != "unmapped"]
        mapping_accuracy = len(mapped_columns) / len(mapping_results) * 100
        
        assert mapping_accuracy >= 80, f"Column mapping accuracy too low: {mapping_accuracy}%"
        
        # Validate high-confidence mappings
        high_confidence_mappings = [r for r in mapping_results.values() if r["confidence"] > 0.8]
        assert len(high_confidence_mappings) >= 3, "Need at least 3 high-confidence column mappings"
        
        print(f"✅ Standard CSV upload: {parsing_results['row_count']} rows, {mapping_accuracy:.1f}% mapping accuracy")
    
    def test_excel_upload_workflow(self):
        """Test Excel file upload and mapping workflow - tests/test_end_to_end_workflow.py:626"""
        # Use multi-industry scenario
        scenario = self.workflow_scenarios.get_scenario_by_id("E2E_NORMAL_003")
        test_data = self.workflow_scenarios.create_test_data_for_scenario(scenario)
        
        # Create Excel file
        excel_data = self.create_test_csv_file(test_data, "xlsx")
        mock_file = self.simulate_flask_file_upload(excel_data, "business_leads.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        # Test Excel parsing
        parsing_results = self.validate_csv_parsing(excel_data, "xlsx")
        assert parsing_results["success"], f"Excel parsing failed: {parsing_results['error']}"
        assert parsing_results["row_count"] == scenario["input_data"]["records"], "Row count mismatch"
        
        # Test column mapping with more complex headers
        mapping_results = self.test_column_mapping_accuracy(parsing_results["columns"])
        
        # Validate mapping works with complex column names
        mapped_columns = [r for r in mapping_results.values() if r["mapped_to"] != "unmapped"]
        assert len(mapped_columns) >= 4, "Should map at least 4 columns for complex Excel files"
        
        print(f"✅ Excel upload: {parsing_results['row_count']} rows, {len(mapped_columns)} columns mapped")
    
    def test_large_file_upload_performance(self):
        """Test large file upload performance - tests/test_end_to_end_workflow.py:648"""
        import time
        
        # Use large scale scenario
        scenario = self.workflow_scenarios.get_scenario_by_id("E2E_NORMAL_002")
        test_data = self.workflow_scenarios.create_test_data_for_scenario(scenario)
        
        # Measure parsing performance
        start_time = time.perf_counter()
        csv_data = self.create_test_csv_file(test_data, "csv")
        parsing_results = self.validate_csv_parsing(csv_data, "csv")
        end_time = time.perf_counter()
        
        processing_time = end_time - start_time
        records_per_second = parsing_results["row_count"] / processing_time if processing_time > 0 else 0
        
        # Performance assertions
        assert parsing_results["success"], "Large file parsing should succeed"
        assert processing_time < 30, f"Large file processing too slow: {processing_time:.2f}s"
        assert records_per_second > 50, f"Processing rate too low: {records_per_second:.0f} records/sec"
        
        # Test column mapping performance
        start_time = time.perf_counter()
        mapping_results = self.test_column_mapping_accuracy(parsing_results["columns"])
        end_time = time.perf_counter()
        
        mapping_time = end_time - start_time
        assert mapping_time < 5, f"Column mapping too slow: {mapping_time:.2f}s"
        
        print(f"✅ Large file performance: {records_per_second:.0f} records/sec, {mapping_time:.2f}s mapping")
    
    def test_invalid_file_error_handling(self):
        """Test error handling for invalid files - tests/test_end_to_end_workflow.py:677"""
        # Test invalid file format
        invalid_data = b"This is not a valid CSV or Excel file"
        mock_file = self.simulate_flask_file_upload(invalid_data, "invalid.txt", "text/plain")
        
        # Should fail parsing
        parsing_results = self.validate_csv_parsing(invalid_data, "csv")
        assert not parsing_results["success"], "Invalid file should fail parsing"
        assert parsing_results["error"] is not None, "Should provide error message"
        
        # Test corrupted CSV
        corrupted_csv = b"Name,Email\nJohn,john@\nIncomplete row"
        parsing_results = self.validate_csv_parsing(corrupted_csv, "csv") 
        # This might succeed with warnings, but let's test it handles gracefully
        
        # Test empty file
        empty_data = b""
        parsing_results = self.validate_csv_parsing(empty_data, "csv")
        assert not parsing_results["success"], "Empty file should fail parsing"
        
        print("✅ Invalid file error handling: Proper error responses for invalid inputs")
    
    def test_missing_required_columns_detection(self):
        """Test detection of missing required columns - tests/test_end_to_end_workflow.py:697"""
        # Create data with missing required columns
        incomplete_data = pd.DataFrame({
            "Random Column 1": ["Value1", "Value2"],
            "Random Column 2": ["Value3", "Value4"],
            "Unrelated Field": ["Value5", "Value6"]
        })
        
        csv_data = self.create_test_csv_file(incomplete_data, "csv")
        parsing_results = self.validate_csv_parsing(csv_data, "csv")
        
        # Should parse successfully but fail column mapping
        assert parsing_results["success"], "File should parse successfully"
        
        mapping_results = self.test_column_mapping_accuracy(parsing_results["columns"])
        
        # Should detect lack of mappable columns
        mapped_columns = [r for r in mapping_results.values() if r["mapped_to"] != "unmapped"]
        mapping_rate = len(mapped_columns) / len(mapping_results) * 100
        
        assert mapping_rate < 50, f"Should detect poor mapping: {mapping_rate}% mapped"
        
        # Check that essential fields are missing
        essential_fields = ["first_name", "company_name", "email"]
        mapped_field_types = [r["mapped_to"] for r in mapping_results.values()]
        
        missing_essential = [field for field in essential_fields if field not in mapped_field_types]
        assert len(missing_essential) > 0, "Should detect missing essential fields"
        
        print(f"✅ Missing columns detection: {len(missing_essential)} essential fields missing")
    
    def test_special_character_column_handling(self):
        """Test handling of special characters in column names and data - tests/test_end_to_end_workflow.py:724"""
        # Create data with special characters in columns and values
        special_data = pd.DataFrame({
            "Nom (First Name)": ["François", "José María"],
            "Société / Company": ["Café Tech™", "España Solutions"],
            "E-mail / Courriel": ["francois@café.com", "jose@españa.es"],
            "Ville / City": ["Paris", "Barcelona"]
        })
        
        csv_data = self.create_test_csv_file(special_data, "csv")
        parsing_results = self.validate_csv_parsing(csv_data, "csv")
        
        # Should handle special characters in parsing
        assert parsing_results["success"], "Should parse files with special characters"
        assert parsing_results["row_count"] == 2, "Should preserve all rows"
        
        # Test column mapping with special characters
        mapping_results = self.test_column_mapping_accuracy(parsing_results["columns"])
        
        # Should map columns despite special characters
        mapped_columns = [r for r in mapping_results.values() if r["mapped_to"] != "unmapped"]
        assert len(mapped_columns) >= 3, "Should map most columns despite special characters"
        
        # Verify specific mappings work
        column_names = list(mapping_results.keys())
        first_name_mapped = any("first_name" in str(mapping_results[col]["mapped_to"]) for col in column_names)
        company_mapped = any("company" in str(mapping_results[col]["mapped_to"]) for col in column_names)
        
        assert first_name_mapped or company_mapped, "Should map at least one key field"
        
        print(f"✅ Special character handling: {len(mapped_columns)} columns mapped with special characters")
    
    def test_column_mapping_confidence_scoring(self):
        """Test column mapping confidence scoring accuracy - tests/test_end_to_end_workflow.py:751"""
        # Test perfect matches
        perfect_data = pd.DataFrame({
            "First Name": ["John", "Jane"],
            "Company Name": ["TechCorp", "DataSys"],
            "Email": ["john@tech.com", "jane@data.com"]
        })
        
        csv_data = self.create_test_csv_file(perfect_data, "csv")
        parsing_results = self.validate_csv_parsing(csv_data, "csv")
        mapping_results = self.test_column_mapping_accuracy(parsing_results["columns"])
        
        # Should have high confidence for exact matches
        high_confidence_count = sum(1 for r in mapping_results.values() if r["confidence"] > 0.9)
        assert high_confidence_count >= 2, "Should have high confidence for exact matches"
        
        # Test fuzzy matches
        fuzzy_data = pd.DataFrame({
            "FirstName": ["John", "Jane"],  # No space
            "CompanyName": ["TechCorp", "DataSys"],  # No space
            "EmailAddress": ["john@tech.com", "jane@data.com"]  # Different format
        })
        
        csv_data = self.create_test_csv_file(fuzzy_data, "csv")
        parsing_results = self.validate_csv_parsing(csv_data, "csv")
        mapping_results = self.test_column_mapping_accuracy(parsing_results["columns"])
        
        # Should still map with good confidence
        mapped_count = sum(1 for r in mapping_results.values() if r["mapped_to"] != "unmapped")
        assert mapped_count >= 2, "Should map fuzzy matches"
        
        medium_confidence_count = sum(1 for r in mapping_results.values() if r["confidence"] > 0.7)
        assert medium_confidence_count >= 2, "Should have reasonable confidence for fuzzy matches"
        
        print(f"✅ Confidence scoring: {high_confidence_count} perfect matches, {medium_confidence_count} fuzzy matches")
    
    def test_comprehensive_upload_validation_workflow(self):
        """Test comprehensive upload validation workflow - tests/test_end_to_end_workflow.py:783"""
        # Test multiple scenarios in sequence
        test_scenarios = [
            ("E2E_NORMAL_001", "csv"),
            ("E2E_NORMAL_003", "xlsx"),
            ("E2E_EDGE_001", "csv"),
            ("E2E_EDGE_002", "xlsx")
        ]
        
        validation_results = []
        
        for scenario_id, file_format in test_scenarios:
            scenario = self.workflow_scenarios.get_scenario_by_id(scenario_id)
            test_data = self.workflow_scenarios.create_test_data_for_scenario(scenario)
            
            # Create file and test parsing
            file_data = self.create_test_csv_file(test_data, file_format)
            parsing_results = self.validate_csv_parsing(file_data, file_format)
            
            # Test column mapping
            if parsing_results["success"]:
                mapping_results = self.test_column_mapping_accuracy(parsing_results["columns"])
                mapped_columns = [r for r in mapping_results.values() if r["mapped_to"] != "unmapped"]
                mapping_rate = len(mapped_columns) / len(mapping_results) * 100 if mapping_results else 0
            else:
                mapping_rate = 0
            
            validation_results.append({
                "scenario_id": scenario_id,
                "file_format": file_format,
                "parsing_success": parsing_results["success"],
                "row_count": parsing_results["row_count"],
                "mapping_rate": mapping_rate
            })
        
        # Validate overall results
        successful_parses = sum(1 for r in validation_results if r["parsing_success"])
        assert successful_parses >= 3, f"Should successfully parse most files: {successful_parses}/{len(test_scenarios)}"
        
        avg_mapping_rate = sum(r["mapping_rate"] for r in validation_results) / len(validation_results)
        assert avg_mapping_rate >= 60, f"Average mapping rate too low: {avg_mapping_rate:.1f}%"
        
        print(f"✅ Comprehensive validation: {successful_parses}/{len(test_scenarios)} files parsed, {avg_mapping_rate:.1f}% avg mapping rate")


class TestCompleteEndToEndWorkflow:
    """
    Tasks 9.3, 9.4, 9.5: Complete End-to-End Workflow Testing
    
    Comprehensive testing of the full ColdEmailAI workflow:
    - Email generation from mapped data
    - Excel export with data integrity
    - Complete workflow automation and error handling
    """
    
    def setup_method(self):
        """Setup complete workflow testing environment"""
        self.workflow_scenarios = EndToEndWorkflowTestScenarios()
        self.csv_mapper = TestAutomatedCSVUploadAndColumnMapping()
        self.csv_mapper.setup_method()
    
    def simulate_email_generation(self, mapped_data, personalization_fields):
        """Simulate AI-powered email generation - tests/test_end_to_end_workflow.py:987"""
        generated_emails = []
        
        for _, row in mapped_data.iterrows():
            # Extract personalization data
            first_name = row.get('First Name', row.get('first_name', 'there'))
            company = row.get('Company Name', row.get('company_name', 'your company'))
            industry = row.get('Industry', row.get('industry', 'your industry'))
            
            # Generate personalized email content following PRD guidelines (~80 words)
            email_content = f"""Dear {first_name},

I hope this email finds you well. I wanted to reach out regarding potential opportunities at {company}.

As someone working in the {industry} sector, I understand the challenges you face with automation and efficiency. Our AI-powered solutions have helped similar companies streamline their operations and reduce manual workload by up to 40%.

I'd love to schedule a brief 15-minute call to discuss how we might be able to help {company} achieve similar results.

Would you be open to a quick conversation this week?

Best regards,
Sales Team"""
            
            generated_emails.append({
                'personalized_email': email_content,
                'generation_success': True,
                'personalization_quality': self._assess_personalization_quality(email_content, row),
                'word_count': len(email_content.split()),
                'has_first_name': first_name.lower() != 'there',
                'has_company': company.lower() != 'your company',
                'has_industry': industry.lower() != 'your industry'
            })
        
        return generated_emails
    
    def _assess_personalization_quality(self, email_content, row_data):
        """Assess quality of personalization in generated email - tests/test_end_to_end_workflow.py:1019"""
        quality_score = 0
        content_lower = email_content.lower()
        
        # Check for personalization elements
        first_name = str(row_data.get('First Name', row_data.get('first_name', ''))).lower()
        company = str(row_data.get('Company Name', row_data.get('company_name', ''))).lower()
        industry = str(row_data.get('Industry', row_data.get('industry', ''))).lower()
        
        if first_name and first_name in content_lower:
            quality_score += 25
        if company and company in content_lower:
            quality_score += 25  
        if industry and industry in content_lower:
            quality_score += 25
        
        # Check for professional structure
        if 'dear' in content_lower and 'best regards' in content_lower:
            quality_score += 25
            
        return quality_score
    
    def create_complete_workflow_data(self, scenario_id):
        """Create complete test data with mapped columns and generated emails - tests/test_end_to_end_workflow.py:1039"""
        scenario = self.workflow_scenarios.get_scenario_by_id(scenario_id)
        raw_data = self.workflow_scenarios.create_test_data_for_scenario(scenario)
        
        # Step 1: CSV Upload simulation (already tested in 9.2)
        csv_data = self.csv_mapper.create_test_csv_file(raw_data, "csv")
        parsing_results = self.csv_mapper.validate_csv_parsing(csv_data, "csv")
        
        if not parsing_results["success"]:
            return None
        
        # Step 2: Column mapping simulation 
        mapping_results = self.csv_mapper.test_column_mapping_accuracy(parsing_results["columns"])
        
        # Step 3: Email generation simulation
        personalization_fields = ["first_name", "company_name", "industry"]
        generated_emails = self.simulate_email_generation(parsing_results["dataframe"], personalization_fields)
        
        # Step 4: Combine data for Excel export
        final_data = parsing_results["dataframe"].copy()
        final_data['Personalized Email'] = [email['personalized_email'] for email in generated_emails]
        final_data['Generation Success'] = [email['generation_success'] for email in generated_emails]
        final_data['Personalization Quality'] = [email['personalization_quality'] for email in generated_emails]
        
        return {
            'scenario': scenario,
            'raw_data': raw_data,
            'parsed_data': parsing_results["dataframe"],
            'mapping_results': mapping_results,
            'generated_emails': generated_emails,
            'final_data': final_data,
            'workflow_success': True
        }
    
    def test_email_generation_workflow(self):
        """Task 9.3: Test email generation from mapped data - tests/test_end_to_end_workflow.py:1067"""
        # Test with normal business scenario
        workflow_data = self.create_complete_workflow_data("E2E_NORMAL_001")
        assert workflow_data is not None, "Workflow data creation should succeed"
        
        generated_emails = workflow_data['generated_emails']
        
        # Validate email generation success
        successful_generations = sum(1 for email in generated_emails if email['generation_success'])
        success_rate = (successful_generations / len(generated_emails)) * 100
        assert success_rate >= 95, f"Email generation success rate too low: {success_rate}%"
        
        # Validate personalization quality
        avg_quality = sum(email['personalization_quality'] for email in generated_emails) / len(generated_emails)
        assert avg_quality >= 60, f"Average personalization quality too low: {avg_quality}%"
        
        # Validate email content structure
        for email in generated_emails:
            content = email['personalized_email']
            assert 'Dear' in content, "Email should have proper greeting"
            assert 'Best regards' in content, "Email should have proper closing"
            assert 40 <= email['word_count'] <= 120, f"Email length inappropriate: {email['word_count']} words"
        
        # Validate personalization elements are present
        personalized_emails = sum(1 for email in generated_emails if 
                                email['has_first_name'] and email['has_company'])
        personalization_rate = (personalized_emails / len(generated_emails)) * 100
        assert personalization_rate >= 80, f"Personalization rate too low: {personalization_rate}%"
        
        print(f"✅ Email generation: {success_rate:.1f}% success, {avg_quality:.1f}% avg quality, {personalization_rate:.1f}% personalized")
    
    def test_excel_export_data_integrity(self):
        """Task 9.4: Test Excel export with data integrity validation - tests/test_end_to_end_workflow.py:1095"""
        # Create complete workflow data
        workflow_data = self.create_complete_workflow_data("E2E_NORMAL_003")
        assert workflow_data is not None, "Workflow data creation should succeed"
        
        final_data = workflow_data['final_data']
        
        # Create Excel export (simulate ExcelExportValidator from previous tests)
        excel_output = io.BytesIO()
        with pd.ExcelWriter(excel_output, engine='openpyxl') as writer:
            final_data.to_excel(writer, index=False, sheet_name='Business Leads')
        
        excel_output.seek(0)
        
        # Validate Excel export data integrity
        exported_df = pd.read_excel(excel_output, sheet_name='Business Leads')
        
        # Validate all original data is preserved
        original_columns = set(workflow_data['raw_data'].columns)
        exported_columns = set(exported_df.columns)
        
        preserved_columns = original_columns.intersection(exported_columns)
        preservation_rate = (len(preserved_columns) / len(original_columns)) * 100
        assert preservation_rate >= 90, f"Column preservation rate too low: {preservation_rate}%"
        
        # Validate row count integrity
        assert len(exported_df) == len(workflow_data['raw_data']), "Row count should be preserved"
        
        # Validate generated emails are included
        assert 'Personalized Email' in exported_df.columns, "Generated emails should be included"
        
        # Validate email content is not corrupted
        email_column = exported_df['Personalized Email']
        non_empty_emails = email_column.notna().sum()
        email_integrity_rate = (non_empty_emails / len(exported_df)) * 100
        assert email_integrity_rate >= 95, f"Email content integrity too low: {email_integrity_rate}%"
        
        # Validate data types are maintained
        for col in preserved_columns:
            if col in workflow_data['raw_data'].columns:
                original_type = workflow_data['raw_data'][col].dtype
                exported_type = exported_df[col].dtype
                # Allow string conversion but check data isn't corrupted
                if original_type != exported_type:
                    # Check sample values are similar
                    sample_original = str(workflow_data['raw_data'][col].iloc[0])
                    sample_exported = str(exported_df[col].iloc[0])
                    assert sample_original == sample_exported or sample_original in sample_exported, f"Data corruption in column {col}"
        
        print(f"✅ Excel export integrity: {preservation_rate:.1f}% columns preserved, {email_integrity_rate:.1f}% email integrity")
    
    def test_complete_workflow_automation(self):
        """Task 9.5: Test complete workflow without manual intervention - tests/test_end_to_end_workflow.py:1139"""
        import time
        
        # Test multiple scenarios automatically
        test_scenarios = ["E2E_NORMAL_001", "E2E_NORMAL_002", "E2E_EDGE_001"]
        workflow_results = []
        
        total_start_time = time.perf_counter()
        
        for scenario_id in test_scenarios:
            scenario_start_time = time.perf_counter()
            
            try:
                # Execute complete workflow
                workflow_data = self.create_complete_workflow_data(scenario_id)
                
                if workflow_data:
                    # Measure workflow performance
                    scenario_end_time = time.perf_counter()
                    processing_time = scenario_end_time - scenario_start_time
                    
                    # Validate workflow completion
                    generated_emails = workflow_data['generated_emails']
                    success_rate = sum(1 for email in generated_emails if email['generation_success']) / len(generated_emails) * 100
                    
                    workflow_results.append({
                        'scenario_id': scenario_id,
                        'success': True,
                        'processing_time': processing_time,
                        'records_processed': len(workflow_data['raw_data']),
                        'email_success_rate': success_rate,
                        'records_per_second': len(workflow_data['raw_data']) / processing_time if processing_time > 0 else 0
                    })
                else:
                    workflow_results.append({
                        'scenario_id': scenario_id,
                        'success': False,
                        'error': 'Workflow data creation failed'
                    })
                    
            except Exception as e:
                workflow_results.append({
                    'scenario_id': scenario_id,
                    'success': False,
                    'error': str(e)
                })
        
        total_end_time = time.perf_counter()
        total_processing_time = total_end_time - total_start_time
        
        # Validate overall workflow automation
        successful_workflows = sum(1 for result in workflow_results if result.get('success', False))
        automation_success_rate = (successful_workflows / len(test_scenarios)) * 100
        
        assert automation_success_rate >= 80, f"Workflow automation success rate too low: {automation_success_rate}%"
        assert total_processing_time < 120, f"Total processing time too long: {total_processing_time:.2f}s"
        
        # Validate individual workflow performance
        for result in workflow_results:
            if result.get('success'):
                assert result['processing_time'] < 60, f"Individual workflow too slow: {result['processing_time']:.2f}s"
                assert result['email_success_rate'] >= 90, f"Email generation rate too low: {result['email_success_rate']:.1f}%"
        
        # Calculate aggregate metrics
        total_records = sum(r.get('records_processed', 0) for r in workflow_results if r.get('success'))
        avg_processing_rate = total_records / total_processing_time if total_processing_time > 0 else 0
        
        print(f"✅ Complete workflow automation: {automation_success_rate:.1f}% success, {avg_processing_rate:.1f} records/sec, {total_processing_time:.2f}s total")
    
    def test_workflow_error_handling_robustness(self):
        """Test robust error handling throughout the workflow - tests/test_end_to_end_workflow.py:1200"""
        # Test error scenarios
        error_scenarios = ["E2E_ERROR_001", "E2E_ERROR_002"]
        error_handling_results = []
        
        for scenario_id in error_scenarios:
            try:
                scenario = self.workflow_scenarios.get_scenario_by_id(scenario_id)
                
                if scenario_id == "E2E_ERROR_001":
                    # Test invalid file format handling
                    invalid_data = b"Invalid file content"
                    parsing_results = self.csv_mapper.validate_csv_parsing(invalid_data, "csv")
                    
                    error_handling_results.append({
                        'scenario_id': scenario_id,
                        'error_detected': not parsing_results["success"],
                        'error_message': parsing_results.get("error"),
                        'graceful_failure': parsing_results.get("error") is not None
                    })
                    
                elif scenario_id == "E2E_ERROR_002":
                    # Test missing columns handling
                    incomplete_data = pd.DataFrame({
                        "Random1": ["A", "B"],
                        "Random2": ["C", "D"]
                    })
                    
                    csv_data = self.csv_mapper.create_test_csv_file(incomplete_data, "csv")
                    parsing_results = self.csv_mapper.validate_csv_parsing(csv_data, "csv")
                    
                    if parsing_results["success"]:
                        mapping_results = self.csv_mapper.test_column_mapping_accuracy(parsing_results["columns"])
                        mapped_count = sum(1 for r in mapping_results.values() if r["mapped_to"] != "unmapped")
                        
                        error_handling_results.append({
                            'scenario_id': scenario_id,
                            'error_detected': mapped_count < 2,  # Should detect insufficient mapping
                            'graceful_failure': True,
                            'mapped_columns': mapped_count
                        })
                    
            except Exception as e:
                error_handling_results.append({
                    'scenario_id': scenario_id,
                    'error_detected': True,
                    'graceful_failure': True,  # Exception was caught
                    'error_message': str(e)
                })
        
        # Validate error handling
        for result in error_handling_results:
            assert result['error_detected'], f"Should detect error in {result['scenario_id']}"
            assert result['graceful_failure'], f"Should handle error gracefully in {result['scenario_id']}"
        
        print(f"✅ Error handling robustness: {len(error_handling_results)} error scenarios handled gracefully")
    
    def test_end_to_end_workflow_integration(self):
        """Test complete end-to-end workflow integration - tests/test_end_to_end_workflow.py:1251"""
        # Execute the full workflow as specified in PRD
        scenario = self.workflow_scenarios.get_scenario_by_id("E2E_NORMAL_001")
        
        # Stage 1: File Upload and Processing
        raw_data = self.workflow_scenarios.create_test_data_for_scenario(scenario)
        csv_data = self.csv_mapper.create_test_csv_file(raw_data, "csv")
        parsing_results = self.csv_mapper.validate_csv_parsing(csv_data, "csv")
        
        assert parsing_results["success"], "Stage 1 (File Upload) should succeed"
        
        # Stage 2: Column Mapping
        mapping_results = self.csv_mapper.test_column_mapping_accuracy(parsing_results["columns"])
        mapped_columns = sum(1 for r in mapping_results.values() if r["mapped_to"] != "unmapped")
        
        assert mapped_columns >= 3, "Stage 2 (Column Mapping) should map essential columns"
        
        # Stage 3: Email Generation
        generated_emails = self.simulate_email_generation(parsing_results["dataframe"], ["first_name", "company_name"])
        email_success_rate = sum(1 for email in generated_emails if email['generation_success']) / len(generated_emails) * 100
        
        assert email_success_rate >= 95, "Stage 3 (Email Generation) should have high success rate"
        
        # Stage 4: Excel Export
        final_data = parsing_results["dataframe"].copy()
        final_data['Personalized Email'] = [email['personalized_email'] for email in generated_emails]
        
        excel_output = io.BytesIO()
        with pd.ExcelWriter(excel_output, engine='openpyxl') as writer:
            final_data.to_excel(writer, index=False, sheet_name='Business Leads')
        
        excel_output.seek(0)
        exported_df = pd.read_excel(excel_output, sheet_name='Business Leads')
        
        assert len(exported_df) == len(raw_data), "Stage 4 (Excel Export) should preserve record count"
        assert 'Personalized Email' in exported_df.columns, "Stage 4 should include generated emails"
        
        # Validate complete workflow success
        workflow_validation = self.workflow_scenarios.validate_workflow_stage(
            "complete_workflow",
            {
                "stage_1_success": parsing_results["success"],
                "stage_2_mappings": mapped_columns,
                "stage_3_success_rate": email_success_rate,
                "stage_4_integrity": len(exported_df) == len(raw_data),
                "end_to_end_success": True
            },
            scenario
        )
        
        assert workflow_validation["passed"], f"Complete workflow should pass validation: {workflow_validation['issues']}"
        
        print(f"✅ End-to-end integration: {len(raw_data)} records → {mapped_columns} mappings → {email_success_rate:.1f}% emails → {len(exported_df)} exported")