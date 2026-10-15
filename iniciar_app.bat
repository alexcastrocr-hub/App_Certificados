@echo off
REM Iniciar App de Certificados - Academia Horizonte (doble clic)
REM Abre la pagina http://localhost:5000 en tu navegador.
cd /d "%~dp0"
uv sync
uv run python app.py
pause
