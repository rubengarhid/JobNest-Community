@echo off
echo ====================================
echo Iniciando CV_LINKEDIN_COMPARATOR
echo ====================================
echo.

echo [1/2] Iniciando Backend API...
start "Backend API" cmd /k "cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul

echo [2/2] Iniciando Frontend (Streamlit)...
start "Frontend - Streamlit" cmd /k "cd frontend && streamlit run app.py"

echo.
echo ====================================
echo Aplicacion iniciada!
echo ====================================
echo.
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:8501
echo.
echo Presiona cualquier tecla para cerrar esta ventana...
pause >nul
