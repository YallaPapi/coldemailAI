"""
Modern Cold Email Generator using FastAPI
Solves all the architectural issues from the Flask version
"""
import os
import asyncio
from typing import List, Dict, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
from io import BytesIO
import openai
from dotenv import load_dotenv
import uuid
from datetime import datetime
import logging

# Load environment
load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Cold Email Generator", version="2.0")

# In-memory storage for simplicity (use Redis in production)
processing_jobs = {}

class EmailGenerator:
    """Async email generator using OpenAI"""
    
    async def generate_email(self, contact: Dict[str, str]) -> str:
        """Generate a single email asynchronously"""
        first_name = str(contact.get('first_name', '')).strip()
        company = str(contact.get('company_name', contact.get('company', ''))).strip()
        title = str(contact.get('title', contact.get('job_title', ''))).strip()
        
        if not (first_name or company):
            return "Insufficient data for email generation"
        
        prompt = f"Write a brief, professional cold email to {first_name} at {company}"
        if title:
            prompt += f" who is a {title}"
        prompt += ". Keep it under 150 words, friendly and focused on offering value."
        
        try:
            # Use async OpenAI call
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return f"Error generating email: {str(e)}"

async def process_csv_background(job_id: str, file_content: bytes, filename: str):
    """Process CSV file in background"""
    try:
        processing_jobs[job_id] = {
            "status": "processing",
            "progress": 0,
            "total": 0,
            "results": None,
            "error": None,
            "started_at": datetime.now()
        }
        
        # Read CSV
        df = pd.read_csv(BytesIO(file_content))
        total_rows = len(df)
        processing_jobs[job_id]["total"] = total_rows
        
        # Generate emails
        email_gen = EmailGenerator()
        results = []
        
        for idx, (_, row) in enumerate(df.iterrows()):
            email = await email_gen.generate_email(row.to_dict())
            results.append({
                'First Name': row.get('first_name', ''),
                'Company': row.get('company_name', row.get('company', '')),
                'Title': row.get('title', row.get('job_title', '')),
                'Email': email
            })
            
            # Update progress
            processing_jobs[job_id]["progress"] = idx + 1
            processing_jobs[job_id]["status"] = "processing"
            
            # Small delay to prevent rate limiting
            if idx % 5 == 0:
                await asyncio.sleep(1)
        
        # Create Excel output
        output_df = pd.DataFrame(results)
        output = BytesIO()
        output_df.to_excel(output, index=False)
        output.seek(0)
        
        processing_jobs[job_id]["status"] = "completed"
        processing_jobs[job_id]["results"] = output.getvalue()
        
    except Exception as e:
        logger.error(f"Processing error: {e}")
        processing_jobs[job_id]["status"] = "failed"
        processing_jobs[job_id]["error"] = str(e)

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the upload page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cold Email Generator 2.0</title>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px; 
                margin: 50px auto; 
                padding: 20px;
                background: #f5f5f5;
            }
            .container { 
                background: white; 
                padding: 40px; 
                border-radius: 12px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { 
                color: #333; 
                margin-bottom: 10px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
            }
            .upload-area {
                border: 2px dashed #ddd;
                border-radius: 8px;
                padding: 40px;
                text-align: center;
                margin: 20px 0;
                transition: all 0.3s;
            }
            .upload-area:hover {
                border-color: #007bff;
                background: #f8f9fa;
            }
            input[type="file"] { 
                display: none;
            }
            .upload-button {
                display: inline-block;
                background: #007bff; 
                color: white; 
                padding: 12px 30px; 
                border-radius: 6px; 
                cursor: pointer;
                transition: background 0.3s;
            }
            .upload-button:hover { 
                background: #0056b3; 
            }
            .file-info {
                margin-top: 20px;
                color: #666;
            }
            .submit-button {
                background: #28a745;
                color: white;
                padding: 12px 40px;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                cursor: pointer;
                margin-top: 20px;
                transition: background 0.3s;
            }
            .submit-button:hover {
                background: #218838;
            }
            .submit-button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            .progress {
                display: none;
                margin-top: 30px;
            }
            .progress-bar {
                width: 100%;
                height: 20px;
                background: #e9ecef;
                border-radius: 10px;
                overflow: hidden;
            }
            .progress-fill {
                height: 100%;
                background: #007bff;
                width: 0%;
                transition: width 0.3s;
            }
            .status {
                margin-top: 10px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Cold Email Generator 2.0</h1>
            <p class="subtitle">Upload a CSV file to generate personalized cold emails powered by AI</p>
            
            <form id="uploadForm">
                <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                    <label class="upload-button">Choose CSV File</label>
                    <input type="file" id="fileInput" accept=".csv" onchange="fileSelected(this)">
                    <div class="file-info" id="fileInfo">No file selected</div>
                </div>
                
                <button type="submit" class="submit-button" id="submitButton" disabled>Generate Emails</button>
            </form>
            
            <div class="progress" id="progress">
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                <div class="status" id="status">Processing...</div>
            </div>
        </div>
        
        <script>
            let selectedFile = null;
            
            function fileSelected(input) {
                selectedFile = input.files[0];
                if (selectedFile) {
                    document.getElementById('fileInfo').textContent = `Selected: ${selectedFile.name} (${(selectedFile.size / 1024).toFixed(1)} KB)`;
                    document.getElementById('submitButton').disabled = false;
                }
            }
            
            document.getElementById('uploadForm').onsubmit = async (e) => {
                e.preventDefault();
                
                if (!selectedFile) return;
                
                const formData = new FormData();
                formData.append('file', selectedFile);
                
                document.getElementById('progress').style.display = 'block';
                document.getElementById('submitButton').disabled = true;
                
                try {
                    // Upload file
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (result.job_id) {
                        // Poll for progress
                        pollProgress(result.job_id);
                    } else {
                        alert('Error: ' + (result.detail || 'Unknown error'));
                    }
                } catch (error) {
                    alert('Upload failed: ' + error.message);
                    document.getElementById('submitButton').disabled = false;
                }
            };
            
            async function pollProgress(jobId) {
                const interval = setInterval(async () => {
                    try {
                        const response = await fetch(`/status/${jobId}`);
                        const status = await response.json();
                        
                        if (status.progress && status.total) {
                            const percent = (status.progress / status.total * 100).toFixed(0);
                            document.getElementById('progressFill').style.width = percent + '%';
                            document.getElementById('status').textContent = `Processing ${status.progress} of ${status.total} contacts...`;
                        }
                        
                        if (status.status === 'completed') {
                            clearInterval(interval);
                            document.getElementById('status').textContent = 'Complete! Downloading...';
                            window.location.href = `/download/${jobId}`;
                        } else if (status.status === 'failed') {
                            clearInterval(interval);
                            document.getElementById('status').textContent = 'Failed: ' + status.error;
                            document.getElementById('submitButton').disabled = false;
                        }
                    } catch (error) {
                        clearInterval(interval);
                        document.getElementById('status').textContent = 'Error checking status';
                        document.getElementById('submitButton').disabled = false;
                    }
                }, 1000);
            }
        </script>
    </body>
    </html>
    """

@app.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Handle file upload and start background processing"""
    # Validate file
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "Only CSV files are supported")
    
    # Read file content
    content = await file.read()
    
    # Create job ID
    job_id = str(uuid.uuid4())
    
    # Start background processing
    background_tasks.add_task(process_csv_background, job_id, content, file.filename)
    
    return {"job_id": job_id, "message": "Processing started"}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    """Get processing status"""
    if job_id not in processing_jobs:
        raise HTTPException(404, "Job not found")
    
    job = processing_jobs[job_id]
    return {
        "status": job["status"],
        "progress": job["progress"],
        "total": job["total"],
        "error": job["error"]
    }

@app.get("/download/{job_id}")
async def download_results(job_id: str):
    """Download generated emails"""
    if job_id not in processing_jobs:
        raise HTTPException(404, "Job not found")
    
    job = processing_jobs[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(400, f"Job status: {job['status']}")
    
    return StreamingResponse(
        BytesIO(job["results"]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=cold_emails_{job_id[:8]}.xlsx"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)