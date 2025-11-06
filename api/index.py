"""
Vercel Serverless Function for Flask App
"""
import sys
import os
from pathlib import Path
import traceback

# 프로젝트 루트를 Python 경로에 추가
try:
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
except Exception as e:
    print(f"Failed to set project root: {e}", file=sys.stderr)

# Vercel 환경 설정
os.environ.setdefault('FLASK_ENV', 'production')

# 실제 Flask 앱 import 시도
try:
    from admin_web.app import app
    print("✅ Admin app loaded successfully!", file=sys.stderr)
except Exception as e:
    # 에러 발생 시 상세한 에러 페이지 앱 생성
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
        <pre style="background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto;">{str(e)}</pre>
        <h2>Traceback:</h2>
        <pre style="background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto;">{traceback.format_exc()}</pre>
        <h2>디버깅 정보:</h2>
        <ul>
        <li>Project root: {project_root if 'project_root' in locals() else 'N/A'}</li>
        <li>Config exists: {(project_root / 'config.json').exists() if 'project_root' in locals() else 'N/A'}</li>
        <li>Python path: {sys.path[:3]}</li>
        </ul>
        </body>
        </html>
        """
        return error_html, 500
    
    app = error_app
    print(f"❌ Failed to load admin app: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)

__all__ = ['app']

