"""
Firestore Database에 관리자 정보를 저장하는 스크립트
"""
import sys
from pathlib import Path
import json
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    print("firebase-admin 패키지가 설치되지 않았습니다.")
    print("설치 중...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "firebase-admin"])
    import firebase_admin
    from firebase_admin import credentials, firestore


def initialize_firestore():
    """Firestore 초기화"""
    try:
        # 이미 초기화되어 있는지 확인
        firestore.client()
        print("✓ Firestore가 이미 초기화되어 있습니다.")
        return True
    except (ValueError, AttributeError):
        # config.json에서 Firebase 설정 로드
        config_path = project_root / "config.json"
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        
        firebase_config = config_data.get("firebase", {})
        project_id = firebase_config.get('projectId', 'blog-cdc9b')
        
        try:
            # Application Default Credentials 시도
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {'projectId': project_id})
            print("✓ Firestore 초기화 성공 (Application Default Credentials)")
            return True
        except Exception:
            try:
                # 직접 초기화 시도 (Service Account Key 없이)
                firebase_admin.initialize_app(options={'projectId': project_id})
                print("✓ Firestore 직접 초기화 성공")
                return True
            except Exception as e:
                print(f"⚠ Firestore Admin SDK 초기화 실패: {str(e)}")
                print(f"   Firestore REST API를 사용합니다...")
                return False


def save_admin_to_firestore(email, password):
    """
    Firestore에 관리자 정보 저장 (REST API 사용)
    """
    try:
        if not password:
            print("⚠ 비밀번호가 필요합니다.")
            return False
        
        from src.firebase_config import get_auth
        auth = get_auth()
        
        # 로그인해서 토큰 가져오기
        print(f"🔐 Firebase Authentication 로그인 중...")
        user_info = auth.sign_in_with_email_and_password(email, password)
        user_id = user_info.get("localId", "")
        id_token = user_info.get("idToken", "")
        
        print(f"✓ 로그인 성공 (UID: {user_id})")
        
        # Firestore REST API로 저장
        import requests
        
        # Firestore REST API URL
        project_id = "blog-cdc9b"
        # 문서 ID는 user_id를 사용 (더 안전함)
        doc_id = user_id
        firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users/{doc_id}"
        
        # 현재 시간 (ISO 8601 형식)
        now = datetime.now()
        now_iso = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        # Firestore 문서 형식으로 데이터 변환
        firestore_doc = {
            "fields": {
                "email": {"stringValue": email},
                "user_id": {"stringValue": user_id},
                "name": {"stringValue": "관리자"},
                "approved": {"booleanValue": True},
                "is_admin": {"booleanValue": True},
                "created_at": {"timestampValue": now_iso},
                "last_login": {"timestampValue": now_iso},
                "role": {"stringValue": "admin"}
            }
        }
        
        headers = {
            "Authorization": f"Bearer {id_token}",
            "Content-Type": "application/json"
        }
        
        print(f"🔍 Firestore에 저장 시도 중...")
        print(f"   URL: {firestore_url}")
        print(f"   문서 ID (user_id): {doc_id}")
        print(f"   이메일: {email}")
        
        # PATCH 메서드로 문서 생성/업데이트
        response = requests.patch(firestore_url, json=firestore_doc, headers=headers, timeout=10)
        
        print(f"   응답 코드: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"✓ Firestore에 관리자 정보 저장 완료!")
            print(f"\n저장된 경로: users/{doc_id} (user_id)")
            print(f"이메일: {email}")
            print(f"저장된 데이터:")
            print(json.dumps({
                "email": email,
                "user_id": user_id,
                "name": "관리자",
                "approved": True,
                "is_admin": True,
                "created_at": now_iso,
                "last_login": now_iso,
                "role": "admin"
            }, indent=2, ensure_ascii=False))
            
            # 저장 확인
            verify_response = requests.get(firestore_url, headers=headers, timeout=5)
            if verify_response.status_code == 200:
                print(f"\n✓ 저장 확인 완료")
                return True
            else:
                print(f"\n⚠ 저장 확인 실패: {verify_response.status_code}")
                return True  # 저장은 성공했으므로 True 반환
        else:
            print(f"❌ Firestore REST API 저장 실패: HTTP {response.status_code}")
            print(f"응답: {response.text[:500]}")
            
            # 권한 오류인 경우
            if response.status_code == 403:
                print(f"\n⚠ Firestore 보안 규칙 문제입니다.")
                print(f"Firebase Console에서 Firestore 규칙을 확인하세요:")
                print(f"  - Firestore Database > 규칙 탭")
                print(f"  - users 컬렉션에 쓰기 권한이 있는지 확인")
            
            return False
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    admin_email = "sprince1004@naver.com"
    admin_password = "skybj6942"
    
    print("=" * 60)
    print("Firestore Database에 관리자 정보 저장")
    print("=" * 60)
    print()
    
    save_admin_to_firestore(admin_email, admin_password)

