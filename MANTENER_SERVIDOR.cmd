@echo off
setlocal
cd /d "%~dp0"
for /d %%D in ("%LocalAppData%\Python\pythoncore-*" "%LocalAppData%\Programs\Python\Python*") do (
  if exist "%%~D\pythonw.exe" (
    start "" "%%~D\pythonw.exe" "%~dp0servidor_persistente.py"
    exit /b 0
  )
)
start "" /min pyw -3 "%~dp0servidor_persistente.py"
