@echo off
rem เปิดเซิร์ฟเวอร์แชร์เว็บ liverV1 (Windows) — ดับเบิลคลิกไฟล์นี้
rem หา python อัตโนมัติ: py launcher -> python -> python3
cd /d "%~dp0"
set PORT=8080
if not "%~1"=="" set PORT=%~1

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 serve.py %PORT%
  goto end
)
where python >nul 2>nul
if %errorlevel%==0 (
  python serve.py %PORT%
  goto end
)
where python3 >nul 2>nul
if %errorlevel%==0 (
  python3 serve.py %PORT%
  goto end
)

echo.
echo [error] ไม่พบ Python ในเครื่องนี้
echo         ติดตั้งจาก https://www.python.org/downloads/ แล้วเปิดไฟล์นี้อีกครั้ง
echo         หรือเปิดเว็บออนไลน์ที่ https://kittanasan.github.io/liver-fat-web/
echo.
pause

:end
echo.
echo ปิดเซิร์ฟเวอร์แล้ว
pause
