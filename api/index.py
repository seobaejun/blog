"""
Vercel Serverless Function for Flask App
Vercel은 WSGI 앱을 직접 지원합니다.
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Flask 앱 import
from admin_web.app import app

# Vercel은 WSGI 앱(app 객체)을 자동으로 처리합니다
# app 객체를 export하면 Vercel이 WSGI로 인식합니다
__all__ = ['app']

