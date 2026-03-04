@echo off
REM ============================================================
REM Tile Trends Intelligence - Send Email Only
REM Use this to resend today's newsletter without re-scraping
REM ============================================================

cd /d "%~dp0\.."

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Send email only
python scheduler.py --email-only

REM Deactivate
deactivate

echo.
pause