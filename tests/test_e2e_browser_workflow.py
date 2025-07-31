#!/usr/bin/env python3
"""
True End-to-End Browser Testing for ColdEmailAI
Following ZAD mandate: ZAD-task-mandate-e2e-browser-testing.md

This test automates a real Chrome browser to validate the complete user journey
using real data and interacting with the actual web interface.
"""

import time
import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
import tempfile
import csv

class TestE2EBrowserWorkflow:
    """Complete browser-based E2E testing class using context7 patterns"""
    
    @pytest.fixture(scope="class")
    def test_csv_file(self):
        """Create a real test CSV file for the E2E test - use context7"""
        # Create temporary CSV file with real business data
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['First Name', 'Company', 'Job Title', 'Industry', 'City', 'State', 'Country'])
            writer.writerow(['John', 'Acme Corp', 'Lead Developer', 'Software', 'San Francisco', 'CA', 'United States'])
            writer.writerow(['Sarah', 'TechStart Inc', 'VP Engineering', 'Technology', 'Austin', 'TX', 'United States'])
            temp_file_path = f.name
        
        yield temp_file_path
        
        # Cleanup
        try:
            os.unlink(temp_file_path)
        except FileNotFoundError:
            pass
    
    @pytest.fixture(scope="class")
    def browser_driver(self):
        """Setup Chrome browser driver with proper options - use context7"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        # Don't run headless so we can see what's happening
        # chrome_options.add_argument("--headless")
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(10)
            yield driver
        except WebDriverException as e:
            pytest.skip(f"Chrome WebDriver not available: {e}")
        finally:
            if 'driver' in locals():
                driver.quit()
    
    def test_full_user_workflow_in_browser(self, browser_driver, test_csv_file):
        """
        CRITICAL TEST: This test automates a real Chrome browser to validate 
        the complete user journey. It uses real data and interacts with the 
        actual web interface.
        
        Following ZAD mandate - this test MUST fail in current state due to
        Unicode encoding issue causing connection reset.
        """
        driver = browser_driver
        
        try:
            # Step 1: Navigate to the application's home page
            print("Step 1: Navigating to ColdEmailAI home page...")
            driver.get("http://127.0.0.1:5000/")
            
            # Verify page loaded correctly
            assert "ColdEmailAI" in driver.title or "Cold Email" in driver.title, f"Expected ColdEmailAI in title, got: {driver.title}"
            print(f"✓ Page loaded successfully: {driver.title}")
            
            # Step 2: Upload the real CSV file
            print("Step 2: Uploading test CSV file...")
            
            # Find file input - try multiple possible selectors
            file_input = None
            for selector in ['input[type="file"]', '#file', 'input[name="file"]']:
                try:
                    file_input = driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            assert file_input is not None, "Could not find file upload input element"
            
            # Upload the CSV file
            file_input.send_keys(os.path.abspath(test_csv_file))
            print(f"✓ File uploaded: {test_csv_file}")
            
            # Submit the upload form
            upload_button = None
            for selector in ['input[type="submit"]', 'button[type="submit"]', '#upload-button', '.upload-btn']:
                try:
                    upload_button = driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            assert upload_button is not None, "Could not find upload submit button"
            upload_button.click()
            print("✓ Upload form submitted")
            
            # Step 3: Wait for mapping page to load
            print("Step 3: Waiting for column mapping page...")
            wait = WebDriverWait(driver, 15)
            
            # Look for mapping interface elements
            mapping_found = False
            for selector in ['select[name*="map"]', '.mapping-select', '#mapping-form']:
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    mapping_found = True
                    break
                except TimeoutException:
                    continue
            
            assert mapping_found, "Column mapping page did not load within 15 seconds"
            print("✓ Column mapping page loaded")
            
            # Step 4: Map the necessary columns
            print("Step 4: Mapping columns...")
            
            # Map required fields - try to find dropdowns/selects
            field_mappings = {
                'first_name': 'First Name',
                'company_name': 'Company', 
                'job_title': 'Job Title',
                'industry': 'Industry'
            }
            
            mapped_count = 0
            for field, column_name in field_mappings.items():
                # Try multiple selector patterns for each field
                selectors_to_try = [
                    f'select[name="map_{field}"]',
                    f'#map_{field}',
                    f'select[name*="{field}"]'
                ]
                
                for selector in selectors_to_try:
                    try:
                        select_element = driver.find_element(By.CSS_SELECTOR, selector)
                        select = Select(select_element)
                        
                        # Try to select by visible text or value
                        try:
                            select.select_by_visible_text(column_name)
                        except:
                            # Try to find the option by partial text match
                            for option in select.options:
                                if column_name.lower() in option.text.lower():
                                    select.select_by_visible_text(option.text)
                                    break
                        
                        mapped_count += 1
                        print(f"✓ Mapped {field} to {column_name}")
                        break
                    except:
                        continue
            
            assert mapped_count >= 2, f"Could only map {mapped_count} fields, need at least 2 (first_name, company_name)"
            print(f"✓ Successfully mapped {mapped_count} columns")
            
            # Step 5: Trigger the email generation process
            print("Step 5: Triggering email generation...")
            
            # Find and click the generate emails button
            generate_button = None
            for selector in [
                'input[type="submit"]', 
                'button[type="submit"]', 
                '#generate-emails-button',
                '.generate-btn',
                'button:contains("Generate")',
                'input[value*="Generate"]'
            ]:
                try:
                    generate_button = driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            # Try XPath if CSS selectors don't work
            if generate_button is None:
                try:
                    generate_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Generate')] | //input[contains(@value, 'Generate')]")
                except:
                    pass
            
            assert generate_button is not None, "Could not find email generation button"
            generate_button.click()
            print("✓ Email generation triggered")
            
            # Step 6: CRITICAL - Wait for results or detect the connection reset error
            print("Step 6: Waiting for email generation results...")
            
            # This is where the test should fail due to Unicode encoding issue
            # The server will crash with "Connection was reset" and the browser 
            # will either hang, show an error page, or timeout
            
            wait_long = WebDriverWait(driver, 60)  # Give it a full minute
            
            try:
                # Look for success indicators
                success_indicators = [
                    (By.ID, "results-container"),
                    (By.CLASS_NAME, "results"),
                    (By.XPATH, "//a[contains(text(), 'Download')]"),
                    (By.XPATH, "//*[contains(text(), 'Success')]"),
                    (By.CSS_SELECTOR, "[href*='.xlsx']")
                ]
                
                result_found = False
                for by, selector in success_indicators:
                    try:
                        element = wait_long.until(EC.presence_of_element_located((by, selector)))
                        result_found = True
                        print(f"✓ SUCCESS: Found result element: {selector}")
                        break
                    except TimeoutException:
                        continue
                
                if result_found:
                    # If we get here, the Unicode fix worked!
                    print("✓ SUCCESS: Email generation completed successfully!")
                    
                    # Additional validations
                    assert "Download" in driver.page_source, "Download link not found on results page"
                    print("✓ Download link found on results page")
                    
                    return True
                else:
                    # No success elements found - check for error indicators
                    error_indicators = [
                        "error", "Error", "ERROR",
                        "failed", "Failed", "FAILED", 
                        "timeout", "Timeout", "TIMEOUT",
                        "500", "502", "503", "504",
                        "Connection", "connection"
                    ]
                    
                    page_source = driver.page_source.lower()
                    found_errors = [error for error in error_indicators if error.lower() in page_source]
                    
                    if found_errors:
                        pytest.fail(f"Email generation failed with errors: {found_errors}")
                    else:
                        pytest.fail("Email generation timed out - no success or error indicators found")
                        
            except TimeoutException:
                # This is the expected failure due to Unicode encoding issue
                current_url = driver.current_url
                page_title = driver.title
                page_source_snippet = driver.page_source[:1000] if driver.page_source else "No page source"
                
                error_msg = f"""
EXPECTED FAILURE: Email generation timed out (Connection Reset Issue)
- Current URL: {current_url}
- Page Title: {page_title}
- Page Source Snippet: {page_source_snippet}

This failure confirms the Unicode encoding bug in Flask /generate_emails endpoint.
The server crashes when trying to return Unicode characters in HTTP responses.
"""
                pytest.fail(error_msg)
            
        except Exception as e:
            # Capture debug information
            try:
                current_url = driver.current_url
                page_title = driver.title
                screenshot_path = f"test_failure_screenshot_{int(time.time())}.png"
                driver.save_screenshot(screenshot_path)
                
                error_msg = f"""
E2E Test Failed: {str(e)}
- Current URL: {current_url}
- Page Title: {page_title}
- Screenshot saved: {screenshot_path}
"""
                pytest.fail(error_msg)
            except:
                pytest.fail(f"E2E Test Failed: {str(e)}")

    def test_browser_can_start(self, browser_driver):
        """Smoke test to ensure browser automation is working"""
        driver = browser_driver
        driver.get("http://127.0.0.1:5000/")
        assert driver.title is not None
        print(f"✓ Browser smoke test passed: {driver.title}")

if __name__ == "__main__":
    # Run the test directly
    pytest.main([__file__, "-v", "-s"])