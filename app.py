import os
import logging
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import pandas as pd
from io import BytesIO
from email_generator import EmailGenerator

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
    return send_file('debug_upload.html')

@app.route('/simple')
def simple_upload():
    """Simple upload page without complex JavaScript"""
    return render_template('simple.html')

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
        
        # Get mapping from form
        mapping = {}
        for field in ['first_name', 'company_name', 'job_title', 'industry', 'city', 'state', 'country', 'company_description']:
            column = request.form.get(f'map_{field}', '').strip()
            if column and column != 'none':
                mapping[field] = column
        
        app.logger.info(f"User mapping: {mapping}")
        
        # Validate we have minimum required fields
        required_fields = ['first_name', 'company_name']
        missing = [field for field in required_fields if field not in mapping]
        if missing:
            flash(f'Please map required fields: {", ".join(missing)}', 'error')
            return render_template('mapping.html', 
                                 columns=session['columns'], 
                                 filename=filename,
                                 row_count=len(df),
                                 current_mapping=dict(request.form))
        
        # Create mapped DataFrame
        mapped_df = pd.DataFrame()
        for field, column in mapping.items():
            if column in df.columns:
                mapped_df[field] = df[column]
            else:
                app.logger.warning(f"Column '{column}' not found in DataFrame")
        
        # Generate personalized emails
        app.logger.info(f"About to generate emails for {len(mapped_df)} leads using mapping: {mapping}")
        try:
            df_with_emails = email_gen.process_leads_with_mapping(mapped_df, mapping)
            app.logger.info(f"Successfully generated emails, result has {len(df_with_emails)} rows")
            
            # Log success metrics
            if 'Personalized' in df_with_emails.columns:
                successful_emails = df_with_emails['Personalized'].notna().sum()
                app.logger.info(f"Generated {successful_emails} personalized emails out of {len(df_with_emails)} leads")
            
        except Exception as e:
            app.logger.error(f"Error generating emails: {str(e)}")
            import traceback
            app.logger.error(f"Full traceback: {traceback.format_exc()}")
            flash(f'Error generating emails: {str(e)}', 'error')
            return redirect(url_for('index'))
        
        # Create output file in memory
        output = BytesIO()
        df_with_emails.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        
        # Generate output filename
        base_name = filename.rsplit('.', 1)[0]
        output_filename = f"{base_name}_with_personalized_emails.xlsx"
        
        app.logger.info(f"Successfully generated {len(df_with_emails)} personalized emails")
        flash(f'Successfully generated {len(df_with_emails)} personalized emails!', 'success')
        
        # Clear session data
        session.pop('file_data', None)
        session.pop('filename', None)
        session.pop('columns', None)
        
        return send_file(
            output,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        app.logger.error(f"Unexpected error in generate_emails: {str(e)}")
        flash(f'An unexpected error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))

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
