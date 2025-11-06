"""
Firebase 인증 관리 모듈
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from src.firebase_config import get_auth


class AuthManager:
    """Firebase 인증 관리 클래스"""
    
    def __init__(self):
        """인증 관리자 초기화"""
        self.auth = get_auth()
        # Realtime Database는 더 이상 사용하지 않음 (Firestore만 사용)
        # self.db = get_db()  # 제거됨
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
            print(f"\n{'='*60}")
            print(f"[회원가입] Firebase Authentication 회원가입 시도")
            print(f"  Email: {email}")
            print(f"  Name: {name}")
            print(f"{'='*60}\n")
            
            user_info = self.auth.create_user_with_email_and_password(email, password)
            
            user_id = user_info.get("localId", "")
            token = user_info.get("idToken", "")
            
            print(f"✓ Firebase Authentication 회원가입 성공")
            print(f"  User ID: {user_id}")
            print(f"  Token 길이: {len(token) if token else 0}\n")
            
            if not user_id:
                raise Exception("Firebase Authentication에서 User ID를 가져올 수 없습니다.")
            
            if not token:
                raise Exception("Firebase Authentication에서 토큰을 가져올 수 없습니다.")
            
            # 토큰 새로고침 (회원가입 직후 토큰이 불안정할 수 있음)
            try:
                import time
                time.sleep(0.5)  # 0.5초 대기
                refreshed_user = self.auth.refresh(user_info.get("refreshToken", ""))
                if refreshed_user and refreshed_user.get("idToken"):
                    token = refreshed_user.get("idToken")
                    print(f"✓ 토큰 새로고침 완료")
            except Exception as refresh_error:
                print(f"⚠ 토큰 새로고침 실패 (기존 토큰 사용): {str(refresh_error)}")
            
            # 사용자 정보 준비 (Firestore에 저장할 데이터)
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
                "login_history": {}
            }
            
            print(f"[회원가입] 저장할 데이터:")
            print(f"  {json.dumps(user_data, ensure_ascii=False, indent=2)}\n")
            
            # Firestore Database에 사용자 정보 저장 (users 컬렉션에 저장)
            saved_to_db = False
            save_errors = []
            
            # config.json에서 projectId 가져오기
            from src.firebase_config import get_firebase
            firebase_config = get_firebase()
            project_id = firebase_config.config.get("projectId", "blog-cdc9b")
            
            # Firestore REST API로 저장 시도
            try:
                import requests
                # Firestore REST API URL
                doc_id = user_id
                firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users/{doc_id}"
                
                print(f"🔍 [회원가입] Firestore 저장 시도")
                print(f"   Project ID: {project_id}")
                print(f"   Firestore URL: {firestore_url}")
                print(f"   Document ID (user_id): {doc_id}")
                print(f"   Email: {email}")
                print(f"   Name: {name}")
                print(f"   Username: {username}")
                print(f"   Phone: {phone}\n")
                
                # 현재 시간 (ISO 8601 형식)
                now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                
                # Firestore 문서 형식으로 데이터 변환
                firestore_doc = {
                    "fields": {
                        "user_id": {"stringValue": user_id},
                        "name": {"stringValue": name},
                        "username": {"stringValue": username},
                        "email": {"stringValue": email},
                        "phone": {"stringValue": phone},
                        "approved": {"booleanValue": False},
                        "is_admin": {"booleanValue": False},
                        "created_at": {"timestampValue": now_iso},
                        "first_login_date": {"nullValue": None},
                        "expiry_date": {"nullValue": None},
                        "last_payment_date": {"nullValue": None},
                        "payment_pending": {"booleanValue": False},
                        "login_history": {"mapValue": {"fields": {}}}
                    }
                }
                
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                # PATCH 메서드로 문서 생성/업데이트
                print(f"   저장할 Firestore 문서:")
                print(f"   {json.dumps(firestore_doc, indent=2, ensure_ascii=False)[:500]}\n")
                print(f"   Authorization 헤더: Bearer {token[:20]}...{token[-10:] if len(token) > 30 else ''}\n")
                
                # 먼저 POST로 시도 (문서가 없으면 생성)
                response = None
                try:
                    # POST로 새 문서 생성 시도
                    post_response = requests.post(
                        f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users",
                        json=firestore_doc,
                        headers=headers,
                        params={"documentId": doc_id},
                        timeout=10
                    )
                    print(f"   POST 시도: HTTP {post_response.status_code}")
                    if post_response.status_code in [200, 201]:
                        response = post_response
                        print(f"✓ POST로 문서 생성 성공")
                    else:
                        print(f"   POST 실패, PATCH 시도: {post_response.text[:200]}")
                except Exception as post_error:
                    print(f"   POST 실패, PATCH 시도: {str(post_error)}")
                
                # POST가 실패하면 PATCH 시도
                if not response or response.status_code not in [200, 201]:
                    response = requests.patch(firestore_url, json=firestore_doc, headers=headers, timeout=10)
                    print(f"   PATCH 시도: HTTP {response.status_code}")
                
                print(f"   최종 HTTP 응답 코드: {response.status_code}")
                print(f"   응답 내용: {response.text[:1000]}\n")
                
                if response.status_code in [200, 201]:
                    print(f"✓ Firestore PATCH 요청 성공 (HTTP {response.status_code})")
                    
                    # 저장 확인 (최대 3번 재시도)
                    max_retries = 3
                    for retry in range(max_retries):
                        import time
                        if retry > 0:
                            time.sleep(0.5)  # 0.5초 대기
                        
                        verify_response = requests.get(firestore_url, headers=headers, timeout=5)
                        print(f"   저장 확인 시도 {retry + 1}/{max_retries}: HTTP {verify_response.status_code}")
                        
                        if verify_response.status_code == 200:
                            saved_doc = verify_response.json()
                            if saved_doc and "fields" in saved_doc:
                                saved_email = saved_doc["fields"].get("email", {}).get("stringValue", "")
                                if saved_email == email:
                                    print(f"✓ 저장 확인 성공!")
                                    print(f"   저장된 이메일: {saved_email}")
                                    print(f"   저장된 이름: {saved_doc['fields'].get('name', {}).get('stringValue', 'N/A')}")
                                    print(f"   저장된 사용자명: {saved_doc['fields'].get('username', {}).get('stringValue', 'N/A')}")
                                    print(f"   저장된 전화번호: {saved_doc['fields'].get('phone', {}).get('stringValue', 'N/A')}")
                                    print(f"   승인 상태: {saved_doc['fields'].get('approved', {}).get('booleanValue', False)}")
                                    saved_to_db = True
                                    break
                                else:
                                    print(f"⚠ 저장 확인: 이메일 불일치")
                                    print(f"   예상: {email}")
                                    print(f"   실제: {saved_email}")
                            else:
                                print(f"⚠ 저장 확인: 문서 구조가 올바르지 않음")
                                print(f"   응답: {json.dumps(saved_doc, indent=2, ensure_ascii=False)[:500]}")
                        elif verify_response.status_code == 401:
                            print(f"⚠ 저장 확인 실패: 인증 토큰 만료 (HTTP 401)")
                            break
                        elif verify_response.status_code == 403:
                            print(f"⚠ 저장 확인 실패: 권한 없음 (HTTP 403)")
                            print(f"   Firestore 규칙을 확인하세요.")
                            break
                        else:
                            print(f"⚠ 저장 확인 실패: HTTP {verify_response.status_code} (재시도 중...)")
                            print(f"   응답: {verify_response.text[:300]}")
                    
                    if not saved_to_db:
                        print(f"❌ 저장 확인 실패: {max_retries}번 시도 후에도 데이터를 확인할 수 없습니다.")
                else:
                    error_msg = f"Firestore REST API HTTP {response.status_code}: {response.text[:500]}"
                    print(f"❌ Firestore 저장 실패: {error_msg}")
                    if response.status_code == 401:
                        print(f"⚠ 인증 토큰이 만료되었거나 유효하지 않습니다.")
                    elif response.status_code == 403:
                        print(f"⚠ Firestore 보안 규칙 문제입니다.")
                        print(f"   Firebase Console > Firestore Database > 규칙 탭에서 확인하세요.")
                        print(f"   개발 단계에서는 다음 규칙을 사용하세요:")
                        print(f"   rules_version = '2';")
                        print(f"   service cloud.firestore {")
                        print(f"     match /databases/{database}/documents {")
                        print(f"       match /{{document=**}} {")
                        print(f"         allow read, write: if request.auth != null;")
                        print(f"       }}")
                        print(f"     }}")
                        print(f"   }}")
                    save_errors.append(error_msg)
            except Exception as rest_error:
                import traceback
                error_msg = f"Firestore REST API: {str(rest_error)}"
                print(f"❌ Firestore 저장 실패: {error_msg}")
                traceback.print_exc()
                save_errors.append(error_msg)
            
            # 저장 실패 시 경고만 출력 (회원가입은 성공으로 처리)
            if not saved_to_db:
                error_summary = "\n   ".join(save_errors)
                warning_message = (
                    f"\n{'='*60}\n"
                    f"⚠ 경고: Firestore에 저장하지 못했습니다.\n"
                    f"   관리자 페이지에서 승인할 때 자동으로 저장됩니다.\n"
                    f"{'='*60}\n"
                    f"시도한 방법들:\n   {error_summary}\n\n"
                    f"Firebase Console에서 다음을 확인해주세요:\n"
                    f"1. Firestore Database가 활성화되어 있는지\n"
                    f"2. Firestore 규칙이 올바르게 설정되어 있는지\n"
                    f"3. 규칙을 '게시' 버튼을 눌러 저장했는지\n"
                    f"{'='*60}\n"
                )
                print(warning_message)
                # 예외를 발생시키지 않고 계속 진행
                print(f"⚠ 회원가입은 성공했지만 Firestore 저장은 실패했습니다.")
                print(f"   관리자 페이지에서 승인할 때 자동으로 저장됩니다.\n")
            else:
                print(f"\n{'='*60}")
                print(f"✓ 회원가입 완료!")
                print(f"   User ID: {user_id}")
                print(f"   Email: {email}")
                print(f"   Name: {name}")
                print(f"   Firestore Database에 저장되었습니다: users/{user_id}")
                print(f"{'='*60}\n")
            
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
        사용자 승인 상태 확인 (Firestore)
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            dict: 승인 상태 정보
        """
        try:
            # Firestore REST API로 승인 상태 확인
            import requests
            from src.firebase_config import get_firebase
            firebase_config = get_firebase()
            project_id = firebase_config.config.get("projectId", "blog-cdc9b")
            firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users/{user_id}"
            
            # 토큰이 없으면 기본값 반환
            if not self.token:
                return {
                    "approved": False,
                    "message": "인증 토큰이 없습니다."
                }
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(firestore_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                doc = response.json()
                if "fields" in doc:
                    approved = doc["fields"].get("approved", {}).get("booleanValue", False)
                    return {
                        "approved": approved,
                        "message": "관리자 승인 대기 중입니다." if not approved else "승인되었습니다."
                    }
            
            # 문서가 없거나 승인되지 않은 경우
            return {
                "approved": False,
                "message": "사용자 정보를 찾을 수 없습니다." if response.status_code == 404 else "승인 상태 확인 실패"
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
            
            # Firestore에서 사용자 정보 가져오기
            user_data = None
            try:
                import requests
                from src.firebase_config import get_firebase
                firebase_config = get_firebase()
                project_id = firebase_config.config.get("projectId", "blog-cdc9b")
                firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users/{user_id}"
                
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }
                
                response = requests.get(firestore_url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    doc = response.json()
                    if "fields" in doc:
                        fields = doc["fields"]
                        # Firestore 필드를 일반 딕셔너리로 변환
                        user_data = {
                            "user_id": fields.get("user_id", {}).get("stringValue", user_id),
                            "email": fields.get("email", {}).get("stringValue", email),
                            "name": fields.get("name", {}).get("stringValue", ""),
                            "username": fields.get("username", {}).get("stringValue", ""),
                            "phone": fields.get("phone", {}).get("stringValue", ""),
                            "approved": fields.get("approved", {}).get("booleanValue", False),
                            "is_admin": fields.get("is_admin", {}).get("booleanValue", False),
                            "created_at": fields.get("created_at", {}).get("timestampValue", "").replace("Z", "") if "timestampValue" in fields.get("created_at", {}) else "",
                            "expiry_date": fields.get("expiry_date", {}).get("timestampValue", "").replace("Z", "") if "timestampValue" in fields.get("expiry_date", {}) else None,
                            "approved_date": fields.get("approved_date", {}).get("timestampValue", "").replace("Z", "") if "timestampValue" in fields.get("approved_date", {}) else None,
                            "first_login_date": fields.get("first_login_date", {}).get("timestampValue", "").replace("Z", "") if "timestampValue" in fields.get("first_login_date", {}) else None,
                        }
                        print(f"✓ Firestore에서 사용자 정보 조회 성공")
            except Exception as get_error:
                print(f"⚠ Firestore 사용자 정보 조회 실패: {str(get_error)}")
            
            # 이용만료일 확인
            if user_data and user_data.get("expiry_date"):
                expiry_date_str = user_data.get("expiry_date")
                try:
                    # ISO 형식 날짜 파싱 (다양한 형식 지원)
                    if 'T' in expiry_date_str:
                        # ISO 형식: 2024-11-06T12:00:00 또는 2024-11-06T12:00:00Z
                        expiry_date_str = expiry_date_str.replace('Z', '+00:00')
                        if '+' in expiry_date_str or expiry_date_str.endswith('+00:00'):
                            expiry_date = datetime.fromisoformat(expiry_date_str)
                            # 시간대 정보 제거 (날짜만 비교)
                            expiry_date = expiry_date.replace(tzinfo=None)
                        else:
                            expiry_date = datetime.fromisoformat(expiry_date_str)
                    else:
                        # 날짜만 있는 형식: 2024-11-06
                        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d')
                    
                    # 현재 날짜와 비교 (시간 제외, 날짜만)
                    current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    expiry_date_only = expiry_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    
                    if expiry_date_only < current_date:
                        raise Exception("EXPIRY_DATE_EXPIRED")
                except (ValueError, AttributeError) as e:
                    # 날짜 형식 오류는 무시하고 계속 진행
                    print(f"⚠ 이용만료일 파싱 오류 (무시됨): {str(e)}")
                    pass
            
            # 첫 로그인인지 확인하고 날짜 기록
            if user_data and not user_data.get("first_login_date"):
                first_login_date = datetime.now().isoformat()
                
                # 업데이트할 데이터
                update_data = {
                    "first_login_date": first_login_date
                }
                
                # 만료일이 없고 승인일이 있는 경우, 승인일 기준으로 30일 후 계산
                if not user_data.get("expiry_date"):
                    if user_data.get("approved_date"):
                        # 승인일 기준으로 30일 후
                        try:
                            approved_date_str = user_data.get("approved_date")
                            if 'T' in approved_date_str:
                                approved_date = datetime.fromisoformat(approved_date_str.replace('Z', '+00:00').replace('+00:00', ''))
                            else:
                                approved_date = datetime.strptime(approved_date_str, '%Y-%m-%d')
                            expiry_date = (approved_date + timedelta(days=30)).isoformat()
                        except:
                            # 승인일 파싱 실패 시 오늘 기준으로 30일 후
                            expiry_date = (datetime.now() + timedelta(days=30)).isoformat()
                    else:
                        # 승인일도 없으면 오늘 기준으로 30일 후
                        expiry_date = (datetime.now() + timedelta(days=30)).isoformat()
                    
                    update_data["expiry_date"] = expiry_date
                
                # Firestore에 업데이트
                try:
                    import requests
                    from src.firebase_config import get_firebase
                    firebase_config = get_firebase()
                    project_id = firebase_config.config.get("projectId", "blog-cdc9b")
                    firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users/{user_id}"
                    
                    headers = {
                        "Authorization": f"Bearer {self.token}",
                        "Content-Type": "application/json"
                    }
                    
                    # Firestore 형식으로 변환
                    firestore_update = {
                        "fields": {
                            "first_login_date": {"timestampValue": first_login_date + "Z"} if first_login_date else {"nullValue": None}
                        }
                    }
                    if "expiry_date" in update_data:
                        firestore_update["fields"]["expiry_date"] = {"timestampValue": update_data["expiry_date"] + "Z"}
                    
                    # 기존 문서 가져오기
                    get_response = requests.get(firestore_url, headers=headers, timeout=5)
                    if get_response.status_code == 200:
                        existing_doc = get_response.json()
                        if "fields" in existing_doc:
                            # 기존 필드와 병합
                            merged_fields = {**existing_doc["fields"], **firestore_update["fields"]}
                            firestore_update["fields"] = merged_fields
                    
                    # PATCH로 업데이트
                    patch_response = requests.patch(firestore_url, json=firestore_update, headers=headers, timeout=10)
                    if patch_response.status_code in [200, 201]:
                        print(f"✓ Firestore에 첫 로그인 정보 업데이트 성공")
                    else:
                        print(f"⚠ Firestore 업데이트 실패: {patch_response.status_code}")
                except Exception as update_error:
                    print(f"⚠ Firestore 업데이트 실패: {str(update_error)}")
            
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
            import requests
            from src.firebase_config import get_firebase
            firebase_config = get_firebase()
            project_id = firebase_config.config.get("projectId", "blog-cdc9b")
            firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users/{user_id}"
            
            if not self.token:
                return
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            # 기존 문서 가져오기
            get_response = requests.get(firestore_url, headers=headers, timeout=5)
            existing_doc = get_response.json() if get_response.status_code == 200 else None
            
            # 로그인 기록 추가
            now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            login_entry_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
            
            # 기존 login_history 가져오기
            login_history = {}
            if existing_doc and "fields" in existing_doc:
                login_history_field = existing_doc["fields"].get("login_history", {})
                if "mapValue" in login_history_field and "fields" in login_history_field["mapValue"]:
                    login_history = login_history_field["mapValue"]["fields"]
            
            # 새 로그인 기록 추가
            login_history[login_entry_id] = {
                "mapValue": {
                    "fields": {
                        "email": {"stringValue": email},
                        "timestamp": {"timestampValue": now_iso},
                        "user_id": {"stringValue": user_id}
                    }
                }
            }
            
            # 업데이트할 필드
            update_fields = {
                "last_login": {"timestampValue": now_iso},
                "email": {"stringValue": email},
                "login_history": {"mapValue": {"fields": login_history}}
            }
            
            # 기존 필드와 병합
            if existing_doc and "fields" in existing_doc:
                merged_fields = {**existing_doc["fields"], **update_fields}
            else:
                merged_fields = update_fields
            
            firestore_doc = {
                "fields": merged_fields
            }
            
            # PATCH로 업데이트
            patch_response = requests.patch(firestore_url, json=firestore_doc, headers=headers, timeout=10)
            if patch_response.status_code in [200, 201]:
                print(f"✓ Firestore에 로그인 기록 저장 성공")
            else:
                print(f"⚠ 로그인 기록 저장 실패: {patch_response.status_code}")
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
            
            # Firestore에 작업 로그 저장
            try:
                import requests
                from src.firebase_config import get_firebase
                firebase_config = get_firebase()
                project_id = firebase_config.config.get("projectId", "blog-cdc9b")
                firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/tasks"
                
                if not self.token:
                    return
                
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }
                
                # Firestore 형식으로 변환
                now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                firestore_doc = {
                    "fields": {
                        "task_type": {"stringValue": task_type},
                        "success": {"booleanValue": success},
                        "timestamp": {"timestampValue": now_iso},
                        "user_id": {"stringValue": user_id}
                    }
                }
                
                if target_url:
                    firestore_doc["fields"]["target_url"] = {"stringValue": target_url}
                if error_message:
                    firestore_doc["fields"]["error_message"] = {"stringValue": error_message}
                
                # POST로 새 문서 생성
                response = requests.post(
                    firestore_url,
                    json=firestore_doc,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    print(f"✓ Firestore에 작업 로그 저장 성공")
                else:
                    print(f"⚠ 작업 로그 저장 실패: {response.status_code}")
            except Exception as firestore_error:
                print(f"⚠ Firestore 작업 로그 저장 실패: {str(firestore_error)}")
        
        except Exception as e:
            print(f"작업 로그 저장 실패: {str(e)}")
