# Local PowerShell runner for Project 1: Policy RAG Assistant
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Starting Policy & Contract Q&A Assistant " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    .\venv\Scripts\pip install -r requirements.txt
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Copy-Item .env.example .env
}

# Check if sample PDFs are generated
$samplePdfDir = "sample_docs\pdf_files"
if (-not (Test-Path $samplePdfDir) -or (Get-ChildItem $samplePdfDir -Filter "*.pdf").Count -eq 0) {
    Write-Host "Generating sample policy and contract PDFs..." -ForegroundColor Yellow
    .\venv\Scripts\python sample_docs\generate_samples.py
}

Write-Host "Starting FastAPI server on http://127.0.0.1:8001 ..." -ForegroundColor Green
Write-Host "Web Chat UI: http://127.0.0.1:8001" -ForegroundColor Green
Write-Host "Swagger Docs: http://127.0.0.1:8001/docs" -ForegroundColor Green
Write-Host "Health check: http://127.0.0.1:8001/health" -ForegroundColor Green

.\venv\Scripts\uvicorn src.main:app --host 127.0.0.1 --port 8001 --reload
