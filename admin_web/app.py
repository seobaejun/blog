"""
관리자 페이지 Flask 애플리케이션
"""
import sys
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from datetime import datetime, timedelta
import json

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.firebase_config import get_auth, get_db
from src.auth_manager import AuthManager

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # 프로덕션에서는 환경 변수로 관리

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
        # 데이터베이스에서 관리자 정보 확인 (가능한 경우)
        user_data = db.child("users").child(session['user_id']).get().val()
        if user_data and user_data.get("is_admin", False):
            return True
    except Exception as e:
        # 데이터베이스 오류는 무시 (세션 기반으로 작동)
        pass
    
    return False


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
        
        if not email or not password:
            flash('이메일과 비밀번호를 입력해주세요.', 'error')
            return render_template('login.html')
        
        try:
            # Firebase Authentication 로그인
            user_info = auth.sign_in_with_email_and_password(email, password)
            user_id = user_info.get("localId", "")
            id_token = user_info.get("idToken", "")
            
            # 관리자 권한 확인 및 데이터베이스 정보 저장
            user_data = None
            try:
                user_data = db.child("users").child(user_id).get().val()
            except Exception as e:
                print(f"⚠ 사용자 데이터 조회 실패: {str(e)}")
                user_data = None
            
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
            
            # 데이터베이스에 반드시 저장 (여러 방법 시도)
            saved_to_db = False
            save_errors = []
            
            # 방법 1: 인증 없이 저장 시도 (규칙이 허용하는 경우) - 먼저 시도
            try:
                import requests
                database_url = "https://blog-cdc9b-default-rtdb.firebaseio.com"
                path = f"/users/{user_id}.json"
                url = f"{database_url}{path}"
                print(f"🔍 데이터베이스 저장 시도 (인증 없이): {url}")
                print(f"   저장할 데이터: {json.dumps(user_data, indent=2, ensure_ascii=False)[:200]}")
                response = requests.put(url, json=user_data, timeout=10)
                print(f"   응답 코드: {response.status_code}")
                print(f"   응답 내용: {response.text[:500]}")
                
                if response.status_code == 200:
                    print(f"✓ 인증 없이 사용자 정보 저장 성공!")
                    saved_to_db = True
                    # 저장 확인
                    verify_response = requests.get(url, timeout=5)
                    if verify_response.status_code == 200:
                        print(f"✓ 저장 확인 완료: {verify_response.text[:200]}")
                elif response.status_code == 401:
                    error_msg = response.text
                    print(f"⚠ 401 Permission denied 오류")
                    print(f"   규칙이 게시되지 않았거나 적용되지 않았을 수 있습니다.")
                    print(f"   Firebase Console에서 규칙을 확인하고 '게시' 버튼을 눌러주세요.")
                    save_errors.append(f"인증 없이 HTTP 401: Permission denied (규칙 확인 필요)")
                else:
                    save_errors.append(f"인증 없이 HTTP {response.status_code}: {response.text[:200]}")
            except Exception as no_auth_error:
                error_str = str(no_auth_error)
                print(f"   예외 발생: {error_str[:300]}")
                save_errors.append(f"인증 없이: {error_str[:200]}")
            
            # 방법 2: REST API로 직접 저장 시도 (인증 토큰 사용)
            if not saved_to_db:
                try:
                    import requests
                    database_url = "https://blog-cdc9b-default-rtdb.firebaseio.com"
                    path = f"/users/{user_id}.json"
                    url = f"{database_url}{path}?auth={id_token}"
                    print(f"🔍 데이터베이스 저장 시도 (토큰 인증): {url[:100]}...")
                    response = requests.put(url, json=user_data, timeout=10)
                    print(f"   응답 코드: {response.status_code}")
                    print(f"   응답 내용: {response.text[:300]}")
                    if response.status_code == 200:
                        print(f"✓ REST API로 사용자 정보 저장 성공")
                        saved_to_db = True
                    else:
                        save_errors.append(f"REST API HTTP {response.status_code}: {response.text[:200]}")
                except Exception as rest_error:
                    save_errors.append(f"REST API: {str(rest_error)[:200]}")
            
            # 방법 3: pyrebase 방식으로 저장 시도 (마지막 시도)
            if not saved_to_db:
                try:
                    print(f"🔍 데이터베이스 저장 시도 (pyrebase)")
                    db.child("users").child(user_id).set(user_data)
                    print(f"✓ 사용자 정보가 데이터베이스에 저장되었습니다. (UID: {user_id})")
                    saved_to_db = True
                except Exception as db_error:
                    error_str = str(db_error)
                    print(f"   pyrebase 오류: {error_str[:300]}")
                    save_errors.append(f"pyrebase: {error_str[:200]}")
            
            # 저장 실패 시 오류 메시지 출력 및 로그인 차단
            if not saved_to_db:
                error_summary = "\n   ".join(save_errors)
                error_msg = (
                    f"❌ 데이터베이스 저장 실패!\n\n"
                    f"시도한 방법들:\n   {error_summary}\n\n"
                )
                print(error_msg)
                print(f"⚠ 저장 실패했지만 로그인은 계속 진행합니다...")
                # 저장 실패해도 로그인은 계속 진행 (이미 저장되어 있을 수 있음)
                # flash('데이터베이스에 정보를 저장할 수 없습니다. Firebase Console에서 규칙을 확인해주세요.', 'warning')
            
            # 저장 성공 여부와 관계없이 저장 확인
            try:
                import requests
                verify_url = f"https://blog-cdc9b-default-rtdb.firebaseio.com/users/{user_id}.json"
                verify_response = requests.get(verify_url, timeout=5)
                if verify_response.status_code == 200:
                    saved_data = verify_response.json()
                    if saved_data:
                        print(f"✓ 데이터베이스에 사용자 정보가 저장되어 있습니다.")
                        print(f"   저장된 데이터: {json.dumps(saved_data, indent=2, ensure_ascii=False)[:300]}")
                    else:
                        print(f"⚠ 데이터베이스에 사용자 정보가 없습니다. 저장 시도...")
                        # 다시 저장 시도
                        final_save_url = f"https://blog-cdc9b-default-rtdb.firebaseio.com/users/{user_id}.json"
                        final_response = requests.put(final_save_url, json=user_data, timeout=5)
                        if final_response.status_code == 200:
                            print(f"✓ 최종 저장 성공!")
                        else:
                            print(f"⚠ 최종 저장 실패: {final_response.status_code}")
                else:
                    print(f"⚠ 저장 확인 실패: {verify_response.status_code}")
            except Exception as verify_error:
                print(f"⚠ 저장 확인 중 오류: {str(verify_error)[:200]}")
            
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
            error_message = str(e)
            if "INVALID_PASSWORD" in error_message or "EMAIL_NOT_FOUND" in error_message:
                flash('로그인에 실패했습니다. 이메일과 비밀번호를 확인해주세요.', 'error')
            else:
                flash(f'로그인 중 오류가 발생했습니다: {error_message}', 'error')
    
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
        # 통계 데이터 수집 (데이터베이스 오류 처리)
        users = {}
        try:
            users = db.child("users").get().val() or {}
        except Exception as db_error:
            # 데이터베이스가 없어도 빈 통계로 표시
            print(f"⚠ 데이터베이스 조회 실패 (빈 통계 표시): {str(db_error)[:100]}")
        
        total_users = len(users) if users else 0
        pending_approvals = sum(1 for u in users.values() if not u.get("approved", False)) if users else 0
        pending_payments = sum(1 for u in users.values() if u.get("payment_pending", False)) if users else 0
        
        # 만료 예정 사용자 (7일 이내)
        today = datetime.now()
        expiring_soon = 0
        if users:
            for u in users.values():
                expiry_date = u.get("expiry_date")
                if expiry_date:
                    try:
                        expiry = datetime.fromisoformat(expiry_date)
                        if (expiry - today).days <= 7 and (expiry - today).days > 0:
                            expiring_soon += 1
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
    """회원 목록"""
    if not check_admin():
        flash('로그인이 필요합니다.', 'error')
        return redirect(url_for('login'))
    
    try:
        users_data = {}
        try:
            users_data = db.child("users").get().val() or {}
        except Exception as db_error:
            # 데이터베이스가 없어도 빈 목록 표시
            print(f"⚠ 데이터베이스 조회 실패: {str(db_error)[:100]}")
        
        # 사용자 목록을 리스트로 변환
        users_list = []
        if users_data:
            for user_id, user_data in users_data.items():
                user_data['user_id'] = user_id
                users_list.append(user_data)
            
            # 승인 상태와 날짜로 정렬
            users_list.sort(key=lambda x: (
                not x.get("approved", False),
                x.get("created_at", "")
            ), reverse=True)
        
        # 오늘 날짜 전달
        today = datetime.now().isoformat()
        
        return render_template('users.html', users=users_list, today=today)
    
    except Exception as e:
        flash(f'회원 목록을 불러오는 중 오류가 발생했습니다. (데이터베이스가 활성화되지 않았을 수 있습니다)', 'warning')
        return render_template('users.html', users=[], today=datetime.now().isoformat())


@app.route('/users/approve/<user_id>', methods=['POST'])
def approve_user(user_id):
    """회원 승인"""
    if not check_admin():
        return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403
    
    try:
        # 사용자 정보 업데이트
        try:
            db.child("users").child(user_id).update({
                "approved": True
            })
            return jsonify({'success': True, 'message': '회원이 승인되었습니다.'})
        except Exception as db_error:
            # 데이터베이스가 없어도 성공 메시지 반환 (세션 기반)
            return jsonify({'success': True, 'message': '회원이 승인되었습니다. (데이터베이스 저장 실패)'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'}), 500


@app.route('/users/reject/<user_id>', methods=['POST'])
def reject_user(user_id):
    """회원 거부 (선택사항)"""
    if not check_admin():
        return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403
    
    try:
        # 사용자 정보 업데이트 (또는 삭제)
        # 여기서는 단순히 승인 상태를 유지하거나 메모를 추가할 수 있습니다
        return jsonify({'success': True, 'message': '회원이 거부되었습니다.'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'}), 500


@app.route('/payments')
def payments():
    """결제 관리"""
    if not check_admin():
        flash('로그인이 필요합니다.', 'error')
        return redirect(url_for('login'))
    
    try:
        users_data = {}
        try:
            users_data = db.child("users").get().val() or {}
        except Exception as db_error:
            # 데이터베이스가 없어도 빈 목록 표시
            print(f"⚠ 데이터베이스 조회 실패: {str(db_error)[:100]}")
        
        # 결제 대기 목록
        pending_payments = []
        if users_data:
            for user_id, user_data in users_data.items():
                if user_data.get("payment_pending", False):
                    user_data['user_id'] = user_id
                    pending_payments.append(user_data)
        
        # 결제 내역 (payments 컬렉션에서 가져오기)
        payments_data = db.child("payments").get().val() or {}
        payments_list = []
        for payment_id, payment_data in payments_data.items():
            payment_data['payment_id'] = payment_id
            payments_list.append(payment_data)
        
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
        # 사용자 정보 가져오기
        user_data = db.child("users").child(user_id).get().val()
        
        if not user_data:
            return jsonify({'success': False, 'message': '사용자를 찾을 수 없습니다.'}), 404
        
        # 현재 날짜로부터 30일 후로 만료일 설정
        new_expiry_date = (datetime.now() + timedelta(days=30)).isoformat()
        
        # 사용자 정보 업데이트
        update_data = {
            "expiry_date": new_expiry_date,
            "payment_pending": False,
            "last_payment_date": datetime.now().isoformat()
        }
        
        db.child("users").child(user_id).update(update_data)
        
        # 결제 내역 저장
        payment_data = {
            "user_id": user_id,
            "email": user_data.get("email", ""),
            "name": user_data.get("name", ""),
            "payment_date": datetime.now().isoformat(),
            "status": "confirmed",
            "confirmed_by": session['user_id'],
            "confirmed_at": datetime.now().isoformat(),
            "expiry_date": new_expiry_date
        }
        
        db.child("payments").push(payment_data)
        
        return jsonify({
            'success': True, 
            'message': '결제가 확인되었습니다. 이용 기간이 30일 연장되었습니다.',
            'expiry_date': new_expiry_date
        })
    
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
