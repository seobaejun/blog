"""
Vercel Serverless Function for Flask App
"""
import sys
import os
from pathlib import Path
import traceback

# 모든 출력을 stderr로 (Vercel 로그에서 확인 가능)
def log(msg):
    print(f"[VERCEL] {msg}", file=sys.stderr, flush=True)

log("Starting Vercel function...")

# 프로젝트 루트를 Python 경로에 추가
try:
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    log(f"Project root: {project_root}")
    
    # config.json 경로 확인
    config_path = project_root / "config.json"
    log(f"Config path: {config_path}, exists: {config_path.exists()}")
    
    # 파일 목록 확인
    log(f"Files in project root: {list(project_root.iterdir())[:10]}")
except Exception as e:
    log(f"Failed to set project root: {e}")
    traceback.print_exc(file=sys.stderr)

# Vercel 환경 설정
os.environ.setdefault('FLASK_ENV', 'production')

# Flask 앱 import 시도
app = None
try:
    log("Importing Flask...")
    from flask import Flask
    
    log("Creating test Flask app...")
    test_app = Flask(__name__)
    
    @test_app.route('/')
    def test():
        return '<h1>Vercel Flask Test</h1><p>기본 Flask 앱이 작동합니다!</p>'
    
    log("Attempting to import admin_web.app...")
    from admin_web.app import app as flask_app
    log("Flask app imported successfully!")
    
    app = flask_app
    
except Exception as e:
    log(f"Error importing Flask app: {e}")
    traceback.print_exc(file=sys.stderr)
    
    # 에러 페이지 앱 생성
    try:
        from flask import Flask
        error_app = Flask(__name__)
        
        @error_app.route('/', defaults={'path': ''})
        @error_app.route('/<path:path>')
        def error_handler(path):
            error_html = f"""
            <html>
            <head><title>Flask 앱 로드 오류</title></head>
            <body style="font-family: Arial; padding: 20px;">
            <h1>Flask 앱 로드 오류</h1>
            <h2>에러 메시지:</h2>
            <pre style="background: #f5f5f5; padding: 10px; border-radius: 5px;">{str(e)}</pre>
            <h2>Traceback:</h2>
            <pre style="background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto;">{traceback.format_exc()}</pre>
            <h2>디버깅 정보:</h2>
            <ul>
            <li>Project root: {project_root if 'project_root' in locals() else 'N/A'}</li>
            <li>Config path: {config_path if 'config_path' in locals() else 'N/A'}</li>
            <li>Config exists: {config_path.exists() if 'config_path' in locals() else 'N/A'}</li>
            <li>Python path: {sys.path[:5]}</li>
            </ul>
            </body>
            </html>
            """
            return error_html, 500
        
        app = error_app
        log("Error app created")
    except Exception as e2:
        log(f"Failed to create error app: {e2}")
        traceback.print_exc(file=sys.stderr)
        # 최후의 수단
        from flask import Flask
        app = Flask(__name__)
        @app.route('/')
        def fallback():
            return f'<h1>Fallback App</h1><p>Error: {str(e2)}</p>', 500

if app is None:
    log("CRITICAL: app is None, creating minimal Flask app")
    from flask import Flask
    app = Flask(__name__)
    @app.route('/')
    def minimal():
        return '<h1>Minimal Flask App</h1><p>App was None</p>', 500

log("App setup complete, exporting app object")
__all__ = ['app']

