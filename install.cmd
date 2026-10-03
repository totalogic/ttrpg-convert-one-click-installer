@echo off
setlocal
title TTRPG Convert One-Click Installer
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
set "INSTALL_EXIT=%ERRORLEVEL%"
echo.
if not "%INSTALL_EXIT%"=="0" echo Installation failed with exit code %INSTALL_EXIT%.
pause
exit /b %INSTALL_EXIT%
