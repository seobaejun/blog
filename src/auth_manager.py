"""
Firebase 인증 관리 모듈
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from src.firebase_config import get_auth, get_db


class AuthManager:
    """Firebase 인증 관리 클래스"""
    
    def __init__(self):
        """인증 관리자 초기화"""
        self.auth = get_auth()
        self.db = get_db()
        self.user = None
        self.token = None
        # Vercel 서버리스 환경에서는 파일 시스템이 읽기 전용이므로
        # 세션 파일 경로는 설정하지만 디렉토리 생성은 시도하지 않음
        self.session_file = Path(__file__).parent.parent / "data" / "session.json"
        # 디렉토리 생성 시도 (실패해도 계속 진행)
        try:
            self.session_file.parent.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            # Vercel 등 읽기 전용 파일 시스템에서는 무시
            print(f"⚠ 세션 디렉토리 생성 실패 (서버리스 환경일 수 있음): {str(e)}")
        self._load_session()
    
    def _load_session(self):
        """저장된 세션 로드 (자동 로그인)"""
        try:
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
                except (OSError, PermissionError, IOError) as e:
                    # 파일 읽기 실패 (서버리스 환경 등)
                    print(f"⚠ 세션 파일 읽기 실패: {str(e)}")
                    return False
                except Exception:
                    self._clear_session()
        except Exception as e:
            # 파일 시스템 접근 실패는 무시 (서버리스 환경)
            print(f"⚠ 세션 로드 실패 (무시됨): {str(e)}")
        return False
    
    def _save_session(self, token, user_id, email=None):
        """세션 정보를 로컬 파일에 저장 (서버리스 환경에서는 무시)"""
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
        except (OSError, PermissionError, IOError) as e:
            # Vercel 등 읽기 전용 파일 시스템에서는 무시
            print(f"⚠ 세션 저장 실패 (서버리스 환경일 수 있음): {str(e)}")
        except Exception as e:
            print(f"⚠ 세션 저장 실패: {str(e)}")
    
    def _clear_session(self):
        """세션 정보 삭제"""
        try:
            if self.session_file.exists():
                try:
                    self.session_file.unlink()
                except (OSError, PermissionError, IOError):
                    # 파일 삭제 실패는 무시 (서버리스 환경)
                    pass
                except Exception:
                    pass
        except Exception:
            # 파일 시스템 접근 실패는 무시
            pass
        
        self.user = None
        self.token = None
    
    def signup(self, name, username, email, password, phone):
        """
        회원가입
        
        Args:
            name: 사용자 이름
            username: 사용자 아이디
            email: 사용자 이메일
            password: 사용자 비밀번호
            phone: 사용자 전화번호
        
        Returns:
            dict: 회원가입 결과
        
        Raises:
            Exception: 회원가입 실패 시
        """
        try:
            # Firebase Authentication 회원가입
            user_info = self.auth.create_user_with_email_and_password(email, password)
            
            user_id = user_info.get("localId", "")
            token = user_info.get("idToken", "")
            
            # Firestore에 사용자 정보 저장
            user_data = {
                "user_id": user_id,
                "name": name,
                "username": username,
                "email": email,
                "phone": phone,
                "approved": False,  # 관리자 승인 대기 상태
                "is_admin": False,
                "first_login_date": None,  # 첫 로그인 날짜 (아직 없음)
                "expiry_date": None,  # 이용 만료일 (아직 없음)
                "last_payment_date": None,
                "payment_pending": False,
                "created_at": datetime.now().isoformat(),
                "login_history": []
            }
            
            # Firestore에 사용자 정보 저장
            self.db.child("users").child(user_id).set(user_data)
            
            return {
                "success": True,
                "message": "회원가입이 완료되었습니다. 관리자 승인 후 로그인할 수 있습니다.",
                "user_id": user_id
            }
        
        except Exception as e:
            error_message = str(e)
            if "EMAIL_EXISTS" in error_message:
                raise Exception("이미 사용 중인 이메일입니다.")
            elif "WEAK_PASSWORD" in error_message:
                raise Exception("비밀번호가 너무 약합니다. 6자 이상 입력해주세요.")
            elif "INVALID_EMAIL" in error_message:
                raise Exception("유효하지 않은 이메일 형식입니다.")
            else:
                raise Exception(f"회원가입 중 오류가 발생했습니다: {error_message}")
    
    def check_approval_status(self, user_id):
        """
        사용자 승인 상태 확인
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            dict: 승인 상태 정보
        """
        try:
            user_data = self.db.child("users").child(user_id).get().val()
            
            if not user_data:
                return {
                    "approved": False,
                    "message": "사용자 정보를 찾을 수 없습니다."
                }
            
            approved = user_data.get("approved", False)
            
            return {
                "approved": approved,
                "message": "관리자 승인 대기 중입니다." if not approved else "승인되었습니다."
            }
        
        except Exception as e:
            return {
                "approved": False,
                "message": f"승인 상태 확인 중 오류가 발생했습니다: {str(e)}"
            }
    
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
            
            # 승인 상태 확인
            approval_status = self.check_approval_status(user_id)
            if not approval_status.get("approved", False):
                raise Exception("관리자 승인이 필요합니다. 승인 후 다시 시도해주세요.")
            
            # 사용자 정보 가져오기
            user_data = self.db.child("users").child(user_id).get().val()
            
            # 첫 로그인인지 확인하고 날짜 기록
            if user_data and not user_data.get("first_login_date"):
                first_login_date = datetime.now().isoformat()
                expiry_date = (datetime.now() + timedelta(days=30)).isoformat()
                
                self.db.child("users").child(user_id).update({
                    "first_login_date": first_login_date,
                    "expiry_date": expiry_date
                })
            
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
            elif "관리자 승인" in error_message:
                raise Exception(error_message)
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
