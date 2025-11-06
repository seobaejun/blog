"""
간단한 테스트 스크립트 - 서버 실행 전 오류 확인
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    print("1. Firebase 설정 확인 중...")
    from src.firebase_config import get_auth, get_db
    print("   ✓ Firebase 설정 로드 성공")
    
    print("2. Firebase 인스턴스 초기화 중...")
    db = get_db()
    auth = get_auth()
    print("   ✓ Firebase 인스턴스 생성 성공")
    
    print("3. Flask 앱 import 중...")
    from admin_web.app import app
    print("   ✓ Flask 앱 import 성공")
    
    print("\n✅ 모든 테스트 통과! 서버를 실행할 수 있습니다.")
    print("\n서버 실행 방법:")
    print("  cd admin_web")
    print("  python app.py")
    print("\n그 다음 브라우저에서 http://localhost:5000 으로 접속하세요.")

except Exception as e:
    print(f"\n❌ 오류 발생: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

