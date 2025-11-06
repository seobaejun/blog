"""
Vercel Serverless Function for Flask App
최소한의 테스트 앱으로 시작
"""
from flask import Flask

# 최소한의 Flask 앱 생성
app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <html>
    <head><title>Vercel Flask Test</title></head>
    <body style="font-family: Arial; padding: 20px;">
    <h1>✅ Vercel Flask 앱이 정상적으로 작동합니다!</h1>
    <p>이 메시지가 보이면 Flask 앱이 Vercel에서 정상적으로 실행되고 있습니다.</p>
    <hr>
    <h2>다음 단계:</h2>
    <p>이제 실제 관리자 페이지 앱을 로드하도록 수정하겠습니다.</p>
    </body>
    </html>
    '''

@app.route('/test')
def test():
    return '<h1>Test Route</h1><p>테스트 라우트가 작동합니다!</p>'

__all__ = ['app']

