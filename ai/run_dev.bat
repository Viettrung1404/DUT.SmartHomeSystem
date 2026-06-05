@echo off
REM Development server startup script for Windows

echo Starting Vietnamese NLP Intent Classification Server (Development Mode)...

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Run the server with hot reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
