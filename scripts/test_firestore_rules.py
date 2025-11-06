"""
Firestore 규칙 테스트 스크립트
"""
import sys
from pathlib import Path
import requests
import json

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.firebase_config import get_auth

ADMIN_EMAIL = "sprince1004@naver.com"
ADMIN_PASSWORD = "skybj6942"
PROJECT_ID = "blog-cdc9b"

def test_firestore_access():
    """Firestore 접근 테스트"""
    try:
        auth = get_auth()
        
        # 로그인해서 토큰 가져오기
        print(f"🔐 Firebase Authentication 로그인 중...")
        user_info = auth.sign_in_with_email_and_password(ADMIN_EMAIL, ADMIN_PASSWORD)
        user_id = user_info.get("localId", "")
        id_token = user_info.get("idToken", "")
        
        print(f"✓ 로그인 성공 (UID: {user_id})")
        print(f"✓ 토큰 획득 완료")
        
        # Firestore 규칙 확인을 위한 테스트 요청
        firestore_url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/users/{user_id}"
        
        headers = {
            "Authorization": f"Bearer {id_token}",
            "Content-Type": "application/json"
        }
        
        # 읽기 테스트
        print(f"\n📖 읽기 테스트...")
        read_response = requests.get(firestore_url, headers=headers, timeout=10)
        print(f"   응답 코드: {read_response.status_code}")
        if read_response.status_code == 200:
            print(f"   ✓ 읽기 성공")
        elif read_response.status_code == 404:
            print(f"   ⚠ 문서가 없음 (정상)")
        else:
            print(f"   ❌ 읽기 실패: {read_response.text[:300]}")
        
        # 쓰기 테스트
        print(f"\n✍️ 쓰기 테스트...")
        test_doc = {
            "fields": {
                "test": {"stringValue": "test_value"}
            }
        }
        write_response = requests.patch(firestore_url, json=test_doc, headers=headers, timeout=10)
        print(f"   응답 코드: {write_response.status_code}")
        if write_response.status_code in [200, 201]:
            print(f"   ✓ 쓰기 성공")
        else:
            print(f"   ❌ 쓰기 실패: {write_response.text[:300]}")
        
        # 규칙 확인 가이드
        print(f"\n" + "=" * 60)
        print(f"규칙 확인 가이드")
        print(f"=" * 60)
        print(f"Firebase Console에서 다음을 확인하세요:")
        print(f"1. Firestore Database > 규칙 탭")
        print(f"2. 현재 규칙이 다음과 같은지 확인:")
        print(f"")
        print(f"rules_version = '2';")
        print(f"service cloud.firestore {{")
        print(f"  match /databases/{{database}}/documents {{")
        print(f"    match /{{document=**}} {{")
        print(f"      allow read, write: if request.auth != null;")
        print(f"    }}")
        print(f"  }}")
        print(f"}}")
        print(f"")
        print(f"3. '게시' 버튼을 눌러 규칙을 적용했는지 확인")
        print(f"4. 규칙을 변경한 경우 몇 분 기다린 후 다시 시도")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("Firestore 규칙 테스트")
    print("=" * 60)
    print()
    test_firestore_access()


