@echo off
REM ============================================================
REM Tile Trends Intelligence - Setup Windows Task Scheduler
REM This creates a scheduled task to run daily at 9:45 AM
REM Run this script AS ADMINISTRATOR
REM ============================================================

echo ============================================================
echo  Tile Trends Intelligence - Task Scheduler Setup
echo ============================================================
echo.

set SCRIPT_DIR=%~dp0
set APP_DIR=%SCRIPT_DIR%..
set BAT_PATH=%SCRIPT_DIR%run_daily.bat

echo Creating scheduled task: TileTrendsDaily
echo Script: %BAT_PATH%
echo Schedule: Daily at 9:45 AM
echo.

schtasks /create /tn "TileTrendsDaily" /tr "\"%BAT_PATH%\"" /sc daily /st 09:45 /f

if %errorlevel% equ 0 (
    echo.
    echo ✅ Task created successfully!
    echo.
    echo The pipeline will run every day at 9:45 AM.
    echo Email will be sent to kolhe.abhinandan@hrjohnsonindia.com
    echo after the pipeline completes (around 10:00 AM).
    echo.
    echo To verify: Open Task Scheduler and look for "TileTrendsDaily"
    echo To remove: schtasks /delete /tn "TileTrendsDaily" /f
) else (
    echo.
    echo ❌ Failed to create task. Please run this script as Administrator.
)

echo.
pause