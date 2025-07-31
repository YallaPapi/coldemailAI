@echo off
echo Installing dependencies...
python -m pip install fastapi uvicorn pandas openai python-dotenv openpyxl python-multipart aiofiles

echo.
echo Starting Modern Cold Email Generator...
echo.
echo Open your browser to: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python modern_app.py
pause