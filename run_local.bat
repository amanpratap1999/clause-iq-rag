@echo off
echo ==========================================
echo  Starting Policy ^& Contract Q^&A Assistant
echo ==========================================

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    call .\venv\Scripts\pip install -r requirements.txt
)

if not exist .env (
    copy .env.example .env
)

if not exist sample_docs\pdf_files (
    echo Generating sample policy PDFs...
    call .\venv\Scripts\python sample_docs\generate_samples.py
)

echo Starting FastAPI server at http://127.0.0.1:8001
echo Web UI: http://127.0.0.1:8001
echo Swagger Docs: http://127.0.0.1:8001/docs
echo Health Check: http://127.0.0.1:8001/health

call .\venv\Scripts\uvicorn src.main:app --host 127.0.0.1 --port 8001 --reload
pause
