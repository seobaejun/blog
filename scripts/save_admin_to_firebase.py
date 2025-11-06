"""
Firebase REST API를 사용하여 관리자 정보를 직접 저장하는 스크립트
"""
import sys
from pathlib import Path
import requests
import json
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.firebase_config import get_auth, get_db


def save_admin_via_rest_api(email, password):
    """
    Firebase REST API를 사용하여 관리자 정보 저장
    """
    try:
        auth = get_auth()
        
        # 로그인해서 토큰 가져오기
        user_info = auth.sign_in_with_email_and_password(email, password)
        user_id = user_info.get("localId", "")
        id_token = user_info.get("idToken", "")
        
        print(f"✓ 로그인 성공 (UID: {user_id})")
        
        # 관리자 정보
        admin_data = {
            "user_id": user_id,
            "email": email,
            "name": "관리자",
            "approved": True,
            "is_admin": True,
            "created_at": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat()
        }
        
        # Firebase Realtime Database REST API로 저장
        database_url = "https://blog-cdc9b-default-rtdb.firebaseio.com"
        path = f"/users/{user_id}.json"
        url = f"{database_url}{path}?auth={id_token}"
        
        print(f"데이터베이스에 저장 시도 중...")
        response = requests.put(url, json=admin_data)
        
        if response.status_code == 200:
            print(f"✓ Firebase 데이터베이스에 관리자 정보 저장 완료!")
            print(f"\n저장된 경로: users/{user_id}")
            print(f"저장된 데이터:")
            print(json.dumps(admin_data, indent=2, ensure_ascii=False))
            return True
        else:
            print(f"❌ 저장 실패: HTTP {response.status_code}")
            print(f"응답: {response.text}")
            
            # 인증 없이 시도 (규칙이 허용하는 경우)
            if response.status_code == 401:
                print(f"\n⚠ 인증 오류. 데이터베이스 규칙을 확인하세요.")
                print(f"Firebase Console에서 다음 규칙 설정:")
                print(f"{{")
                print(f"  'rules': {{")
                print(f"    'users': {{")
                print(f"      '.read': true,")
                print(f"      '.write': true")
                print(f"    }}")
                print(f"  }}")
                print(f"}}")
            
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
    print("Firebase REST API로 관리자 정보 저장")
    print("=" * 60)
    print()
    
    save_admin_via_rest_api(admin_email, admin_password)


