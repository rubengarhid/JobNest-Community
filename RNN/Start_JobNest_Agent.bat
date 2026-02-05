@echo off
TITLE JobNest AI Agent Console
color 0A

echo ==================================================
echo      INICIANDO JOBNEST AI AGENT
echo      Core: RNN Classifier + FastAPI
echo ==================================================
echo.

:: 1. Verificar e Instalar Dependencias
echo [1/3] Verificando dependencias...
:: Check locations for requirements.txt
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    if exist "..\requirements.txt" (
        pip install -r ..\requirements.txt
    ) else (
        if exist "..\clasification_alg\requirements.txt" (
             pip install -r ..\clasification_alg\requirements.txt
        ) else (
             echo [AVISO] No se encontro requirements.txt. Asumiendo que las librerias estan instaladas.
        )
    )
)

echo.

:: 2. Verificar si existe el Modelo Entrenado
echo [2/3] Verificando modelo cerebral (jobnest_rnn_model.keras)...

if exist "jobnest_rnn_model.keras" (
    echo [INFO] Modelo encontrado. No es necesario re-entrenar.
) else (
    echo [INFO] Modelo NO encontrado. Iniciando entrenamiento (esto tomara unos segundos)...
    python rnn_classifier.py
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Fallo el entrenamiento. Revisa los errores arriba.
        pause
        exit /b
    )
    echo [OK] Entrenamiento completado.
)

echo.

:: 3. Iniciar el Servidor API
echo [3/3] Iniciando Servidor API en http://localhost:8000
echo.
echo Presiona CTRL+C para detener el servidor.
echo.

python agent_api.py

pause
