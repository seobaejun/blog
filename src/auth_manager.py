"""
Firebase 인증 관리 모듈
"""
import json
from pathlib import Path
from datetime import datetime
from src.firebase_config import get_auth, get_db


class AuthManager:
    """Firebase 인증 관리 클래스"""
    
    def __init__(self):
        """인증 관리자 초기화"""
        self.auth = get_auth()
        self.db = get_db()
        self.user = None
        self.token = None
        self.session_file = Path(__file__).parent.parent / "data" / "session.json"
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_session()
    
    def _load_session(self):
        """저장된 세션 로드 (자동 로그인)"""
        if self.session_file.exists():
            try:
                with open(self.session_file, "r", encoding="utf-8") as f:
                    session_data = json.load(f)
                
                if "token" in session_data and "user_id" in session_data:
                    # 토큰 저장 및 사용자 정보 추출
                    self.token = session_data["token"]
                    user_id = session_data.get("user_id", "")
                    email = session_data.get("email", "")
                    
                    # 간단한 사용자 정보 구조 생성
                    self.user = {
                        "users": [{
                            "localId": user_id,
                            "email": email
                        }]
                    }
                    return True
            except Exception:
                self._clear_session()
        return False
    
    def _save_session(self, token, user_id, email=None):
        """세션 정보를 로컬 파일에 저장"""
        session_data = {
            "token": token,
            "user_id": user_id,
            "saved_at": datetime.now().isoformat()
        }
        
        if email:
            session_data["email"] = email
        
        try:
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"세션 저장 실패: {str(e)}")
    
    def _clear_session(self):
        """세션 정보 삭제"""
        if self.session_file.exists():
            try:
                self.session_file.unlink()
            except Exception:
                pass
        
        self.user = None
        self.token = None
    
    def login(self, email, password):
        """
        이메일/비밀번호로 로그인
        
        Args:
            email: 사용자 이메일
            password: 사용자 비밀번호
        
        Returns:
            dict: 사용자 정보와 토큰이 포함된 딕셔너리
        
        Raises:
            Exception: 로그인 실패 시
        """
        try:
            # Firebase Authentication 로그인
            user_info = self.auth.sign_in_with_email_and_password(email, password)
            
            self.token = user_info.get("idToken")
            user_id = user_info.get("localId", "")
            
            # 사용자 정보 구조 생성
            self.user = {
                "users": [{
                    "localId": user_id,
                    "email": email
                }]
            }
            
            # 세션 저장
            self._save_session(self.token, user_id, email)
            
            # 로그인 기록을 Firestore에 저장
            self._save_login_history(user_id, email)
            
            return {
                "success": True,
                "user": self.user,
                "token": self.token
            }
        
        except Exception as e:
            error_message = str(e)
            if "INVALID_PASSWORD" in error_message or "EMAIL_NOT_FOUND" in error_message:
                raise Exception("로그인에 실패했습니다. 이메일과 비밀번호를 확인해주세요.")
            elif "INVALID_EMAIL" in error_message:
                raise Exception("유효하지 않은 이메일 형식입니다.")
            else:
                raise Exception(f"로그인 중 오류가 발생했습니다: {error_message}")
    
    def logout(self):
        """로그아웃"""
        try:
            if self.token:
                # Firebase에서 로그아웃 (선택사항)
                pass
            
            self._clear_session()
            
            return {
                "success": True,
                "message": "로그아웃되었습니다."
            }
        except Exception as e:
            raise Exception(f"로그아웃 중 오류가 발생했습니다: {str(e)}")
    
    def is_logged_in(self):
        """로그인 상태 확인"""
        return self.user is not None and self.token is not None
    
    def get_user_info(self):
        """현재 로그인한 사용자 정보 반환"""
        if not self.is_logged_in():
            return None
        
        try:
            user_data = self.user.get("users", [{}])[0]
            return {
                "email": user_data.get("email", ""),
                "user_id": user_data.get("localId", ""),
                "email_verified": user_data.get("emailVerified", False)
            }
        except Exception:
            return None
    
    def _save_login_history(self, user_id, email):
        """로그인 기록을 Firestore에 저장"""
        try:
            login_data = {
                "email": email,
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id
            }
            
            # users 컬렉션에 로그인 기록 저장
            self.db.child("users").child(user_id).child("login_history").push(login_data)
            
            # 마지막 로그인 시간 업데이트
            self.db.child("users").child(user_id).update({
                "last_login": datetime.now().isoformat(),
                "email": email
            })
        except Exception as e:
            # 로그 기록 실패는 치명적이지 않으므로 무시
            print(f"로그인 기록 저장 실패: {str(e)}")
    
    def save_task_log(self, task_type, success, target_url=None, error_message=None):
        """
        작업 로그를 Firestore에 저장
        
        Args:
            task_type: 작업 유형 ('neighbor_add', 'like', 'comment')
            success: 성공 여부 (bool)
            target_url: 대상 URL (선택사항)
            error_message: 오류 메시지 (선택사항)
        """
        if not self.is_logged_in():
            return
        
        try:
            user_id = self.get_user_info().get("user_id")
            if not user_id:
                return
            
            task_data = {
                "task_type": task_type,
                "success": success,
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id
            }
            
            if target_url:
                task_data["target_url"] = target_url
            
            if error_message:
                task_data["error_message"] = error_message
            
            # tasks 컬렉션에 저장
            self.db.child("tasks").push(task_data)
        
        except Exception as e:
            print(f"작업 로그 저장 실패: {str(e)}")
