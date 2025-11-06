"""
Vercel Serverless Function for Flask App
"""
import sys
import os
from pathlib import Path
import traceback

# 에러 로깅을 위한 함수
def log_error(msg, error=None):
    """에러를 stderr에 출력 (Vercel 로그에서 확인 가능)"""
    print(f"ERROR: {msg}", file=sys.stderr)
    if error:
        print(f"Exception: {error}", file=sys.stderr)
        print(f"Traceback:\n{traceback.format_exc()}", file=sys.stderr)

# 프로젝트 루트를 Python 경로에 추가
project_root = None
config_path = None

try:
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    log_error(f"Project root added: {project_root}")
    
    # config.json 경로 확인
    config_path = project_root / "config.json"
    log_error(f"Config path: {config_path}, exists: {config_path.exists()}")
except Exception as e:
    log_error("Failed to set project root", e)

# Vercel 환경 설정
os.environ.setdefault('FLASK_ENV', 'production')

# 최소한의 테스트 앱 먼저 생성
from flask import Flask
test_app = Flask(__name__)

@test_app.route('/')
def test_root():
    return '<h1>Vercel Flask Test</h1><p>기본 Flask 앱이 작동합니다!</p>'

try:
    # Flask 앱 import
    log_error("Attempting to import Flask app...")
    from admin_web.app import app as flask_app
    log_error("Flask app imported successfully")
    
    # 실제 Flask 앱 사용
    app = flask_app
    __all__ = ['app']
    
except Exception as e:
    # 에러 발생 시 디버깅을 위한 간단한 앱 생성
    log_error("Failed to import Flask app", e)
    
    try:
        from flask import Flask
        
        error_app = Flask(__name__)
        
        @error_app.route('/', defaults={'path': ''})
        @error_app.route('/<path:path>')
        def error_handler(path):
            error_msg = f"""
            <html>
            <head><title>Flask 앱 로드 오류</title></head>
            <body>
            <h1>Flask 앱 로드 오류</h1>
            <h2>에러 메시지:</h2>
            <pre>{str(e)}</pre>
            <h2>Traceback:</h2>
            <pre>{traceback.format_exc()}</pre>
            <h2>디버깅 정보:</h2>
            <ul>
            <li>Project root: {project_root}</li>
            <li>Config path: {config_path}</li>
            <li>Config exists: {config_path.exists()}</li>
            <li>Python path: {sys.path}</li>
            </ul>
            </body>
            </html>
            """
            return error_msg, 500
        
        app = error_app
        __all__ = ['app']
        log_error("Error app created")
        
    except Exception as e2:
        log_error("Failed to create error app", e2)
        # 최후의 수단: 빈 Flask 앱
        from flask import Flask
        app = Flask(__name__)
        __all__ = ['app']

