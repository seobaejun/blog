"""
Firebase Functions용 Flask 애플리케이션 엔트리 포인트
"""
import sys
from pathlib import Path
import os

# Firebase Functions 환경 설정
os.environ.setdefault('FLASK_ENV', 'production')

# 프로젝트 루트를 Python 경로에 추가
# 배포 시 admin_web과 src가 firebase_functions 디렉토리 안에 복사되므로
# 현재 디렉토리(firebase_functions)를 프로젝트 루트로 사용
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Flask 앱 import
from admin_web.app import app as flask_app

# Firebase Functions v2 HTTP 함수로 Flask 앱 래핑
from functions_framework import http

@http
def app(request):
    """
    Firebase Functions HTTP 함수
    Flask 앱을 HTTP 요청으로 처리합니다.
    """
    # functions_framework의 Request 객체에서 정보 추출
    method = request.method
    path = request.path if hasattr(request, 'path') else '/'
    
    # 쿼리 스트링 추출
    query_string = ''
    if hasattr(request, 'args'):
        # Flask의 request.args와 유사하게 처리
        query_string = '&'.join([f"{k}={v}" for k, v in request.args.items()])
    elif hasattr(request, 'query_string'):
        query_string = request.query_string if isinstance(request.query_string, str) else request.query_string.decode('utf-8')
    
    # 헤더 처리
    headers = {}
    if hasattr(request, 'headers'):
        if hasattr(request.headers, 'items'):
            headers = dict(request.headers.items())
        elif isinstance(request.headers, dict):
            headers = request.headers
        else:
            # headers가 다른 형태일 경우
            for key in dir(request.headers):
                if not key.startswith('_'):
                    try:
                        headers[key] = getattr(request.headers, key)
                    except:
                        pass
    
    # 요청 본문 처리
    data = b''
    if hasattr(request, 'get_data'):
        try:
            data = request.get_data(as_text=False)
        except:
            try:
                data = request.get_data()
            except:
                data = b''
    elif hasattr(request, 'data'):
        data = request.data if isinstance(request.data, bytes) else str(request.data).encode('utf-8')
    elif hasattr(request, 'body'):
        data = request.body if isinstance(request.body, bytes) else str(request.body).encode('utf-8')
    
    # Flask 요청 컨텍스트 생성
    try:
        with flask_app.test_request_context(
            path=path,
            method=method,
            headers=headers,
            query_string=query_string.encode('utf-8') if query_string else b'',
            data=data,
            content_type=headers.get('Content-Type', ''),
        ):
            with flask_app.app_context():
                # Flask 앱에서 응답 생성
                response = flask_app.full_dispatch_request()
                
                # Functions Framework 형식으로 반환
                return (
                    response.get_data(),
                    response.status_code,
                    dict(response.headers)
                )
    except Exception as e:
        # 에러 발생 시 에러 메시지 반환
        import traceback
        error_message = f"Error processing request: {str(e)}\n{traceback.format_exc()}"
        return (
            error_message.encode('utf-8'),
            500,
            {'Content-Type': 'text/plain; charset=utf-8'}
        )
