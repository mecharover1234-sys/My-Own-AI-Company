@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   AI Research Team - Build
echo ========================================
echo.

:: 아이콘 미리 생성
python -c "
import os, sys
sys.path.insert(0, '.')
from main import _make_app_icon
_make_app_icon()
print('Icon generated.')
" 2>nul || echo (icon generation skipped)

:: PyInstaller 빌드
echo [1/2] Building exe...
pyinstaller AI_Research_Team.spec --noconfirm --clean
if errorlevel 1 (
    echo.
    echo BUILD FAILED.
    pause
    exit /b 1
)

:: ZIP 압축
echo [2/2] Zipping dist folder...
powershell -NoProfile -Command ^
  "Compress-Archive -Path 'dist\AI_Research_Team' -DestinationPath 'dist\AI_Research_Team_Windows.zip' -Force"

echo.
echo ========================================
echo   Build complete!
echo   dist\AI_Research_Team\AI_Research_Team.exe
echo   dist\AI_Research_Team_Windows.zip
echo ========================================
pause
