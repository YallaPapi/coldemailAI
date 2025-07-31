@echo off
echo Installing required packages...
python -m pip install flask pandas openai python-dotenv openpyxl

echo.
echo Starting Cold Email Generator...
echo Open your browser to http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python simple_working_app.py