"""
Firebase Realtime Database에 관리자 정보 업데이트 스크립트
(데이터베이스 규칙 문제로 인해 수동 업데이트용)
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.firebase_config import get_auth, get_db
from datetime import datetime


def update_admin_in_database(email, password):
    """
    기존 관리자 계정의 데이터베이스 정보 업데이트
    """
    try:
        auth = get_auth()
        db = get_db()
        
        print(f"관리자 계정 정보 업데이트 중: {email}")
        
        # 로그인해서 user_id 가져오기
        user_info = auth.sign_in_with_email_and_password(email, password)
        user_id = user_info.get("localId", "")
        
        print(f"사용자 ID: {user_id}")
        
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
        
        # Firebase Realtime Database에 업데이트
        try:
            # 기존 데이터 확인
            existing = db.child("users").child(user_id).get().val()
            if existing:
                # 기존 데이터와 병합
                admin_data.update(existing)
                admin_data["is_admin"] = True
                admin_data["approved"] = True
            
            db.child("users").child(user_id).set(admin_data)
            print(f"✓ Firebase 데이터베이스 업데이트 완료")
            return True
            
        except Exception as db_error:
            print(f"❌ 데이터베이스 업데이트 실패: {str(db_error)}")
            print(f"\nFirebase Console에서 다음 경로에 수동으로 설정하세요:")
            print(f"   Realtime Database > users > {user_id}")
            print(f"   - is_admin: true (boolean)")
            print(f"   - approved: true (boolean)")
            print(f"   - email: {email}")
            print(f"   - name: 관리자")
            return False
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    admin_email = "sprince1004@naver.com"
    admin_password = "skybj6942"
    
    print("=" * 50)
    print("관리자 데이터베이스 정보 업데이트")
    print("=" * 50)
    
    update_admin_in_database(admin_email, admin_password)
