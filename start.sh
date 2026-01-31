#!/bin/bash

echo "===================================="
echo "Iniciando CV_LINKEDIN_COMPARATOR"
echo "===================================="
echo ""

echo "[1/2] Iniciando Backend API..."
cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..
sleep 3

echo "[2/2] Iniciando Frontend (Streamlit)..."
cd frontend && streamlit run app.py &
FRONTEND_PID=$!
cd ..

echo ""
echo "===================================="
echo "Aplicacion iniciada!"
echo "===================================="
echo ""
echo "PIDs de los procesos:"
echo "  Backend API: $BACKEND_PID"
echo "  Frontend: $FRONTEND_PID"
echo ""
echo "URLs:"
echo "  Backend API: http://localhost:8000"
echo "  Frontend UI: http://localhost:8501"
echo ""
echo "Presiona Ctrl+C para detener todos los servicios"
echo ""

# Función para limpiar procesos al salir
cleanup() {
    echo ""
    echo "Deteniendo todos los servicios..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "Servicios detenidos."
    exit 0
}

# Capturar señal de interrupción
trap cleanup INT TERM

# Esperar a que todos los procesos terminen
wait
