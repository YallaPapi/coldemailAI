@echo off
echo Starting Simple Cold Email Generator...
echo.
echo Installing minimal dependencies...
python -m pip install flask pandas openai python-dotenv openpyxl

echo.
echo Open your browser to: http://localhost:5000
echo Upload the test_leads.csv file to generate emails
echo Press Ctrl+C to stop
echo.

python simple_working_app.py
pause