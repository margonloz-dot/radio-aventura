@echo off
chcp 65001 >nul
setlocal
title Radio Aventura - Estacion local
cd /d "%~dp0"
set "RADIO_PYTHON="
for /d %%D in ("%LocalAppData%\Python\pythoncore-*" "%LocalAppData%\Programs\Python\Python*") do (
  if exist "%%~D\python.exe" set "RADIO_PYTHON=%%~D\python.exe"
)
if defined RADIO_PYTHON (
  "%RADIO_PYTHON%" "%~dp0app.py"
  if errorlevel 1 goto fallo
  exit /b 0
)
py -3 "%~dp0app.py"
if not errorlevel 1 exit /b 0
python "%~dp0app.py"
if not errorlevel 1 exit /b 0
:fallo
echo.
echo No se pudo iniciar la aplicacion. Revisa el mensaje anterior.
echo Necesitas Python 3.10 o posterior. No se requieren paquetes adicionales.
echo Tambien puedes abrir una terminal en esta carpeta y ejecutar: python app.py
pause
