"""
관리자 계정 생성 스크립트
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.firebase_config import get_auth, get_db
from datetime import datetime


def create_admin_account(email, password, name="관리자"):
    """
    관리자 계정 생성
    
    Args:
        email: 관리자 이메일
        password: 관리자 비밀번호
        name: 관리자 이름
    """
    try:
        auth = get_auth()
        db = get_db()
        
        print(f"관리자 계정 생성 중: {email}")
        
        # Firebase Authentication에 계정 생성
        try:
            user_info = auth.create_user_with_email_and_password(email, password)
            user_id = user_info.get("localId", "")
            print(f"✓ Firebase Authentication 계정 생성 완료 (UID: {user_id})")
        except Exception as e:
            error_msg = str(e)
            if "EMAIL_EXISTS" in error_msg:
                print("⚠ 이메일이 이미 존재합니다. 기존 계정을 사용합니다.")
                # 기존 계정으로 로그인해서 user_id 가져오기
                user_info = auth.sign_in_with_email_and_password(email, password)
                user_id = user_info.get("localId", "")
            else:
                raise Exception(f"계정 생성 실패: {error_msg}")
        
        # Firebase Realtime Database에 관리자 정보 저장
        admin_data = {
            "user_id": user_id,
            "email": email,
            "name": name,
            "approved": True,  # 관리자는 자동 승인
            "is_admin": True,  # 관리자 플래그
            "first_login_date": None,
            "expiry_date": None,
            "last_payment_date": None,
            "payment_pending": False,
            "created_at": datetime.now().isoformat(),
            "login_history": {}
        }
        
        # Firebase Realtime Database에 저장 (규칙 허용 필요)
        try:
            db.child("users").child(user_id).set(admin_data)
            print(f"✓ Firebase에 관리자 정보 저장 완료")
        except Exception as db_error:
            # 데이터베이스 규칙 문제일 수 있으므로, 일단 계정만 생성하고 나중에 수동으로 설정 가능
            print(f"⚠ Firebase 데이터베이스 저장 실패: {str(db_error)}")
            print(f"   Firebase Console에서 수동으로 다음 정보를 설정하세요:")
            print(f"   - users/{user_id}/is_admin = true")
            print(f"   - users/{user_id}/approved = true")
            print(f"   - users/{user_id}/email = {email}")
            print(f"   - users/{user_id}/name = {name}")
        print(f"\n✅ 관리자 계정 생성 완료!")
        print(f"   이메일: {email}")
        print(f"   사용자 ID: {user_id}")
        print(f"\n이제 관리자 페이지에서 로그인할 수 있습니다.")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 관리자 계정 정보
    admin_email = "sprince1004@naver.com"
    admin_password = "skybj6942"
    admin_name = "관리자"
    
    print("=" * 50)
    print("관리자 계정 생성 스크립트")
    print("=" * 50)
    
    create_admin_account(admin_email, admin_password, admin_name)
