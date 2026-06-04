@echo off
echo ===================================================
echo Setting up Intelligent Resume Ranking System...
echo ===================================================

echo.
echo [1/4] Creating Python virtual environment (.venv)...
python -m venv .venv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment. Ensure Python is installed and in your PATH.
    pause
    exit /b %errorlevel%
)

echo.
echo [2/4] Upgrading pip...
call .venv\Scripts\python.exe -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo Warning: Failed to upgrade pip. Continuing...
)

echo.
echo [3/4] Installing dependencies from requirements.txt...
call .venv\Scripts\pip.exe install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies.
    pause
    exit /b %errorlevel%
)

echo.
echo [4/4] Creating folder structures for sample data...
mkdir sample_data >nul 2>&1
mkdir sample_data\resumes >nul 2>&1
mkdir sample_data\job_descriptions >nul 2>&1

echo.
echo ===================================================
echo Setup complete successfully!
echo To run the application, activate the virtual environment and run:
echo streamlit run app.py
echo ===================================================
echo.
pause
