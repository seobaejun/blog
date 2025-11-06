"""
Vercel Serverless Function for Flask App
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Vercel 환경 설정
os.environ.setdefault('FLASK_ENV', 'production')

try:
    # Flask 앱 import
    from admin_web.app import app
    
    # Vercel Python 런타임은 app 객체를 자동으로 WSGI 앱으로 인식합니다
    # app 객체를 export하면 Vercel이 자동으로 처리합니다
    __all__ = ['app']
    
except Exception as e:
    # 에러 발생 시 디버깅을 위한 간단한 앱 생성
    from flask import Flask
    import traceback
    
    error_app = Flask(__name__)
    
    @error_app.route('/', defaults={'path': ''})
    @error_app.route('/<path:path>')
    def error_handler(path):
        error_msg = f"""
        <h1>Flask 앱 로드 오류</h1>
        <pre>{str(e)}</pre>
        <h2>Traceback:</h2>
        <pre>{traceback.format_exc()}</pre>
        """
        return error_msg, 500
    
    app = error_app
    __all__ = ['app']

