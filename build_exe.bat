@echo off
chcp 65001 >nul
echo ========================================
echo 네이버 블로그 자동화 프로그램 exe 빌드
echo ========================================
echo.

REM Python 가상환경 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    pause
    exit /b 1
)

echo [1/4] 클라이언트 의존성 설치 중...
pip install -r requirements_client.txt
if errorlevel 1 (
    echo [오류] 의존성 설치 실패
    pause
    exit /b 1
)

echo.
echo [2/4] PyInstaller 설치 확인 중...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller가 설치되어 있지 않습니다. 설치 중...
    pip install pyinstaller
    if errorlevel 1 (
        echo [오류] PyInstaller 설치 실패
        pause
        exit /b 1
    )
)

echo.
echo [3/4] exe 파일 빌드 중...
pyinstaller build_exe.spec --clean
if errorlevel 1 (
    echo [오류] exe 빌드 실패
    pause
    exit /b 1
)

echo.
echo [4/4] 빌드 완료!
echo.
echo ========================================
echo 빌드 결과:
echo ========================================
echo exe 파일 위치: dist\NaverBlogAuto.exe
echo.
echo 중요: config.json 파일을 exe와 같은 폴더에 배치해야 합니다.
echo.
pause

