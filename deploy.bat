@echo off
echo ============================================================
echo Firebase Functions 배포 스크립트
echo ============================================================
echo.

echo [1/4] Firebase CLI 버전 확인...
firebase --version
if errorlevel 1 (
    echo Firebase CLI가 설치되지 않았습니다.
    echo 설치 중...
    npm install -g firebase-tools
    if errorlevel 1 (
        echo Firebase CLI 설치 실패
        pause
        exit /b 1
    )
)
echo.

echo [2/4] Firebase 로그인 확인...
firebase projects:list >nul 2>&1
if errorlevel 1 (
    echo Firebase 로그인이 필요합니다.
    echo 브라우저가 열리면 로그인을 진행해주세요.
    firebase login
    if errorlevel 1 (
        echo 로그인 실패
        pause
        exit /b 1
    )
)
echo.

echo [3/4] Firebase 프로젝트 설정...
firebase use blog-cdc9b
if errorlevel 1 (
    echo 프로젝트 설정 실패
    pause
    exit /b 1
)
echo.

echo [4/4] Functions 배포 시작...
echo 이 작업은 몇 분이 걸릴 수 있습니다.
firebase deploy --only functions
if errorlevel 1 (
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


