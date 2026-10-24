@echo off
setlocal
cd /d "%~dp0"
for /d %%D in ("%LocalAppData%\Python\pythoncore-*" "%LocalAppData%\Programs\Python\Python*") do (
  if exist "%%~D\python.exe" (
    "%%~D\python.exe" "%~dp0servidor_persistente.py" --stop
    exit /b 0
  )
)
py -3 "%~dp0servidor_persistente.py" --stop
