@echo off
setlocal

REM Startet die Streamlit-App ohne virtuelle Umgebung.
REM Voraussetzung: streamlit ist systemweit installiert und im PATH.

cd /d "%~dp0"
streamlit run app.py

endlocal
