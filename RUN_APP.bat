@echo off
echo ============================================
echo    Matali Smart Pricing System V2.0
echo    نظام التسعير الذكي - متالي
echo ============================================
echo.
echo Starting the application...
echo جاري تشغيل التطبيق...
echo.

cd /d "%~dp0"

REM Try to run with python command
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Using python command...
    python -m streamlit run app_v2.py
    goto :eof
)

REM Try Windows Store Python
if exist "C:\Users\ahmed\AppData\Local\Microsoft\WindowsApps\python.exe" (
    echo Using Windows Store Python...
    "C:\Users\ahmed\AppData\Local\Microsoft\WindowsApps\python.exe" -m streamlit run app_v2.py
    goto :eof
)

REM If nothing works
echo.
echo ERROR: Python not found!
echo خطأ: لم يتم العثور على Python!
echo.
echo Please install Python from:
echo https://www.python.org/downloads/
echo.
pause
