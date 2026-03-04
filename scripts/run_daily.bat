@echo off
REM ============================================================
REM Tile Trends Intelligence - Daily Pipeline + Email
REM Schedule this in Windows Task Scheduler to run at 9:45 AM
REM (Pipeline runs first, then email sends at completion)
REM ============================================================

cd /d "%~dp0\.."

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run pipeline and send email
python scheduler.py --now

REM Deactivate
deactivate

echo.
echo ✅ Daily job completed!
pause