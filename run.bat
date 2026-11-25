@echo off
rem ==========================================================
rem  CargoOpt - one-click start for Windows
rem  Double-click this file. The first run installs everything
rem  (needs internet), later runs start in a few seconds.
rem ==========================================================
setlocal
title CargoOpt
cd /d "%~dp0"
echo.
echo  CargoOpt - Truck Load Optimizer
echo  ===============================
echo.

rem ---------- 1. find Python ----------
set "PY="
python --version >nul 2>&1
if not errorlevel 1 set "PY=python"
if defined PY goto have_python
py -3 --version >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if defined PY goto have_python

echo  Python is not installed on this computer.
where winget >nul 2>&1
if errorlevel 1 goto no_winget
echo  Installing Python 3.12 with winget. Please answer the questions it asks...
winget install -e --id Python.Python.3.12
echo.
echo  When the installation has finished, close this window and double-click run.bat again.
pause
exit /b 0

:no_winget
echo  Please install Python 3 from https://www.python.org/downloads/
echo  During setup tick "Add python.exe to PATH", then double-click run.bat again.
start "" https://www.python.org/downloads/
pause
exit /b 1

:have_python
for /f "delims=" %%v in ('%PY% --version 2^>^&1') do echo  Found %%v

rem ---------- 2. private environment (.venv) ----------
if exist ".venv\Scripts\python.exe" goto have_venv
echo  [1/3] Creating a private Python environment in .venv ...
%PY% -m venv .venv
if errorlevel 1 goto fail
:have_venv

rem ---------- 3. install packages (only when requirements.txt changed) ----------
fc /b requirements.txt ".venv\requirements.installed" >nul 2>&1
if not errorlevel 1 goto installed
echo  [2/3] Installing packages - first time only, this can take a few minutes ...
".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto fail
copy /y requirements.txt ".venv\requirements.installed" >nul
:installed

rem ---------- 4. start the app and open the browser ----------
echo  [3/3] Starting CargoOpt at http://localhost:8501
echo        Keep this window open while you use the app. Close it to stop the app.
echo.
start "" /min powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep 5; Start-Process 'http://localhost:8501'"
".venv\Scripts\python.exe" -m streamlit run app.py --server.port 8501 --browser.gatherUsageStats false
pause
exit /b 0

:fail
echo.
echo  Something went wrong. Check the internet connection and run this file again.
pause
exit /b 1
