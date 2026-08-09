@echo off
cd /d "%~dp0"

echo Starte Ollama...
start "" "C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama app.exe"
timeout /t 4 /nobreak >nul

call venv\Scripts\activate.bat
streamlit run app.py