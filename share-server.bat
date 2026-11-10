@echo off
chcp 65001 >nul
cd /d "%~dp0"
title liverV1 - share to other computers

echo ============================================================
echo  liverV1 - เปิดเว็บให้เครื่องอื่นในวงเดียวกันเข้าใช้งาน
echo ============================================================
echo.

set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (
  where python >nul 2>nul && set "PY=python"
)
if not defined PY (
  echo [error] ไม่พบ Python ในเครื่องนี้
  echo         ติดตั้ง Python จาก https://www.python.org/downloads/ แล้วรันไฟล์นี้อีกครั้ง
  echo.
  pause
  exit /b 1
)

echo [firewall] เปิดทางให้เครื่องอื่นเชื่อมต่อ (Windows จะถามยืนยัน 1 ครั้ง)
netsh advfirewall firewall add rule name="liverV1 Web 8080" dir=in action=allow protocol=TCP localport=8080 profile=private >nul 2>nul

echo [server] กำลังเปิดเซิร์ฟเวอร์ ... ปิดหน้าต่างนี้ = หยุดให้บริการ
echo.
%PY% serve.py
echo.
pause
