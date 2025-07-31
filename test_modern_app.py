#!/usr/bin/env python3
"""
Test the modern FastAPI cold email generator
"""
import asyncio
import aiohttp
import pandas as pd
from io import BytesIO
import time

async def test_app():
    """Test the FastAPI application"""
    base_url = "http://localhost:5000"
    
    # Create test CSV data
    test_data = pd.DataFrame({
        'first_name': ['John', 'Sarah', 'Mike'],
        'company_name': ['Acme Corp', 'TechStart', 'Global Inc'],
        'title': ['CEO', 'CTO', 'VP Sales']
    })
    
    csv_buffer = BytesIO()
    test_data.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    async with aiohttp.ClientSession() as session:
        # 1. Test home page
        print("1. Testing home page...")
        async with session.get(base_url) as resp:
            assert resp.status == 200
            print("✓ Home page accessible")
        
        # 2. Upload file
        print("\n2. Uploading CSV file...")
        data = aiohttp.FormData()
        data.add_field('file', csv_buffer.getvalue(), 
                      filename='test.csv',
                      content_type='text/csv')
        
        async with session.post(f"{base_url}/upload", data=data) as resp:
            assert resp.status == 200
            result = await resp.json()
            job_id = result['job_id']
            print(f"✓ File uploaded, job ID: {job_id}")
        
        # 3. Check progress
        print("\n3. Checking progress...")
        completed = False
        for i in range(30):  # Wait up to 30 seconds
            async with session.get(f"{base_url}/status/{job_id}") as resp:
                status = await resp.json()
                print(f"   Status: {status['status']} - {status['progress']}/{status['total']}")
                
                if status['status'] == 'completed':
                    completed = True
                    break
                elif status['status'] == 'failed':
                    print(f"✗ Job failed: {status['error']}")
                    return
                
            await asyncio.sleep(1)
        
        if not completed:
            print("✗ Job timed out")
            return
        
        print("✓ Email generation completed!")
        
        # 4. Download results
        print("\n4. Downloading results...")
        async with session.get(f"{base_url}/download/{job_id}") as resp:
            assert resp.status == 200
            content = await resp.read()
            
            # Save to file
            with open('test_results.xlsx', 'wb') as f:
                f.write(content)
            
            print(f"✓ Results saved to test_results.xlsx ({len(content)} bytes)")
        
        print("\n✅ All tests passed! The app is working correctly.")

if __name__ == "__main__":
    print("Testing Modern Cold Email Generator")
    print("===================================")
    print("Make sure the app is running: python modern_app.py")
    print()
    
    try:
        asyncio.run(test_app())
    except aiohttp.ClientConnectorError:
        print("❌ Could not connect to the app. Is it running on http://localhost:5000?")
    except Exception as e:
        print(f"❌ Test failed: {e}")