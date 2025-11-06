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

log("=" * 60)
log("Starting Vercel function initialization...")
log("=" * 60)

# 프로젝트 루트를 Python 경로에 추가
project_root = None
try:
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    log(f"✓ Project root added: {project_root}")
    
    # config.json 확인
    config_path = project_root / "config.json"
    log(f"✓ Config path: {config_path}")
    log(f"✓ Config exists: {config_path.exists()}")
    
    # 파일 목록 확인
    files = [f.name for f in project_root.iterdir() if f.is_file()][:10]
    log(f"✓ Files in root: {files}")
except Exception as e:
    log(f"✗ Failed to set project root: {e}")
    traceback.print_exc(file=sys.stderr)

# Vercel 환경 설정
os.environ.setdefault('FLASK_ENV', 'production')

# Flask 앱 import 시도
app = None
error_message = None
error_traceback = None

try:
    log("Step 1: Importing Flask...")
    from flask import Flask
    log("✓ Flask imported")
    
    log("Step 2: Importing admin_web.app...")
    from admin_web.app import app as flask_app
    log("✓ Admin app imported successfully!")
    
    app = flask_app
    
except Exception as e:
    error_message = str(e)
    error_traceback = traceback.format_exc()
    log(f"✗ Error importing admin app: {e}")
    traceback.print_exc(file=sys.stderr)
    
    # 에러 페이지 앱 생성
    try:
        log("Creating error handler app...")
        from flask import Flask
        error_app = Flask(__name__)
        
        @error_app.route('/favicon.ico')
        def favicon():
            return '', 404
        
        @error_app.route('/', defaults={'path': ''})
        @error_app.route('/<path:path>')
        def error_handler(path):
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Flask 앱 로드 오류</title>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    h1 {{ color: #d32f2f; }}
                    pre {{ background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; border: 1px solid #ddd; }}
                    ul {{ line-height: 1.8; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>❌ Flask 앱 로드 오류</h1>
                    <h2>에러 메시지:</h2>
                    <pre>{error_message}</pre>
                    <h2>Traceback:</h2>
                    <pre>{error_traceback}</pre>
                    <h2>디버깅 정보:</h2>
                    <ul>
                        <li><strong>Project root:</strong> {project_root if project_root else 'N/A'}</li>
                        <li><strong>Config exists:</strong> {(project_root / 'config.json').exists() if project_root else 'N/A'}</li>
                        <li><strong>Python path:</strong> {sys.path[:5]}</li>
                        <li><strong>Current directory:</strong> {os.getcwd()}</li>
                    </ul>
                </div>
            </body>
            </html>
            """
            return error_html, 500
        
        app = error_app
        log("✓ Error handler app created")
        
    except Exception as e2:
        log(f"✗ Failed to create error app: {e2}")
        traceback.print_exc(file=sys.stderr)
        # 최후의 수단
        from flask import Flask
        app = Flask(__name__)
        @app.route('/')
        def fallback():
            return f'<h1>Critical Error</h1><p>{str(e2)}</p>', 500

if app is None:
    log("✗ CRITICAL: app is None!")
    from flask import Flask
    app = Flask(__name__)
    @app.route('/')
    def minimal():
        return '<h1>App was None</h1><p>Flask app failed to initialize</p>', 500

log("=" * 60)
log("App setup complete!")
log("=" * 60)

__all__ = ['app']

