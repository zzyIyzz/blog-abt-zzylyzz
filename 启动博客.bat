@echo off
chcp 65001 >nul
title Hugo Blog Manager
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "%~dp0start.ps1"
pause
