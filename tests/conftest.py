"""
Pytest configuration and shared fixtures for ColdEmailAI testing.

This module provides shared fixtures following Context7 patterns and TaskMaster research-driven setup.
Based on research: "pytest Flask application testing framework setup best practices 2025"
"""

import os
import sys
import io
import tempfile
import psutil
from typing import Generator, Dict, Any
import pandas as pd
import pytest
from flask import Flask
from flask.testing import FlaskClient

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app, email_gen


@pytest.fixture(scope='session')
def app() -> Flask:
    """
    Create application for testing.
    Research-driven: Use session scope for performance, separate test config.
    """
    # Configure app for testing
    flask_app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
    })
    
    return flask_app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """
    Create test client for making requests.
    Research-driven: Function scope for test isolation.
    """
    return app.test_client()


@pytest.fixture
def memory_monitor():
    """
    Memory monitoring fixture for performance tests.
    Research-driven: Use psutil for memory tracking during file processing.
    """
    class MemoryMonitor:
        def __init__(self):
            self.process = psutil.Process()
            self.baseline = None
            self.peak = None
            
        def start_monitoring(self):
            """Start memory monitoring baseline"""
            self.baseline = self.process.memory_info().rss
            return self.baseline
            
        def get_current_usage(self):
            """Get current memory usage"""
            current = self.process.memory_info().rss
            if self.peak is None or current > self.peak:
                self.peak = current
            return current
            
        def get_memory_increase(self):
            """Get memory increase from baseline"""
            if self.baseline is None:
                raise ValueError("Must call start_monitoring() first")
            current = self.get_current_usage()
            return current - self.baseline
            
        def assert_memory_increase_under(self, max_bytes: int):
            """Assert memory increase is under threshold"""
            increase = self.get_memory_increase()
            assert increase < max_bytes, f"Memory increased by {increase} bytes, max allowed: {max_bytes}"
            
        def get_stats(self) -> Dict[str, int]:
            """Get memory statistics"""
            return {
                'baseline': self.baseline,
                'current': self.get_current_usage(),
                'peak': self.peak,
                'increase': self.get_memory_increase() if self.baseline else 0
            }
    
    return MemoryMonitor()


@pytest.fixture
def temp_directory():
    """
    Create temporary directory for test files.
    Research-driven: Proper cleanup and isolation.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


# Test data generation fixtures
@pytest.fixture
def small_csv_content() -> bytes:
    """
    Generate small CSV content for basic testing.
    Real business data as per ZAD requirements.
    """
    csv_data = """first_name,last_name,company_name,title,industry,city,state,country
Sarah,Johnson,TechFlow Solutions,Marketing Director,Software,Austin,TX,United States
David,Chen,Green Valley Farms,Operations Manager,Agriculture,Sacramento,CA,United States
Jessica,Rodriguez,BrightStar Consulting,CEO,Business Services,Miami,FL,United States
Marcus,Williams,AutoParts Direct,VP Sales,Automotive,Detroit,MI,United States
Amanda,Taylor,Wellness Hub,Founder,Healthcare,Portland,OR,United States"""
    return csv_data.encode('utf-8')


@pytest.fixture
def large_csv_content() -> bytes:
    """
    Generate large CSV content for performance testing.
    Real business data scaled up as per ZAD requirements.
    """
    # Base realistic business data
    companies = [
        "TechFlow Solutions", "Green Valley Farms", "BrightStar Consulting", 
        "AutoParts Direct", "Wellness Hub", "DataSync Corp", "CloudNet Systems",
        "InnovateLab", "SecureGuard Inc", "FastTrack Logistics"
    ]
    first_names = [
        "Sarah", "David", "Jessica", "Marcus", "Amanda", "Robert", "Lisa",
        "Michael", "Jennifer", "William", "Susan", "James", "Patricia"
    ]
    last_names = [
        "Johnson", "Chen", "Rodriguez", "Williams", "Taylor", "Brown", "Davis",
        "Miller", "Wilson", "Moore", "Anderson", "Thomas", "Jackson"
    ]
    titles = [
        "CEO", "Marketing Director", "Operations Manager", "VP Sales", "Founder",
        "CTO", "Sales Manager", "Product Manager", "Director", "Vice President"
    ]
    industries = [
        "Software", "Agriculture", "Business Services", "Automotive", "Healthcare",
        "Manufacturing", "Retail", "Finance", "Education", "Technology"
    ]
    cities = [
        "Austin", "Sacramento", "Miami", "Detroit", "Portland", "Denver",
        "Atlanta", "Phoenix", "Seattle", "Boston", "Chicago", "Houston"
    ]
    states = ["TX", "CA", "FL", "MI", "OR", "CO", "GA", "AZ", "WA", "MA", "IL"]
    
    # Generate header
    csv_lines = ["first_name,last_name,company_name,title,industry,city,state,country"]
    
    # Generate 2000+ rows of realistic data
    import random
    for i in range(2100):
        company = f"{random.choice(companies)} #{i//10 + 1}"
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        title = random.choice(titles)
        industry = random.choice(industries)
        city = random.choice(cities)
        state = random.choice(states)
        
        csv_lines.append(f"{first_name},{last_name},{company},{title},{industry},{city},{state},United States")
    
    return '\n'.join(csv_lines).encode('utf-8')


@pytest.fixture
def messy_csv_content() -> bytes:
    """
    Generate messy CSV with real-world data quality issues.
    Research-driven: Test edge cases and data cleaning.
    """
    csv_data = """First Name, Last Name ,COMPANY_NAME,Job Title,industry,City,State,Country
Sarah  ,Johnson,TechFlow Solutions  ,Marketing Director,software,Austin,TX,United States
,Chen,Green Valley Farms,Operations Manager,Agriculture,Sacramento,CA,
Jessica,Rodriguez,"BrightStar, Consulting",CEO,Business Services,Miami,FL,United States
Marcus,Williams,AutoParts Direct,VP Sales,automotive,Detroit,MI,United States
Amanda,,Wellness Hub,Founder,Healthcare,"Portland, OR",OR,United States"""
    return csv_data.encode('utf-8')


@pytest.fixture
def malicious_files() -> Dict[str, bytes]:
    """
    Generate malicious files for security testing.
    Research-driven: Test security validation.
    """
    return {
        'fake_csv.exe': b'This is an executable file disguised as CSV',
        'script_injection.csv': b'name,email\n=cmd|"/c calc",test@example.com\n',
        'oversized.txt': b'x' * (20 * 1024 * 1024),  # 20MB file
        'empty_file.csv': b'',
        'invalid_csv.csv': b'This is not a valid CSV format at all',
    }


@pytest.fixture
def valid_excel_content() -> bytes:
    """
    Generate valid Excel content for testing.
    Research-driven: Test multiple file format support.
    """
    # Create Excel file in memory
    output = io.BytesIO()
    df = pd.DataFrame({
        'first_name': ['Sarah', 'David', 'Jessica'],
        'last_name': ['Johnson', 'Chen', 'Rodriguez'],
        'company_name': ['TechFlow Solutions', 'Green Valley Farms', 'BrightStar Consulting'],
        'title': ['Marketing Director', 'Operations Manager', 'CEO'],
        'industry': ['Software', 'Agriculture', 'Business Services']
    })
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    return output.getvalue()


# Performance thresholds based on research
MEMORY_THRESHOLDS = {
    'small_file_max_increase': 10 * 1024 * 1024,    # 10MB max increase for small files
    'large_file_max_increase': 50 * 1024 * 1024,    # 50MB max increase for large files
    'processing_timeout': 30,                        # 30 seconds max processing time
}


@pytest.fixture
def performance_thresholds() -> Dict[str, int]:
    """
    Performance thresholds for testing.
    Research-driven: Based on ZAD requirements.
    """
    return MEMORY_THRESHOLDS