import os
import logging
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify, Response, stream_template
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import pandas as pd
from io import BytesIO
from email_generator import EmailGenerator
import json
import time
import threading
from queue import Queue

def sanitize_to_ascii(text):
    """
    Aggressively converts text to ASCII. It replaces smart quotes and other
    common non-ASCII characters with their ASCII equivalents and ignores
    anything it can't convert.
    """
    if not isinstance(text, str):
        return text
    
    # Replace common "smart" punctuation with ASCII equivalents
    replacements = {
        ''': "'", ''': "'",
        '"': '"', '"': '"',
        '—': '--', '–': '-',
        '…': '...'
    }
    for smart, basic in replacements.items():
        text = text.replace(smart, basic)
        
    # Encode to ASCII, ignoring any characters that can't be converted
    return text.encode('ascii', 'ignore').decode('ascii')

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Validate OpenAI API key is set
if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY must be set in .env file")

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configuration
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize email generator
email_gen = EmailGenerator()

# Progress tracking
progress_queues = {}

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with file upload form"""
    return render_template('index.html')

@app.route('/debug')
def debug():
    """Simple debug upload page"""
    return render_template('debug_upload.html')

@app.route('/simple')
def simple_upload():
    """Simple upload page without complex JavaScript"""
    return render_template('simple.html')

@app.route('/test')
def test_upload():
    """Test upload page with minimal JavaScript"""
    return render_template('upload_test.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and show column mapping interface"""
    try:
        # Enhanced debug logging
        app.logger.info(f"Request files: {list(request.files.keys())}")
        app.logger.info(f"Request form: {dict(request.form)}")
        app.logger.info(f"Request method: {request.method}")
        app.logger.info(f"Content type: {request.content_type}")
        
        # Check if file was uploaded
        if 'file' not in request.files:
            app.logger.error("No 'file' key in request.files")
            app.logger.error(f"Available keys: {list(request.files.keys())}")
            flash('No file selected - file input not found in request', 'error')
            return redirect(url_for('index'))
        
        file = request.files['file']
        app.logger.info(f"File object: {file}")
        app.logger.info(f"File filename: '{file.filename}'")
        app.logger.info(f"File content type: {file.content_type}")
        
        # Check if file is valid
        if not file.filename or file.filename == '':
            app.logger.error(f"Empty filename. File object: {file}")
            flash('No file selected - filename is empty', 'error')
            return redirect(url_for('index'))
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload Excel (.xlsx, .xls) or CSV files only.', 'error')
            return redirect(url_for('index'))
        
        # Read the uploaded file
        filename = secure_filename(file.filename or 'upload')
        app.logger.info(f"Processing file: {filename}")
        
        # Read file content for both DataFrame and storage
        file_content = file.read()
        
        # Load spreadsheet into DataFrame
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(BytesIO(file_content))
            else:
                df = pd.read_excel(BytesIO(file_content))
        except Exception as e:
            app.logger.error(f"Error reading file: {str(e)}")
            flash(f'Error reading file: {str(e)}', 'error')
            return redirect(url_for('index'))
        
        # Store file data in session for the mapping step  
        import base64
        file_data = base64.b64encode(file_content).decode('utf-8')
        
        # Get column headers from the uploaded file
        columns = list(df.columns)
        
        app.logger.info(f"Found {len(columns)} columns: {columns}")
        
        # Store in session for next step
        from flask import session
        session['file_data'] = file_data
        session['filename'] = filename
        session['columns'] = columns
        
        # Show mapping interface
        return render_template('mapping.html', 
                             columns=columns, 
                             filename=filename,
                             row_count=len(df))
        
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        flash(f'An unexpected error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/generate_emails', methods=['POST'])
def generate_emails():
    """Generate emails based on user column mapping"""
    try:
        from flask import session
        
        # Debug logging
        app.logger.info(f"Generate emails request form: {dict(request.form)}")
        app.logger.info(f"Session keys: {list(session.keys())}")
        
        # Get stored file data
        if 'file_data' not in session:
            app.logger.error("No file_data in session")
            flash('Session expired. Please upload your file again.', 'error')
            return redirect(url_for('index'))
            
        # Decode file data
        import base64
        file_data = base64.b64decode(session['file_data'])
        filename = session['filename']
        
        # Recreate DataFrame
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(BytesIO(file_data))
            else:
                df = pd.read_excel(BytesIO(file_data))
            app.logger.info(f"Successfully recreated DataFrame with {len(df)} rows and columns: {list(df.columns)}")
        except Exception as e:
            app.logger.error(f"Error recreating file: {str(e)}")
            flash(f'Error recreating file: {str(e)}', 'error')
            return redirect(url_for('index'))
        
        # Enhanced debug logging for form data
        app.logger.info(f"Raw form data received: {dict(request.form)}")
        app.logger.info(f"Form keys: {list(request.form.keys())}")
        
        # Get mapping from form with detailed logging
        mapping = {}
        for field in ['first_name', 'company_name', 'job_title', 'industry', 'city', 'state', 'country', 'company_description']:
            form_key = f'map_{field}'
            column = request.form.get(form_key, '').strip()
            app.logger.info(f"Field '{field}': form_key='{form_key}', raw_value='{request.form.get(form_key)}', stripped='{column}'")
            
            if column and column != 'none' and column != '':
                mapping[field] = column
            else:
                app.logger.warning(f"Field '{field}' not mapped: column='{column}'")
        
        app.logger.info(f"Final user mapping: {mapping}")
        
        # Validate we have minimum required fields with enhanced error reporting
        required_fields = ['first_name', 'company_name']
        missing = []
        for field in required_fields:
            if field not in mapping:
                missing.append(field)
                app.logger.error(f"Required field '{field}' missing from mapping")
        
        if missing:
            error_msg = f'Please map required fields: {", ".join(missing)}. Form data received: {dict(request.form)}'
            app.logger.error(f"Form validation failed: {error_msg}")
            flash(f'Please map required fields: {", ".join(missing)}', 'error')
            return render_template('mapping.html', 
                                 columns=session['columns'], 
                                 filename=filename,
                                 row_count=len(df),
                                 current_mapping=dict(request.form))
        
        # Create mapped DataFrame with case-insensitive column matching
        mapped_df = pd.DataFrame()
        
        # Create case-insensitive column mapping
        column_map = {col.lower(): col for col in df.columns}
        
        for field, column in mapping.items():
            # Try exact match first, then case-insensitive
            if column in df.columns:
                mapped_df[field] = df[column]
            elif column.lower() in column_map:
                actual_column = column_map[column.lower()]
                mapped_df[field] = df[actual_column]
                app.logger.info(f"Mapped '{column}' to actual column '{actual_column}' (case-insensitive)")
            else:
                app.logger.warning(f"Column '{column}' not found in DataFrame (even case-insensitive)")
                # Add empty column to avoid errors
                mapped_df[field] = ''
        
        # Generate personalized emails with improved error handling
        app.logger.info(f"About to generate emails for {len(mapped_df)} leads using mapping: {mapping}")
        try:
            df_with_emails = email_gen.process_leads_with_mapping(mapped_df, mapping)

            # === START: ADD THIS SANITIZATION CODE ===
            app.logger.info("Sanitizing AI-generated emails to ASCII...")
            if 'Personalized' in df_with_emails.columns:
                df_with_emails['Personalized'] = df_with_emails['Personalized'].apply(sanitize_to_ascii)
                app.logger.info("Sanitization complete.")
            # === END: ADD THIS SANITIZATION CODE ===

            app.logger.info(f"Successfully generated emails, result has {len(df_with_emails)} rows")
            
            # Log success metrics
            if 'Personalized' in df_with_emails.columns:
                successful_emails = df_with_emails['Personalized'].notna().sum()
                app.logger.info(f"Generated {successful_emails} personalized emails out of {len(df_with_emails)} leads")
            
            # === START: ADD THIS LOGGING CODE ===
            app.logger.info("--- START OF FINAL DEBUG LOG ---")
            app.logger.info(f"DataFrame shape before Excel creation: {df_with_emails.shape}")
            app.logger.info(f"DataFrame columns: {list(df_with_emails.columns)}")
            app.logger.info("DataFrame dtypes:")
            app.logger.info(df_with_emails.dtypes)
            
            # Log the first 5 rows of the 'Personalized' column to inspect for problematic characters
            app.logger.info("--- Inspecting 'Personalized' column for problematic characters (first 5 rows) ---")
            for index, email_text in df_with_emails['Personalized'].head().items():
                try:
                    # Try to encode to ascii to see if it fails
                    email_text.encode('ascii')
                    app.logger.info(f"Row {index}: [ASCII-safe] {email_text[:100]}...")
                except UnicodeEncodeError:
                    app.logger.warning(f"Row {index}: [CONTAINS NON-ASCII] {email_text[:100]}...")
            
            app.logger.info("--- END OF FINAL DEBUG LOG ---")
            # === END: ADD THIS LOGGING CODE ===
            
        except Exception as e:
            app.logger.error(f"Error generating emails: {str(e)}")
            import traceback
            app.logger.error(f"Full traceback: {traceback.format_exc()}")
            flash(f'Error generating emails: {str(e)}', 'error')
            return redirect(url_for('index'))
        
        # Create output file in memory with proper Unicode handling
        output = BytesIO()
        
        # Ensure proper Unicode handling in Excel export
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_with_emails.to_excel(writer, index=False, sheet_name='Personalized Emails')
        
        output.seek(0)
        
        # Generate output filename with proper encoding
        base_name = filename.rsplit('.', 1)[0]
        output_filename = f"{base_name}_with_personalized_emails.xlsx"
        
        app.logger.info(f"Successfully generated {len(df_with_emails)} personalized emails")
        flash(f'Successfully generated {len(df_with_emails)} personalized emails!', 'success')
        
        # Store the Excel file temporarily for download
        import tempfile
        import uuid
        
        # Generate unique filename for temp storage
        temp_id = str(uuid.uuid4())
        temp_filepath = os.path.join(tempfile.gettempdir(), f"email_results_{temp_id}.xlsx")
        
        # Save Excel file
        with open(temp_filepath, 'wb') as f:
            f.write(output.getvalue())
        
        # Store temp file info in session for download
        session['download_file'] = temp_filepath
        session['download_filename'] = output_filename
        session['result_count'] = len(df_with_emails)
        
        # Clear upload session data
        session.pop('file_data', None)
        session.pop('filename', None)
        session.pop('columns', None)
        
        # Redirect to success page
        return redirect(url_for('download_results'))
        
    except Exception as e:
        app.logger.error(f"Unexpected error in generate_emails: {str(e)}")
        flash(f'An unexpected error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download_results')
def download_results():
    """Show success page with download link"""
    from flask import session
    
    if 'download_file' not in session:
        flash('No results available. Please generate emails first.', 'error')
        return redirect(url_for('index'))
    
    result_count = session.get('result_count', 0)
    download_filename = session.get('download_filename', 'results.xlsx')
    
    return render_template('results.html', 
                         result_count=result_count,
                         download_filename=download_filename)

@app.route('/download_file')
def download_file():
    """Download the generated Excel file"""
    from flask import session
    
    if 'download_file' not in session:
        flash('No file available for download.', 'error')
        return redirect(url_for('index'))
    
    temp_filepath = session['download_file']
    download_filename = session['download_filename']
    
    if not os.path.exists(temp_filepath):
        flash('Download file not found. Please regenerate emails.', 'error')
        return redirect(url_for('index'))
    
    def remove_file(response):
        try:
            os.remove(temp_filepath)
            session.pop('download_file', None)
            session.pop('download_filename', None)
            session.pop('result_count', None)
        except:
            pass
        return response
    
    response = send_file(
        temp_filepath,
        as_attachment=True,
        download_name=download_filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    response.call_on_close(remove_file)
    return response

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return {'status': 'healthy', 'service': 'cold-email-generator'}

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    flash('File too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
