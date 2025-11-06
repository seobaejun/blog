@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================================
echo Firebase Functions 배포
echo ============================================================
echo.
echo 현재 위치: %CD%
echo.
echo [1/3] Firebase 프로젝트 설정...
firebase use blog-cdc9b
if errorlevel 1 (
    echo 프로젝트 설정 실패
    echo.
    echo Firebase 로그인이 필요합니다.
    echo firebase login 명령어를 먼저 실행하세요.
    pause
    exit /b 1
)
echo.
echo [2/3] Functions 배포 시작...
echo 이 작업은 몇 분이 걸릴 수 있습니다.
echo.
firebase deploy --only functions
if errorlevel 1 (
    echo.
    echo 배포 실패
    pause
    exit /b 1
)
echo.
echo ============================================================
echo 배포 완료!
echo ============================================================
echo.
echo Functions URL 확인:
firebase functions:list
echo.
pause


