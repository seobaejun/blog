"""
관리자 페이지 Flask 애플리케이션
"""
import sys
import os
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from datetime import datetime, timedelta
import json

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.firebase_config import get_auth, get_db
from src.auth_manager import AuthManager

# Flask 앱 초기화 (static 폴더 명시적 지정)
static_folder = Path(__file__).parent / 'static'
app = Flask(__name__, static_folder=str(static_folder), static_url_path='/static')
# SECRET_KEY를 환경 변수에서 읽거나 기본값 사용
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this-in-production')

# Firebase 인스턴스 (에러 발생 시에도 앱 로드 가능하도록 try-except 사용)
try:
    auth_manager = AuthManager()
    db = get_db()
    auth = get_auth()
except Exception as e:
    # Firebase 초기화 실패해도 앱은 로드됨 (실제 사용 시점에 에러 발생)
    print(f"⚠ Firebase 초기화 실패 (앱은 계속 로드됨): {str(e)}")
    import traceback
    traceback.print_exc()
    # 더미 객체로 설정 (실제 사용 시 에러 발생)
    auth_manager = None
    db = None
    auth = None


def check_admin():
    """관리자 권한 확인"""
    if 'user_id' not in session:
        return False
    
    # 관리자 이메일로 직접 확인 (데이터베이스 없이도 작동)
    ADMIN_EMAIL = "sprince1004@naver.com"
    if 'email' in session and session.get('email') == ADMIN_EMAIL:
        return True
    
    try:
        # Firestore에서 관리자 정보 확인
        import requests
        project_id = "blog-cdc9b"
        user_id = session.get('user_id')
        id_token = session.get('token')
        
        if not id_token:
            return False
        
        firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users/{user_id}"
        headers = {
            "Authorization": f"Bearer {id_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(firestore_url, headers=headers, timeout=5)
        if response.status_code == 200:
            firestore_doc = response.json()
            if "fields" in firestore_doc:
                is_admin = firestore_doc["fields"].get("is_admin", {}).get("booleanValue", False)
                if is_admin:
                    return True
    except Exception as e:
        # Firestore 오류는 무시 (세션 기반으로 작동)
        pass
    
    return False


@app.route('/favicon.ico')
def favicon():
    """favicon.ico 요청 처리 (404 반환)"""
    from flask import abort
    abort(404)


@app.route('/')
def index():
    """메인 페이지 리다이렉트"""
    if check_admin():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """관리자 로그인"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        print(f"🔐 로그인 시도: email={email}")
        
        if not email or not password:
            flash('이메일과 비밀번호를 입력해주세요.', 'error')
            return render_template('login.html')
        
        # Firebase 인스턴스 확인 및 재초기화
        global auth_manager, db, auth
        
        if auth is None or db is None:
            flash('Firebase가 초기화되지 않았습니다. 서버 설정을 확인해주세요.', 'error')
            print("⚠ Firebase 인스턴스가 None입니다. 초기화를 다시 시도합니다.")
            try:
                # 재초기화 시도
                auth_manager = AuthManager()
                db = get_db()
                auth = get_auth()
                print("✓ Firebase 재초기화 성공")
            except Exception as init_error:
                import traceback
                print(f"✗ Firebase 재초기화 실패: {init_error}")
                traceback.print_exc()
                flash(f'Firebase 초기화 오류: {str(init_error)}', 'error')
            return render_template('login.html')
        
        try:
            # Firebase Authentication 로그인
            print(f"🔍 Firebase 인증 시도 중...")
            user_info = auth.sign_in_with_email_and_password(email, password)
            print(f"✓ Firebase 인증 성공: user_id={user_info.get('localId', 'N/A')}")
            user_id = user_info.get("localId", "")
            id_token = user_info.get("idToken", "")
            
            # 관리자 권한 확인 및 데이터베이스 정보 저장
            user_data = None
            
            # 1. Firestore에서 먼저 조회 시도
            try:
                import requests
                project_id = "blog-cdc9b"
                firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users/{user_id}"
                headers = {
                    "Authorization": f"Bearer {id_token}",
                    "Content-Type": "application/json"
                }
                response = requests.get(firestore_url, headers=headers, timeout=5)
                if response.status_code == 200:
                    firestore_doc = response.json()
                    if "fields" in firestore_doc:
                        fields = firestore_doc["fields"]
                        user_data = {
                            "user_id": user_id,
                            "email": fields.get("email", {}).get("stringValue", email),
                            "name": fields.get("name", {}).get("stringValue", "관리자"),
                            "approved": fields.get("approved", {}).get("booleanValue", False),
                            "is_admin": fields.get("is_admin", {}).get("booleanValue", False),
                            "created_at": fields.get("created_at", {}).get("timestampValue", ""),
                            "last_login": datetime.now().isoformat()
                        }
                        print(f"✓ Firestore에서 사용자 정보 조회 성공")
            except Exception as firestore_error:
                print(f"⚠ Firestore 조회 실패: {str(firestore_error)}")
            
            # Firestore에서 사용자 정보를 못 가져왔으면 기본 정보 생성
            if not user_data:
                print(f"⚠ Firestore에 사용자 정보가 없습니다. 기본 정보를 생성합니다.")
            
            # 관리자 정보 준비
            admin_info = {
                "user_id": user_id,
                "email": email,
                "name": "관리자",
                "approved": True,
                "is_admin": True,
                "created_at": datetime.now().isoformat(),
                "last_login": datetime.now().isoformat()
            }
            
            # 관리자 이메일 확인
            ADMIN_EMAIL = "sprince1004@naver.com"
            is_admin_email = (email == ADMIN_EMAIL)
            
            # 사용자 정보가 없으면 생성, 있으면 업데이트
            if not user_data:
                # 새로 생성
                user_data = admin_info.copy() if is_admin_email else {
                    "user_id": user_id,
                    "email": email,
                    "name": user_info.get("displayName", ""),
                    "approved": False,
                    "is_admin": False,
                    "created_at": datetime.now().isoformat(),
                    "last_login": datetime.now().isoformat()
                }
            else:
                # 관리자 이메일이면 관리자 권한 부여
                if is_admin_email:
                    user_data["is_admin"] = True
                    user_data["approved"] = True
                user_data["last_login"] = datetime.now().isoformat()
            
            # Firestore에 사용자 정보 저장
            saved_to_db = False
            try:
                import requests
                project_id = "blog-cdc9b"
                firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users/{user_id}"
                
                # Firestore 문서 형식으로 변환
                now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                firestore_doc = {
                    "fields": {
                        "user_id": {"stringValue": user_id},
                        "email": {"stringValue": user_data.get("email", email)},
                        "name": {"stringValue": user_data.get("name", "관리자")},
                        "approved": {"booleanValue": user_data.get("approved", is_admin_email)},
                        "is_admin": {"booleanValue": user_data.get("is_admin", is_admin_email)},
                        "created_at": {"timestampValue": user_data.get("created_at", now_iso) if isinstance(user_data.get("created_at"), str) and "T" in user_data.get("created_at", "") else now_iso},
                        "last_login": {"timestampValue": now_iso}
                    }
                }
                
                headers = {
                    "Authorization": f"Bearer {id_token}",
                    "Content-Type": "application/json"
                }
                
                print(f"🔍 Firestore에 사용자 정보 저장 시도")
                response = requests.patch(firestore_url, json=firestore_doc, headers=headers, timeout=10)
                print(f"   HTTP 응답 코드: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    print(f"✓ Firestore에 사용자 정보 저장 성공")
                    saved_to_db = True
                else:
                    print(f"⚠ Firestore 저장 실패: HTTP {response.status_code}")
                    print(f"   응답: {response.text[:300]}")
            except Exception as firestore_save_error:
                print(f"⚠ Firestore 저장 실패: {str(firestore_save_error)}")
            
            if not saved_to_db:
                print(f"⚠ Firestore 저장 실패했지만 로그인은 계속 진행합니다...")
            
            # 관리자 권한 확인
            if not user_data.get("is_admin", False):
                flash('관리자 권한이 없습니다.', 'error')
                return render_template('login.html')
            
            # 세션에 저장
            session['user_id'] = user_id
            session['email'] = email
            session['name'] = user_data.get("name", "관리자")
            session['token'] = id_token  # 토큰도 세션에 저장
            
            return redirect(url_for('dashboard'))
        
        except Exception as e:
            import traceback
            import json
            error_message = str(e)
            print(f"❌ 로그인 오류 발생: {error_message}")
            traceback.print_exc()
            
            # Firebase 인증 오류 메시지 추출 (JSON 응답에서)
            firebase_error_code = None
            try:
                if "{" in error_message and "}" in error_message:
                    # JSON 응답에서 오류 코드 추출 시도
                    json_start = error_message.find("{")
                    json_end = error_message.rfind("}") + 1
                    if json_start >= 0 and json_end > json_start:
                        error_json = json.loads(error_message[json_start:json_end])
                        if "error" in error_json and "message" in error_json["error"]:
                            firebase_error_code = error_json["error"]["message"]
            except:
                pass
            
            # Firebase 인증 오류 메시지 확인
            if firebase_error_code:
                if "INVALID_PASSWORD" in firebase_error_code or "EMAIL_NOT_FOUND" in firebase_error_code or "INVALID_LOGIN_CREDENTIALS" in firebase_error_code:
                    flash('로그인에 실패했습니다. 이메일과 비밀번호를 확인해주세요.', 'error')
                elif "INVALID_EMAIL" in firebase_error_code:
                    flash('올바른 이메일 형식이 아닙니다.', 'error')
                else:
                    flash(f'로그인 오류: {firebase_error_code}', 'error')
            elif "INVALID_PASSWORD" in error_message or "EMAIL_NOT_FOUND" in error_message or "INVALID_LOGIN_CREDENTIALS" in error_message:
                flash('로그인에 실패했습니다. 이메일과 비밀번호를 확인해주세요.', 'error')
            elif "INVALID_EMAIL" in error_message:
                flash('올바른 이메일 형식이 아닙니다.', 'error')
            else:
                flash('로그인 중 오류가 발생했습니다. 이메일과 비밀번호를 확인해주세요.', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """로그아웃"""
    session.clear()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    """대시보드"""
    if not check_admin():
        flash('로그인이 필요합니다.', 'error')
        return redirect(url_for('login'))
    
    try:
        # 통계 데이터 수집 (Firestore에서 조회)
        total_users = 0
        pending_approvals = 0
        try:
            import requests
            project_id = "blog-cdc9b"
            firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users"
            
            id_token = session.get('token')
            if id_token:
                headers = {
                    "Authorization": f"Bearer {id_token}",
                    "Content-Type": "application/json"
                }
                response = requests.get(firestore_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    firestore_data = response.json()
                    documents = firestore_data.get("documents", [])
                    total_users = len(documents)
                    pending_approvals = sum(1 for doc in documents 
                                          if not doc.get("fields", {}).get("approved", {}).get("booleanValue", False))
        except Exception as db_error:
            # 데이터베이스가 없어도 빈 통계로 표시
            print(f"⚠ Firestore 조회 실패 (빈 통계 표시): {str(db_error)[:100]}")
        
        # 결제 대기 및 만료 예정 사용자 계산
        pending_payments = 0
        expiring_soon = 0
        try:
            if id_token:
                headers = {
                    "Authorization": f"Bearer {id_token}",
                    "Content-Type": "application/json"
                }
                response = requests.get(firestore_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    firestore_data = response.json()
                    documents = firestore_data.get("documents", [])
                    pending_payments = sum(1 for doc in documents 
                                          if doc.get("fields", {}).get("payment_pending", {}).get("booleanValue", False))
                    
                    # 만료 예정 사용자 (7일 이내)
                    today = datetime.now()
                    for doc in documents:
                        expiry_field = doc.get("fields", {}).get("expiry_date", {})
                        if "timestampValue" in expiry_field:
                            expiry_str = expiry_field["timestampValue"].replace("Z", "")
                            try:
                                expiry_date = datetime.fromisoformat(expiry_str)
                                days_left = (expiry_date.replace(tzinfo=None) - today.replace(tzinfo=None)).days
                                if 0 <= days_left <= 7:
                                    expiring_soon += 1
                            except:
                                pass
        except:
            pass
        
        stats = {
            'total_users': total_users,
            'pending_approvals': pending_approvals,
            'pending_payments': pending_payments,
            'expiring_soon': expiring_soon
        }
        
        return render_template('dashboard.html', stats=stats)
    
    except Exception as e:
        # 오류 발생 시 빈 통계로 표시
        flash(f'대시보드 데이터를 불러오는 중 오류가 발생했습니다. (데이터베이스가 활성화되지 않았을 수 있습니다)', 'warning')
        return render_template('dashboard.html', stats={
            'total_users': 0,
            'pending_approvals': 0,
            'pending_payments': 0,
            'expiring_soon': 0
        })


@app.route('/users')
def users():
    """회원 목록 (Firestore에서 조회)"""
    if not check_admin():
        flash('로그인이 필요합니다.', 'error')
        return redirect(url_for('login'))
    
    print(f"\n{'='*60}")
    print(f"[회원 목록 조회] 시작")
    print(f"   세션 정보: user_id={session.get('user_id')}, email={session.get('email')}")
    print(f"   토큰 존재: {bool(session.get('token'))}")
    print(f"{'='*60}\n")
    
    try:
        users_list = []
        
        # Firestore에서 사용자 목록 조회
        try:
            import requests
            project_id = "blog-cdc9b"
            firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users"
            
            # 세션에서 토큰 가져오기
            id_token = session.get('token')
            if not id_token:
                print("⚠ 세션에 토큰이 없습니다.")
                print(f"   세션 키: {list(session.keys())}")
                flash('로그인이 필요합니다. 다시 로그인해주세요.', 'error')
                return redirect(url_for('login'))
            
            print(f"✓ 세션에서 토큰 확인: {id_token[:20]}...")
            
            headers = {
                "Authorization": f"Bearer {id_token}",
                "Content-Type": "application/json"
            }
            
            print(f"🔍 Firestore에서 사용자 목록 조회 시도")
            print(f"   Project ID: {project_id}")
            print(f"   URL: {firestore_url}")
            print(f"   토큰 길이: {len(id_token)}")
            
            response = requests.get(firestore_url, headers=headers, timeout=10)
            print(f"   HTTP 응답 코드: {response.status_code}")
            print(f"   응답 헤더: {dict(response.headers)}")
            print(f"   응답 본문 (처음 500자): {response.text[:500]}")
            
            if response.status_code == 200:
                try:
                    firestore_data = response.json()
                    documents = firestore_data.get("documents", [])
                    print(f"✓ Firestore에서 {len(documents)}명의 사용자 조회 성공")
                    
                    if len(documents) == 0:
                        print("⚠ Firestore에 문서가 없습니다. 회원가입한 사용자가 없거나 Firestore에 저장되지 않았을 수 있습니다.")
                except Exception as json_error:
                    print(f"❌ JSON 파싱 실패: {str(json_error)}")
                    print(f"   응답 본문: {response.text}")
                    documents = []
                
                # Firestore 문서를 일반 딕셔너리로 변환
                for doc in documents:
                    doc_name = doc.get("name", "")
                    # 문서 이름에서 user_id 추출: projects/.../documents/users/{user_id}
                    user_id = doc_name.split("/")[-1] if "/" in doc_name else ""
                    
                    fields = doc.get("fields", {})
                    
                    # Firestore 필드를 일반 값으로 변환하는 헬퍼 함수
                    def get_string_value(field_name, default=""):
                        field = fields.get(field_name, {})
                        if "stringValue" in field:
                            return field["stringValue"]
                        return default
                    
                    def get_bool_value(field_name, default=False):
                        field = fields.get(field_name, {})
                        if "booleanValue" in field:
                            return field["booleanValue"]
                        return default
                    
                    def get_timestamp_value(field_name, default=None):
                        field = fields.get(field_name, {})
                        if "nullValue" in field:
                            return None
                        if "timestampValue" in field:
                            # Firestore timestamp 형식: "2025-11-06T18:07:10.205453Z"
                            timestamp = field["timestampValue"]
                            # ISO 형식으로 변환 (템플릿에서 사용하기 쉽게)
                            return timestamp.replace("Z", "") if timestamp else None
                        return default
                    
                    # Firestore 필드를 일반 값으로 변환
                    user_data = {
                        "user_id": user_id,
                        "name": get_string_value("name", ""),
                        "username": get_string_value("username", ""),
                        "email": get_string_value("email", ""),
                        "phone": get_string_value("phone", ""),
                        "approved": get_bool_value("approved", False),
                        "is_admin": get_bool_value("is_admin", False),
                        "created_at": get_timestamp_value("created_at", ""),
                        "expiry_date": get_timestamp_value("expiry_date"),
                        "first_login_date": get_timestamp_value("first_login_date"),
                        "approved_date": get_timestamp_value("approved_date"),
                    }
                    
                    users_list.append(user_data)
                    print(f"  Firestore 사용자 추가: {user_data.get('email')} - 승인: {user_data.get('approved')}")
                
                print(f"✓ {len(documents)}명의 Firestore 사용자 데이터 변환 완료")
            else:
                error_msg = f"Firestore 조회 실패: HTTP {response.status_code}"
                print(f"❌ {error_msg}")
                print(f"   응답 전체: {response.text}")
                if response.status_code == 401:
                    print("⚠ 인증 토큰이 만료되었거나 유효하지 않습니다. 다시 로그인해주세요.")
                    flash('Firestore 인증 토큰이 만료되었습니다. 다시 로그인해주세요.', 'error')
                    session.clear()
                    return redirect(url_for('login'))
                elif response.status_code == 403:
                    print("⚠ Firestore 접근 권한이 없습니다.")
                    print("   Firebase Console > Firestore Database > 규칙 탭에서 확인하세요.")
                    flash('Firestore 접근 권한이 없습니다. Firebase Console에서 규칙을 확인해주세요.', 'error')
                else:
                    print(f"⚠ Firestore 조회 실패: HTTP {response.status_code}")
                    flash(f'Firestore 조회 실패: HTTP {response.status_code}', 'error')
        except Exception as firestore_error:
            import traceback
            print(f"❌ Firestore 조회 실패: {str(firestore_error)}")
            traceback.print_exc()
            flash(f'Firestore에서 회원 목록을 불러오는 중 오류가 발생했습니다.', 'warning')
        
        print(f"✓ 총 {len(users_list)}명의 사용자 정보 수집 완료 (Firestore)")
        
        # Realtime Database에서도 사용자 목록 조회 (회원가입 시 Realtime Database에 저장되는 경우 대비)
        try:
            print(f"\n🔍 Realtime Database에서 사용자 목록 조회 시도")
            if db is not None:
                try:
                    users_rtdb = db.child("users").get()
                    if users_rtdb and users_rtdb.val():
                        rtdb_data = users_rtdb.val()
                        print(f"✓ Realtime Database에서 {len(rtdb_data)}명의 사용자 조회 성공")
                        
                        # 이미 추가된 user_id 목록 (중복 방지)
                        existing_user_ids = {user.get("user_id") for user in users_list}
                        
                        # Realtime Database 데이터를 users_list에 추가
                        for user_id, user_data in rtdb_data.items():
                            if user_id not in existing_user_ids:
                                # Realtime Database 형식을 일반 딕셔너리로 변환
                                user_info = {
                                    "user_id": user_id,
                                    "name": user_data.get("name", ""),
                                    "username": user_data.get("username", ""),
                                    "email": user_data.get("email", ""),
                                    "phone": user_data.get("phone", ""),
                                    "approved": user_data.get("approved", False),
                                    "is_admin": user_data.get("is_admin", False),
                                    "created_at": user_data.get("created_at", ""),
                                    "expiry_date": user_data.get("expiry_date"),
                                    "first_login_date": user_data.get("first_login_date"),
                                    "approved_date": user_data.get("approved_date"),
                                }
                                users_list.append(user_info)
                                print(f"  Realtime Database 사용자 추가: {user_info.get('email')} - 승인: {user_info.get('approved')}")
                            else:
                                # 이미 Firestore에 있는 경우, Realtime Database 데이터로 업데이트 (최신 정보)
                                # 단, approved 필드는 Firestore 값을 우선시 (Firestore가 더 정확한 승인 상태를 가지고 있음)
                                for idx, existing_user in enumerate(users_list):
                                    if existing_user.get("user_id") == user_id:
                                        # Firestore에서 가져온 approved 값 보존
                                        firestore_approved = existing_user.get("approved", False)
                                        rtdb_approved = user_data.get("approved", False)
                                        
                                        # Firestore에서 approved: true인데 Realtime Database에서 approved: false인 경우 동기화
                                        if firestore_approved and not rtdb_approved:
                                            print(f"  🔄 승인 상태 동기화 필요: {user_id} (Firestore=True, Realtime=False)")
                                            try:
                                                # Realtime Database에 승인 정보 동기화
                                                sync_data = user_data.copy()
                                                sync_data["approved"] = True
                                                sync_data["rejected"] = False
                                                
                                                # Firestore의 승인일과 만료일도 동기화
                                                if existing_user.get("approved_date"):
                                                    sync_data["approved_date"] = existing_user.get("approved_date")
                                                if existing_user.get("expiry_date"):
                                                    sync_data["expiry_date"] = existing_user.get("expiry_date")
                                                if existing_user.get("first_login_date"):
                                                    sync_data["first_login_date"] = existing_user.get("first_login_date")
                                                
                                                db.child("users").child(user_id).set(sync_data)
                                                print(f"  ✓ Realtime Database 승인 상태 동기화 완료: {user_id}")
                                                
                                                # users_list도 업데이트
                                                user_data = sync_data
                                            except Exception as sync_error:
                                                print(f"  ⚠ 동기화 실패: {str(sync_error)}")
                                        
                                        # Realtime Database 데이터로 업데이트 (빈 값이 아닌 경우만)
                                        if user_data.get("name"):
                                            users_list[idx]["name"] = user_data.get("name")
                                        if user_data.get("username"):
                                            users_list[idx]["username"] = user_data.get("username")
                                        if user_data.get("phone"):
                                            users_list[idx]["phone"] = user_data.get("phone")
                                        # approved는 Firestore 값을 유지 (Realtime Database 값으로 덮어쓰지 않음)
                                        # users_list[idx]["approved"]는 이미 Firestore 값으로 설정되어 있음
                                        if "is_admin" in user_data:
                                            users_list[idx]["is_admin"] = user_data.get("is_admin")
                                        if user_data.get("expiry_date"):
                                            users_list[idx]["expiry_date"] = user_data.get("expiry_date")
                                        print(f"  Realtime Database 데이터로 업데이트: {user_id} (승인 상태: Firestore={firestore_approved} 유지)")
                                        break
                    else:
                        print("⚠ Realtime Database에 사용자 데이터가 없습니다.")
                except Exception as rtdb_error:
                    print(f"⚠ Realtime Database 조회 실패: {str(rtdb_error)}")
            else:
                print("⚠ Realtime Database 인스턴스가 없습니다.")
        except Exception as rtdb_error:
            print(f"⚠ Realtime Database 조회 중 오류: {str(rtdb_error)}")
        
        print(f"✓ 총 {len(users_list)}명의 사용자 정보 수집 완료 (Firestore + Realtime Database)")
        
        # 승인 상태와 날짜로 정렬
        users_list.sort(key=lambda x: (
            not x.get("approved", False),
            x.get("created_at", "")
        ), reverse=True)
        
        # 오늘 날짜 전달
        today = datetime.now().isoformat()
        
        return render_template('users.html', users=users_list, today=today)
    
    except Exception as e:
        import traceback
        print(f"❌ 회원 목록 조회 중 오류: {str(e)}")
        traceback.print_exc()
        flash(f'회원 목록을 불러오는 중 오류가 발생했습니다.', 'warning')
        return render_template('users.html', users=[], today=datetime.now().isoformat())


# sync_users_to_database 함수는 더 이상 사용하지 않음 (Firestore만 사용)


@app.route('/users/approve/<user_id>', methods=['POST'])
def approve_user(user_id):
    """회원 승인 (Firestore에 저장)"""
    if not check_admin():
        return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403
    
    try:
        # 현재 날짜
        now = datetime.now()
        approved_date_iso = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        # 승인일로부터 30일 후 만료일 계산
        expiry_date_iso = (now + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        # Firestore에 저장
        try:
            import requests
            project_id = "blog-cdc9b"
            firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users/{user_id}"
            
            # 세션에서 토큰 가져오기
            id_token = session.get('token')
            if not id_token:
                return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
            
            headers = {
                "Authorization": f"Bearer {id_token}",
                "Content-Type": "application/json"
            }
            
            # 기존 사용자 정보 가져오기
            existing_doc = None
            try:
                get_response = requests.get(firestore_url, headers=headers, timeout=5)
                if get_response.status_code == 200:
                    existing_doc = get_response.json()
                    print(f"✓ 기존 사용자 정보 조회 성공")
            except Exception as get_error:
                print(f"⚠ 기존 사용자 정보 조회 실패: {str(get_error)}")
            
            # Firestore에 사용자 정보가 없는 경우, Firebase Authentication에서 기본 정보 가져오기
            if not existing_doc or "fields" not in existing_doc:
                print(f"⚠ Firestore에 사용자 정보가 없습니다. Firebase Authentication에서 기본 정보를 가져옵니다.")
                # Firebase Authentication REST API로 사용자 정보 가져오기
                try:
                    # Firebase Admin SDK 없이도 Firebase Authentication REST API를 사용할 수 있지만,
                    # 여기서는 기본값으로 사용자 정보를 생성합니다.
                    # 실제로는 Firebase Admin SDK가 필요하지만, 일단 기본 정보로 생성합니다.
                    print(f"   기본 사용자 정보로 Firestore 문서를 생성합니다.")
                except Exception as auth_error:
                    print(f"⚠ Firebase Authentication 정보 조회 실패: {str(auth_error)}")
            
            # 업데이트할 필드 준비
            update_fields = {
                "approved": {"booleanValue": True},
                "approved_date": {"timestampValue": approved_date_iso},
                "rejected": {"booleanValue": False}  # 승인 시 거부 상태 해제
            }
            
            # first_login_date가 없으면 현재 날짜로 설정 (승인 시 즉시 이용 가능하도록)
            if existing_doc and "fields" in existing_doc:
                existing_first_login = existing_doc["fields"].get("first_login_date", {})
                if "nullValue" in existing_first_login or "timestampValue" not in existing_first_login:
                    # first_login_date가 없으면 현재 날짜로 설정
                    update_fields["first_login_date"] = {"timestampValue": approved_date_iso}
            else:
                # 사용자 정보가 없는 경우 first_login_date 설정
                update_fields["first_login_date"] = {"timestampValue": approved_date_iso}
            
            # 만료일이 없거나 이미 설정된 만료일이 과거인 경우에만 새로 설정
            if existing_doc and "fields" in existing_doc:
                existing_expiry = existing_doc["fields"].get("expiry_date", {})
                if "nullValue" not in existing_expiry and "timestampValue" in existing_expiry:
                    # 기존 만료일이 있는 경우 확인
                    existing_expiry_str = existing_expiry["timestampValue"]
                    try:
                        existing_expiry_date = datetime.fromisoformat(existing_expiry_str.replace("Z", "+00:00").replace("+00:00", ""))
                        if existing_expiry_date.replace(tzinfo=None) < now:
                            # 만료일이 이미 지난 경우 새로 설정
                            update_fields["expiry_date"] = {"timestampValue": expiry_date_iso}
                    except:
                        # 날짜 파싱 실패 시 새로 설정
                        update_fields["expiry_date"] = {"timestampValue": expiry_date_iso}
                else:
                    # 만료일이 없는 경우 새로 설정
                    update_fields["expiry_date"] = {"timestampValue": expiry_date_iso}
            else:
                # 사용자 정보가 없는 경우 만료일 설정
                update_fields["expiry_date"] = {"timestampValue": expiry_date_iso}
            
            # Firestore 문서 업데이트 (기존 필드와 병합)
            if existing_doc and "fields" in existing_doc:
                # 기존 필드와 병합 (update_fields가 나중에 오므로 덮어씀)
                merged_fields = {**existing_doc["fields"], **update_fields}
                # rejected 필드가 명시적으로 False로 설정되도록 보장
                merged_fields["rejected"] = {"booleanValue": False}
            else:
                # Firestore에 사용자 정보가 없는 경우, 기본 필드 생성
                # user_id는 필수
                merged_fields = {
                    "user_id": {"stringValue": user_id},
                    "approved": update_fields["approved"],
                    "approved_date": update_fields["approved_date"],
                    "expiry_date": update_fields["expiry_date"],
                    "is_admin": {"booleanValue": False},
                    "created_at": {"timestampValue": now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")},
                    "first_login_date": update_fields.get("first_login_date", {"timestampValue": approved_date_iso}),
                    "last_payment_date": {"nullValue": None},
                    "payment_pending": {"booleanValue": False},
                    "login_history": {"mapValue": {"fields": {}}}
                }
                # 기존 필드가 있으면 병합
                if existing_doc and "fields" in existing_doc:
                    merged_fields = {**existing_doc["fields"], **merged_fields}
            
            firestore_doc = {
                "fields": merged_fields
            }
            
            # PATCH 메서드로 업데이트
            print(f"🔍 Firestore 승인 정보 저장 시도: user_id={user_id}")
            response = requests.patch(firestore_url, json=firestore_doc, headers=headers, timeout=10)
            print(f"   HTTP 응답 코드: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print(f"✓ Firestore에 승인 정보 저장 성공")
                
                # 저장된 데이터 확인 (디버깅용)
                try:
                    verify_response = requests.get(firestore_url, headers=headers, timeout=5)
                    if verify_response.status_code == 200:
                        verify_doc = verify_response.json()
                        if "fields" in verify_doc:
                            saved_approved = verify_doc["fields"].get("approved", {}).get("booleanValue", False)
                            saved_rejected = verify_doc["fields"].get("rejected", {}).get("booleanValue", True)
                            print(f"   저장 확인 - approved: {saved_approved}, rejected: {saved_rejected}")
                except Exception as verify_error:
                    print(f"⚠ 저장 확인 실패: {str(verify_error)}")
                
                # Realtime Database에도 승인 정보 저장 (클라이언트 프로그램 호환성)
                rtdb_success = False
                try:
                    if db is not None:
                        print(f"🔍 Realtime Database 승인 정보 저장 시도: user_id={user_id}")
                        # Realtime Database 형식으로 변환
                        rtdb_data = {
                            "approved": True,
                            "approved_date": approved_date_iso.replace("Z", ""),
                            "expiry_date": expiry_date_iso.replace("Z", ""),
                            "first_login_date": approved_date_iso.replace("Z", ""),
                            "rejected": False  # 승인 시 거부 상태 해제
                        }
                        
                        # 기존 데이터가 있으면 업데이트, 없으면 새로 생성
                        existing_user = db.child("users").child(user_id).get()
                        if existing_user and existing_user.val():
                            # 기존 데이터와 병합
                            existing_data = existing_user.val()
                            # approved와 rejected는 반드시 덮어쓰기
                            existing_data["approved"] = True
                            existing_data["rejected"] = False
                            # 나머지 필드 업데이트
                            existing_data.update({
                                "approved_date": rtdb_data["approved_date"],
                                "expiry_date": rtdb_data["expiry_date"],
                                "first_login_date": rtdb_data["first_login_date"]
                            })
                            db.child("users").child(user_id).set(existing_data)
                            print(f"✓ Realtime Database에 승인 정보 업데이트 성공")
                        else:
                            # 새로 생성
                            rtdb_data["user_id"] = user_id
                            db.child("users").child(user_id).set(rtdb_data)
                            print(f"✓ Realtime Database에 승인 정보 생성 성공")
                        
                        # 저장 확인 (잠시 대기 후 확인)
                        import time
                        time.sleep(0.5)  # Realtime Database 동기화 대기
                        verify_user = db.child("users").child(user_id).get()
                        if verify_user and verify_user.val():
                            verified_approved = verify_user.val().get("approved", False)
                            print(f"   저장 확인 - approved: {verified_approved}")
                            if not verified_approved:
                                print(f"   ⚠ 경고: Realtime Database에 approved가 False로 저장되었습니다!")
                                # 다시 시도
                                print(f"   재시도: approved를 True로 강제 설정")
                                retry_data = verify_user.val().copy()
                                retry_data["approved"] = True
                                retry_data["rejected"] = False
                                db.child("users").child(user_id).set(retry_data)
                                print(f"   재시도 완료")
                        
                        rtdb_success = True
                    else:
                        print("⚠ Realtime Database 인스턴스가 없습니다.")
                except Exception as rtdb_error:
                    print(f"⚠ Realtime Database 저장 실패: {str(rtdb_error)}")
                
                return jsonify({
                    'success': True, 
                    'message': f'회원이 승인되었습니다. (승인일: {approved_date_iso[:10]}, 만료일: {expiry_date_iso[:10]})'
                })
            else:
                error_msg = f"Firestore HTTP {response.status_code}: {response.text[:200]}"
                print(f"❌ {error_msg}")
                return jsonify({
                    'success': False, 
                    'message': f'Firestore 저장 실패: {error_msg[:100]}'
                }), 500
        except Exception as db_error:
            import traceback
            error_msg = str(db_error)
            print(f"❌ Firestore 저장 실패: {error_msg}")
            traceback.print_exc()
            return jsonify({
                'success': False, 
                'message': f'데이터베이스 저장 실패: {error_msg[:100]}. Firebase Console에서 규칙을 확인해주세요.'
            }), 500
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'}), 500


@app.route('/users/reject/<user_id>', methods=['POST'])
def reject_user(user_id):
    """회원 거부 (Firestore에서 rejected 상태로 업데이트)"""
    if not check_admin():
        return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403
    
    try:
        import requests
        project_id = "blog-cdc9b"
        firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users/{user_id}"
        
        id_token = session.get('token')
        if not id_token:
            return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
        
        headers = {
            "Authorization": f"Bearer {id_token}",
            "Content-Type": "application/json"
        }
        
        # 기존 사용자 정보 가져오기
        existing_doc = None
        try:
            get_response = requests.get(firestore_url, headers=headers, timeout=5)
            if get_response.status_code == 200:
                existing_doc = get_response.json()
        except Exception as get_error:
            print(f"⚠ 기존 사용자 정보 조회 실패: {str(get_error)}")
        
        # 거부 상태로 업데이트
        now = datetime.now()
        now_iso = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        update_fields = {
            "approved": {"booleanValue": False},
            "rejected": {"booleanValue": True},
            "rejected_date": {"timestampValue": now_iso}
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
        print(f"🔍 Firestore 거부 정보 저장 시도: user_id={user_id}")
        response = requests.patch(firestore_url, json=firestore_doc, headers=headers, timeout=10)
        print(f"   HTTP 응답 코드: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"✓ Firestore에 거부 정보 저장 성공")
            return jsonify({
                'success': True, 
                'message': '회원이 거부되었습니다.'
            })
        else:
            error_msg = f"Firestore HTTP {response.status_code}: {response.text[:200]}"
            print(f"❌ {error_msg}")
            return jsonify({
                'success': False, 
                'message': f'Firestore 저장 실패: {error_msg[:100]}'
            }), 500
    
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"❌ 회원 거부 실패: {error_msg}")
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'message': f'오류가 발생했습니다: {error_msg[:100]}'
        }), 500


@app.route('/users/delete/<user_id>', methods=['POST'])
def delete_user(user_id):
    """회원 삭제 (Firestore에서 문서 삭제)"""
    if not check_admin():
        return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403
    
    try:
        import requests
        project_id = "blog-cdc9b"
        firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users/{user_id}"
        
        id_token = session.get('token')
        if not id_token:
            return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
        
        headers = {
            "Authorization": f"Bearer {id_token}",
            "Content-Type": "application/json"
        }
        
        # Firestore에서 문서 삭제
        print(f"🔍 Firestore 사용자 삭제 시도: user_id={user_id}")
        response = requests.delete(firestore_url, headers=headers, timeout=10)
        print(f"   HTTP 응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✓ Firestore에서 사용자 삭제 성공")
            return jsonify({
                'success': True, 
                'message': '회원이 삭제되었습니다.'
            })
        elif response.status_code == 404:
            # 이미 삭제된 경우
            return jsonify({
                'success': True, 
                'message': '회원이 이미 삭제되었습니다.'
            })
        else:
            error_msg = f"Firestore HTTP {response.status_code}: {response.text[:200]}"
            print(f"❌ {error_msg}")
            return jsonify({
                'success': False, 
                'message': f'Firestore 삭제 실패: {error_msg[:100]}'
            }), 500
    
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"❌ 회원 삭제 실패: {error_msg}")
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'message': f'오류가 발생했습니다: {error_msg[:100]}'
        }), 500


@app.route('/users/update-expiry/<user_id>', methods=['POST'])
def update_expiry_date(user_id):
    """이용만료일 수정"""
    print(f"🔍 만료일 수정 요청: user_id={user_id}")
    
    if not check_admin():
        print("❌ 관리자 권한 없음")
        return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403
    
    try:
        data = request.get_json()
        print(f"📥 받은 데이터: {data}")
        expiry_date = data.get('expiry_date', '').strip()
        
        if not expiry_date:
            print("❌ 만료일이 없음")
            return jsonify({'success': False, 'message': '만료일을 입력해주세요.'}), 400
        
        # 날짜 형식 검증
        try:
            datetime.fromisoformat(expiry_date)
        except ValueError:
            # YYYY-MM-DD 형식인지 확인
            try:
                datetime.strptime(expiry_date, '%Y-%m-%d')
                # ISO 형식으로 변환 (시간 포함)
                expiry_date = f"{expiry_date}T23:59:59"
            except ValueError:
                return jsonify({'success': False, 'message': '올바른 날짜 형식이 아닙니다. (YYYY-MM-DD)'}), 400
        
        # Firestore에 만료일 업데이트
        try:
            import requests
            project_id = "blog-cdc9b"
            firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users/{user_id}"
            
            # 세션에서 토큰 가져오기
            id_token = session.get('token')
            if not id_token:
                return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
            
            headers = {
                "Authorization": f"Bearer {id_token}",
                "Content-Type": "application/json"
            }
            
            # 기존 사용자 정보 가져오기
            existing_doc = None
            try:
                get_response = requests.get(firestore_url, headers=headers, timeout=5)
                if get_response.status_code == 200:
                    existing_doc = get_response.json()
                    print(f"✓ 기존 사용자 정보 조회 성공")
            except Exception as get_error:
                print(f"⚠ 기존 사용자 정보 조회 실패: {str(get_error)}")
            
            # 만료일을 Firestore timestamp 형식으로 변환
            # expiry_date는 "YYYY-MM-DD" 또는 "YYYY-MM-DDTHH:MM:SS" 형식
            if 'T' in expiry_date:
                expiry_timestamp = expiry_date.replace("Z", "")
            else:
                # YYYY-MM-DD 형식인 경우 시간 추가
                expiry_timestamp = f"{expiry_date}T23:59:59"
            
            if not expiry_timestamp.endswith("Z"):
                expiry_timestamp = f"{expiry_timestamp}Z"
            
            # 업데이트할 필드
            update_fields = {
                "expiry_date": {"timestampValue": expiry_timestamp}
            }
            
            # 기존 필드와 병합
            if existing_doc and "fields" in existing_doc:
                merged_fields = {**existing_doc["fields"], **update_fields}
            else:
                merged_fields = update_fields
            
            firestore_doc = {
                "fields": merged_fields
            }
            
            # PATCH 메서드로 업데이트
            print(f"🔍 Firestore 만료일 저장 시도: user_id={user_id}, expiry_date={expiry_date}")
            response = requests.patch(firestore_url, json=firestore_doc, headers=headers, timeout=10)
            print(f"   HTTP 응답 코드: {response.status_code}")
            print(f"   응답 내용: {response.text[:300]}")
            
            firestore_success = False
            if response.status_code in [200, 201]:
                print(f"✓ Firestore에 만료일 저장 성공")
                firestore_success = True
            else:
                error_msg = f"Firestore HTTP {response.status_code}: {response.text[:200]}"
                print(f"⚠ {error_msg}")
            
            # Realtime Database에도 저장
            rtdb_success = False
            try:
                if db is not None:
                    print(f"🔍 Realtime Database 만료일 저장 시도: user_id={user_id}, expiry_date={expiry_date}")
                    # 기존 데이터를 먼저 가져와서 병합
                    existing_user = db.child("users").child(user_id).get()
                    if existing_user and existing_user.val():
                        # 기존 데이터와 병합
                        user_data = existing_user.val()
                        user_data["expiry_date"] = expiry_date
                        # 기존 데이터를 유지하면서 expiry_date만 업데이트
                        db.child("users").child(user_id).set(user_data)
                        print(f"✓ Realtime Database에 만료일 저장 성공 (기존 데이터 유지)")
                    else:
                        # 기존 데이터가 없으면 expiry_date만 저장
                        db.child("users").child(user_id).update({"expiry_date": expiry_date})
                        print(f"✓ Realtime Database에 만료일 저장 성공 (새 데이터)")
                    rtdb_success = True
                else:
                    print("⚠ Realtime Database 인스턴스가 없습니다.")
            except Exception as rtdb_error:
                print(f"⚠ Realtime Database 저장 실패: {str(rtdb_error)}")
                import traceback
                traceback.print_exc()
            
            # 둘 중 하나라도 성공하면 성공으로 처리
            if firestore_success or rtdb_success:
                return jsonify({
                    'success': True, 
                    'message': f'이용만료일이 {expiry_date[:10]}로 변경되었습니다.'
                })
            else:
                return jsonify({
                    'success': False, 
                    'message': f'Firestore 및 Realtime Database 저장 모두 실패했습니다.'
                }), 500
        except Exception as db_error:
            import traceback
            error_msg = str(db_error)
            print(f"❌ Firestore 저장 실패: {error_msg}")
            traceback.print_exc()
            return jsonify({
                'success': False, 
                'message': f'데이터베이스 업데이트 실패: {error_msg[:100]}. Firebase Console에서 규칙을 확인해주세요.'
            }), 500
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'}), 500


@app.route('/payments')
def payments():
    """결제 관리"""
    if not check_admin():
        flash('로그인이 필요합니다.', 'error')
        return redirect(url_for('login'))
    
    try:
        # Firestore에서 사용자 및 결제 정보 조회
        pending_payments = []
        payments_list = []
        try:
            import requests
            project_id = "blog-cdc9b"
            id_token = session.get('token')
            
            if id_token:
                headers = {
                    "Authorization": f"Bearer {id_token}",
                    "Content-Type": "application/json"
                }
                
                # 사용자 목록 조회
                users_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users"
                users_response = requests.get(users_url, headers=headers, timeout=10)
                
                if users_response.status_code == 200:
                    users_data = users_response.json()
                    documents = users_data.get("documents", [])
                    
                    for doc in documents:
                        doc_name = doc.get("name", "")
                        user_id = doc_name.split("/")[-1] if "/" in doc_name else ""
                        fields = doc.get("fields", {})
                        
                        # 결제 대기 목록
                        payment_pending = fields.get("payment_pending", {}).get("booleanValue", False)
                        if payment_pending:
                            user_data = {
                                "user_id": user_id,
                                "email": fields.get("email", {}).get("stringValue", ""),
                                "name": fields.get("name", {}).get("stringValue", ""),
                                "payment_pending": True
                            }
                            pending_payments.append(user_data)
                
                # 결제 내역 조회
                payments_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/payments"
                payments_response = requests.get(payments_url, headers=headers, timeout=10)
                
                if payments_response.status_code == 200:
                    payments_data = payments_response.json()
                    documents = payments_data.get("documents", [])
                    
                    for doc in documents:
                        doc_name = doc.get("name", "")
                        payment_id = doc_name.split("/")[-1] if "/" in doc_name else ""
                        fields = doc.get("fields", {})
                        
                        payment_data = {
                            "payment_id": payment_id,
                            "user_id": fields.get("user_id", {}).get("stringValue", ""),
                            "email": fields.get("email", {}).get("stringValue", ""),
                            "name": fields.get("name", {}).get("stringValue", ""),
                            "payment_date": fields.get("payment_date", {}).get("timestampValue", "").replace("Z", "") if "timestampValue" in fields.get("payment_date", {}) else "",
                            "status": fields.get("status", {}).get("stringValue", ""),
                            "expiry_date": fields.get("expiry_date", {}).get("timestampValue", "").replace("Z", "") if "timestampValue" in fields.get("expiry_date", {}) else ""
                        }
                        payments_list.append(payment_data)
        except Exception as db_error:
            # 데이터베이스가 없어도 빈 목록 표시
            print(f"⚠ Firestore 조회 실패: {str(db_error)[:100]}")
        
        # 날짜순 정렬
        payments_list.sort(key=lambda x: x.get("payment_date", ""), reverse=True)
        
        return render_template('payments.html', 
                             pending_payments=pending_payments,
                             payments=payments_list)
    
    except Exception as e:
        flash(f'결제 정보를 불러오는 중 오류가 발생했습니다: {str(e)}', 'error')
        return render_template('payments.html', pending_payments=[], payments=[])


@app.route('/payments/confirm/<user_id>', methods=['POST'])
def confirm_payment(user_id):
    """결제 확인 및 30일 연장"""
    if not check_admin():
        return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403
    
    try:
        import requests
        project_id = "blog-cdc9b"
        id_token = session.get('token')
        
        if not id_token:
            return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
        
        headers = {
            "Authorization": f"Bearer {id_token}",
            "Content-Type": "application/json"
        }
        
        # Firestore에서 사용자 정보 가져오기
        user_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users/{user_id}"
        user_response = requests.get(user_url, headers=headers, timeout=5)
        
        if user_response.status_code != 200:
            return jsonify({'success': False, 'message': '사용자를 찾을 수 없습니다.'}), 404
        
        user_doc = user_response.json()
        if "fields" not in user_doc:
            return jsonify({'success': False, 'message': '사용자 정보를 찾을 수 없습니다.'}), 404
        
        fields = user_doc["fields"]
        user_data = {
            "email": fields.get("email", {}).get("stringValue", ""),
            "name": fields.get("name", {}).get("stringValue", "")
        }
        
        # 현재 날짜로부터 30일 후로 만료일 설정
        now = datetime.now()
        new_expiry_date_iso = (now + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        last_payment_date_iso = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        payment_date_iso = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        # 사용자 정보 업데이트
        update_fields = {
            "expiry_date": {"timestampValue": new_expiry_date_iso},
            "payment_pending": {"booleanValue": False},
            "last_payment_date": {"timestampValue": last_payment_date_iso}
        }
        
        # 기존 필드와 병합
        merged_fields = {**fields, **update_fields}
        user_update_doc = {"fields": merged_fields}
        
        user_update_response = requests.patch(user_url, json=user_update_doc, headers=headers, timeout=10)
        
        if user_update_response.status_code not in [200, 201]:
            return jsonify({'success': False, 'message': '사용자 정보 업데이트 실패'}), 500
        
        # 결제 내역 저장
        payment_doc = {
            "fields": {
                "user_id": {"stringValue": user_id},
                "email": {"stringValue": user_data.get("email", "")},
                "name": {"stringValue": user_data.get("name", "")},
                "payment_date": {"timestampValue": payment_date_iso},
                "status": {"stringValue": "confirmed"},
                "confirmed_by": {"stringValue": session.get('user_id', '')},
                "confirmed_at": {"timestampValue": payment_date_iso},
                "expiry_date": {"timestampValue": new_expiry_date_iso}
            }
        }
        
        payments_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/payments"
        payment_response = requests.post(payments_url, json=payment_doc, headers=headers, timeout=10)
        
        if payment_response.status_code in [200, 201]:
            return jsonify({
                'success': True, 
                'message': '결제가 확인되었습니다. 이용 기간이 30일 연장되었습니다.',
                'expiry_date': new_expiry_date_iso[:10]  # 날짜만 반환
            })
        else:
            return jsonify({
                'success': False,
                'message': f'결제 내역 저장 실패: HTTP {payment_response.status_code}'
            }), 500
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'}), 500


if __name__ == '__main__':
    import os
    # .env 파일 로드 비활성화 (config.json 사용)
    os.environ.pop('FLASK_ENV', None)
    
    print("=" * 60)
    print("관리자 페이지 서버 시작")
    print("=" * 60)
    print("브라우저에서 다음 주소로 접속하세요:")
    print("  http://localhost:5000")
    print("  http://127.0.0.1:5000")
    print("=" * 60)
    print("\n로그인 정보:")
    print("  이메일: sprince1004@naver.com")
    print("  비밀번호: skybj6942")
    print("=" * 60)
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
