#!/usr/bin/env python3
"""
Test the full ColdEmailAI workflow with mock email generation
Simulates the complete process: CSV upload -> mapping -> chunked processing -> email generation
"""
import pandas as pd
import tempfile
import os
from mock_email_generator import MockEmailGenerator

def test_full_workflow():
    """Test the complete workflow from CSV to email generation"""
    print("Testing full workflow with mock email generation...")
    
    # Use production test data
    test_file = "production_test.csv"
    
    if not os.path.exists(test_file):
        print(f"ERROR: Test file {test_file} not found")
        return False
    
    try:
        # Initialize mock email generator
        email_gen = MockEmailGenerator()
        
        # Step 1: Simulate chunked CSV processing (as in the main app)
        CHUNK_SIZE = 2  # Small chunks for testing
        all_results = []
        chunk_count = 0
        
        print(f"Processing {test_file} in chunks of {CHUNK_SIZE}...")
        
        # Column mapping (same as in main application)
        mapping = {
            'First Name': 'first_name',
            'Last Name': 'last_name',
            'Company Name': 'company_name', 
            'Title': 'title',
            'Industry': 'industry'
        }
        
        for chunk in pd.read_csv(test_file, chunksize=CHUNK_SIZE):
            chunk_count += 1
            print(f"  Processing chunk {chunk_count} ({len(chunk)} rows)")
            
            # Step 2: Apply column mapping
            mapped_chunk = pd.DataFrame()
            for field, column in mapping.items():
                if column in chunk.columns:
                    mapped_chunk[field] = chunk[column]
            
            # Step 3: Generate emails for the chunk
            chunk_with_emails = email_gen.process_leads_with_mapping(mapped_chunk, mapping)
            all_results.append(chunk_with_emails)
            
            print(f"    Generated {len(chunk_with_emails)} emails")
        
        # Step 4: Combine all results
        final_result = pd.concat(all_results, ignore_index=True)
        
        print(f"\nWorkflow completed successfully!")
        print(f"Total chunks processed: {chunk_count}")
        print(f"Total emails generated: {len(final_result)}")
        print(f"Success rate: {len(final_result[final_result['generation_status'] == 'success'])}/{len(final_result)}")
        
        # Step 5: Show sample results
        print("\nSample generated emails:")
        print("-" * 60)
        
        for i, row in final_result.head(2).iterrows():
            print(f"Lead {i+1}: {row.get('First Name', 'N/A')} at {row.get('Company Name', 'N/A')}")
            print(f"Email:\n{row['generated_email']}")
            print("-" * 60)
        
        # Step 6: Save results (simulating export functionality)
        output_file = "test_workflow_output.xlsx"
        final_result.to_excel(output_file, index=False)
        print(f"\nResults saved to {output_file}")
        
        return True
        
    except Exception as e:
        print(f"ERROR in full workflow test: {str(e)}")
        return False

def test_large_file_workflow():
    """Test workflow with larger file to validate chunked processing"""
    print("\nTesting workflow with large file...")
    
    large_file = "large_test.csv"
    
    if not os.path.exists(large_file):
        print("Creating large test file...")
        os.system("python create_large_test.py")
    
    try:
        email_gen = MockEmailGenerator()
        
        # Process large file in realistic chunks
        CHUNK_SIZE = 1000  # Same as main application
        all_results = []
        chunk_count = 0
        total_processed = 0
        
        print(f"Processing {large_file} with chunk size {CHUNK_SIZE}...")
        
        mapping = {
            'First Name': 'first_name',
            'Last Name': 'last_name', 
            'Company Name': 'company_name',
            'Title': 'title',
            'Industry': 'industry'
        }
        
        for chunk in pd.read_csv(large_file, chunksize=CHUNK_SIZE):
            chunk_count += 1
            total_processed += len(chunk)
            
            # Apply mapping
            mapped_chunk = pd.DataFrame()
            for field, column in mapping.items():
                if column in chunk.columns:
                    mapped_chunk[field] = chunk[column]
            
            # Generate emails (in real app, this would be the expensive OpenAI call)
            chunk_with_emails = email_gen.process_leads_with_mapping(mapped_chunk, mapping)
            all_results.append(chunk_with_emails)
            
            if chunk_count <= 3:
                print(f"  Chunk {chunk_count}: {len(chunk)} rows -> {len(chunk_with_emails)} emails")
            elif chunk_count == 4:
                print("  ... (processing additional chunks)")
        
        # Combine results
        final_result = pd.concat(all_results, ignore_index=True)
        
        print(f"\nLarge file workflow completed!")
        print(f"Chunks processed: {chunk_count}")
        print(f"Total leads processed: {total_processed}")
        print(f"Total emails generated: {len(final_result)}")
        
        # Save large results
        output_file = "test_large_workflow_output.xlsx"
        final_result.to_excel(output_file, index=False)
        print(f"Results saved to {output_file}")
        
        return True
        
    except Exception as e:
        print(f"ERROR in large file workflow test: {str(e)}")
        return False

def main():
    """Run full workflow tests"""
    print("Full Workflow Tests")
    print("=" * 50)
    
    tests = [
        ("Full Workflow (Small File)", test_full_workflow),
        ("Full Workflow (Large File)", test_large_file_workflow)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test {test_name} failed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("WORKFLOW TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: Full workflow tests passed!")
        print("The application can process CSV files, map columns, and generate emails.")
        return True
    else:
        print("FAILURE: Some workflow tests failed.")
        return False

if __name__ == "__main__":
    success = main()