@echo off
echo Starting MAH-CET Seat Matrix Analytics App...
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
    .\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8501 --server.headless false
) else (
    python -m streamlit run app.py --server.port 8501 --server.headless false
)
pause
