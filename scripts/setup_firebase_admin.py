"""
Firebase에 관리자 정보를 직접 저장하는 스크립트
(인증 토큰을 사용하여 저장)
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.firebase_config import get_auth, get_db
from datetime import datetime


def setup_admin_in_firebase(email, password):
    """
    관리자 정보를 Firebase에 저장
    """
    try:
        auth = get_auth()
        db = get_db()
        
        print(f"관리자 계정 로그인 및 데이터베이스 설정: {email}")
        
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
        
        # Firebase Realtime Database에 저장
        try:
            db.child("users").child(user_id).set(admin_data)
            print(f"✓ Firebase 데이터베이스에 관리자 정보 저장 완료!")
            print(f"\n저장된 정보:")
            print(f"  - 경로: users/{user_id}")
            print(f"  - is_admin: true")
            print(f"  - approved: true")
            print(f"  - email: {email}")
            return True
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 데이터베이스 저장 실패: {error_msg}")
            
            if "404" in error_msg or "Not Found" in error_msg:
                print(f"\n⚠ Firebase Realtime Database가 활성화되지 않았거나 규칙 문제입니다.")
                print(f"\n해결 방법:")
                print(f"1. Firebase Console > Realtime Database로 이동")
                print(f"2. 데이터베이스 생성 (없는 경우)")
                print(f"3. 규칙 탭에서 다음 규칙 설정:")
                print(f"   {{")
                print(f"     'rules': {{")
                print(f"       'users': {{")
                print(f"         '$uid': {{")
                print(f"           '.read': true,")
                print(f"           '.write': true")
                print(f"         }}")
                print(f"       }}")
                print(f"     }}")
                print(f"   }}")
                print(f"\n4. 또는 Firebase Console에서 수동으로 설정:")
                print(f"   - users/{user_id}/is_admin = true (boolean)")
                print(f"   - users/{user_id}/approved = true (boolean)")
                print(f"   - users/{user_id}/email = {email}")
                print(f"   - users/{user_id}/name = 관리자")
            
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
    print("Firebase 관리자 정보 설정 스크립트")
    print("=" * 60)
    print()
    
    setup_admin_in_firebase(admin_email, admin_password)
