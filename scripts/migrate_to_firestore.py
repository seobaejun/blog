"""
Realtime Database에서 Firestore로 데이터 마이그레이션 스크립트
"""
import json
import requests
from datetime import datetime
from pathlib import Path
import sys

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.firebase_config import get_auth


def get_realtime_database_data():
    """Realtime Database에서 모든 데이터 가져오기"""
    try:
        # config.json에서 projectId 가져오기
        config_path = project_root / "config.json"
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        
        project_id = config_data["firebase"]["projectId"]
        database_url = f"https://{project_id}-default-rtdb.firebaseio.com"
        
        print(f"🔍 Realtime Database에서 데이터 가져오기 시도...")
        print(f"   URL: {database_url}")
        
        # 마이그레이션을 위해 임시로 databaseURL 추가
        import pyrebase
        firebase_config = config_data["firebase"].copy()
        firebase_config["databaseURL"] = database_url
        
        # Firebase 초기화 (마이그레이션용)
        firebase = pyrebase.initialize_app(firebase_config)
        auth = firebase.auth()
        # 관리자 이메일로 로그인 (실제 이메일/비밀번호 필요)
        print("\n⚠ 관리자 이메일과 비밀번호를 입력해야 합니다.")
        email = input("관리자 이메일: ").strip()
        password = input("비밀번호: ").strip()
        
        user_info = auth.sign_in_with_email_and_password(email, password)
        id_token = user_info.get("idToken")
        
        print(f"✓ 로그인 성공\n")
        
        # Realtime Database REST API로 모든 데이터 가져오기
        url = f"{database_url}/.json?auth={id_token}"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Realtime Database 데이터 가져오기 성공")
            return data, id_token
        else:
            print(f"❌ Realtime Database 데이터 가져오기 실패: HTTP {response.status_code}")
            print(f"   응답: {response.text[:500]}")
            return None, None
    
    except Exception as e:
        print(f"❌ Realtime Database 데이터 가져오기 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None


def normalize_timestamp(value):
    """타임스탬프 문자열을 Firestore 형식으로 정규화"""
    if not isinstance(value, str):
        return None
    
    # ISO 형식 날짜 문자열인지 확인
    if "T" in value or (len(value) == 10 and value.count("-") == 2):
        try:
            if "T" in value:
                # ISO 형식: 2024-11-06T12:00:00 또는 2024-11-06T12:00:00Z
                # 시간대 정보 제거하고 UTC로 변환
                if "+" in value:
                    # +09:00 같은 시간대 제거
                    value = value.split("+")[0]
                elif "-" in value[-6:] and value[-6] in ["+", "-"]:
                    # -05:00 같은 시간대 제거
                    value = value[:-6]
                
                # Z가 없으면 추가
                if not value.endswith("Z"):
                    # 마이크로초 확인
                    if "." in value:
                        # 마이크로초가 있으면 Z만 추가
                        value = value + "Z"
                    else:
                        # 마이크로초가 없으면 추가
                        value = value + ".000000Z"
                
                # Firestore 형식 검증 (RFC3339)
                return value
            elif len(value) == 10 and value.count("-") == 2:
                # 날짜만 있는 형식: 2024-11-06
                # 자정으로 설정
                return value + "T00:00:00.000000Z"
        except:
            pass
    
    return None


def convert_to_firestore_format(value, field_name=""):
    """Realtime Database 값을 Firestore 형식으로 변환"""
    if value is None:
        return {"nullValue": None}
    elif isinstance(value, bool):
        return {"booleanValue": value}
    elif isinstance(value, int):
        return {"integerValue": str(value)}
    elif isinstance(value, float):
        return {"doubleValue": value}
    elif isinstance(value, str):
        # 타임스탬프 형식인지 확인
        normalized_ts = normalize_timestamp(value)
        if normalized_ts:
            return {"timestampValue": normalized_ts}
        return {"stringValue": value}
    elif isinstance(value, dict):
        # 맵으로 변환
        fields = {}
        for k, v in value.items():
            fields[k] = convert_to_firestore_format(v, k)
        return {"mapValue": {"fields": fields}}
    elif isinstance(value, list):
        # 배열로 변환
        array_values = [convert_to_firestore_format(item) for item in value]
        return {"arrayValue": {"values": array_values}}
    else:
        # 기본적으로 문자열로 변환
        return {"stringValue": str(value)}


def migrate_users_to_firestore(users_data, id_token):
    """users 컬렉션을 Firestore로 마이그레이션"""
    if not users_data:
        print("⚠ users 데이터가 없습니다.")
        return 0
    
    project_id = "blog-cdc9b"
    firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users"
    
    headers = {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json"
    }
    
    migrated_count = 0
    skipped_count = 0
    error_count = 0
    
    print(f"\n{'='*60}")
    print(f"📦 users 컬렉션 마이그레이션 시작")
    print(f"{'='*60}\n")
    
    for user_id, user_data in users_data.items():
        try:
            print(f"🔍 사용자 마이그레이션: {user_id}")
            
            # Firestore 형식으로 변환
            firestore_doc = {
                "fields": {}
            }
            
            for key, value in user_data.items():
                firestore_doc["fields"][key] = convert_to_firestore_format(value, key)
            
            # user_id 필드 추가 (없으면)
            if "user_id" not in firestore_doc["fields"]:
                firestore_doc["fields"]["user_id"] = {"stringValue": user_id}
            
            # Firestore에 저장 (PATCH로 업데이트 또는 생성)
            doc_url = f"{firestore_url}/{user_id}"
            response = requests.patch(doc_url, json=firestore_doc, headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                print(f"   ✓ 마이그레이션 성공: {user_id}")
                migrated_count += 1
            else:
                print(f"   ❌ 마이그레이션 실패: HTTP {response.status_code}")
                print(f"      응답: {response.text[:200]}")
                error_count += 1
        
        except Exception as e:
            print(f"   ❌ 오류 발생: {str(e)}")
            error_count += 1
    
    print(f"\n{'='*60}")
    print(f"📊 users 마이그레이션 결과")
    print(f"   성공: {migrated_count}개")
    print(f"   실패: {error_count}개")
    print(f"{'='*60}\n")
    
    return migrated_count


def migrate_payments_to_firestore(payments_data, id_token):
    """payments 컬렉션을 Firestore로 마이그레이션"""
    if not payments_data:
        print("⚠ payments 데이터가 없습니다.")
        return 0
    
    project_id = "blog-cdc9b"
    firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/payments"
    
    headers = {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json"
    }
    
    migrated_count = 0
    error_count = 0
    
    print(f"\n{'='*60}")
    print(f"📦 payments 컬렉션 마이그레이션 시작")
    print(f"{'='*60}\n")
    
    for payment_id, payment_data in payments_data.items():
        try:
            print(f"🔍 결제 내역 마이그레이션: {payment_id}")
            
            # Firestore 형식으로 변환
            firestore_doc = {
                "fields": {}
            }
            
            for key, value in payment_data.items():
                firestore_doc["fields"][key] = convert_to_firestore_format(value, key)
            
            # payment_id 필드 추가 (없으면)
            if "payment_id" not in firestore_doc["fields"]:
                firestore_doc["fields"]["payment_id"] = {"stringValue": payment_id}
            
            # Firestore에 저장 (POST로 새 문서 생성)
            response = requests.post(
                firestore_url,
                json=firestore_doc,
                headers=headers,
                params={"documentId": payment_id},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"   ✓ 마이그레이션 성공: {payment_id}")
                migrated_count += 1
            else:
                print(f"   ❌ 마이그레이션 실패: HTTP {response.status_code}")
                print(f"      응답: {response.text[:200]}")
                error_count += 1
        
        except Exception as e:
            print(f"   ❌ 오류 발생: {str(e)}")
            error_count += 1
    
    print(f"\n{'='*60}")
    print(f"📊 payments 마이그레이션 결과")
    print(f"   성공: {migrated_count}개")
    print(f"   실패: {error_count}개")
    print(f"{'='*60}\n")
    
    return migrated_count


def migrate_tasks_to_firestore(tasks_data, id_token):
    """tasks 컬렉션을 Firestore로 마이그레이션"""
    if not tasks_data:
        print("⚠ tasks 데이터가 없습니다.")
        return 0
    
    project_id = "blog-cdc9b"
    firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/tasks"
    
    headers = {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json"
    }
    
    migrated_count = 0
    error_count = 0
    
    print(f"\n{'='*60}")
    print(f"📦 tasks 컬렉션 마이그레이션 시작")
    print(f"{'='*60}\n")
    
    for task_id, task_data in tasks_data.items():
        try:
            print(f"🔍 작업 로그 마이그레이션: {task_id}")
            
            # Firestore 형식으로 변환
            firestore_doc = {
                "fields": {}
            }
            
            for key, value in task_data.items():
                firestore_doc["fields"][key] = convert_to_firestore_format(value, key)
            
            # task_id 필드 추가 (없으면)
            if "task_id" not in firestore_doc["fields"]:
                firestore_doc["fields"]["task_id"] = {"stringValue": task_id}
            
            # Firestore에 저장 (POST로 새 문서 생성)
            response = requests.post(
                firestore_url,
                json=firestore_doc,
                headers=headers,
                params={"documentId": task_id},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"   ✓ 마이그레이션 성공: {task_id}")
                migrated_count += 1
            else:
                print(f"   ❌ 마이그레이션 실패: HTTP {response.status_code}")
                print(f"      응답: {response.text[:200]}")
                error_count += 1
        
        except Exception as e:
            print(f"   ❌ 오류 발생: {str(e)}")
            error_count += 1
    
    print(f"\n{'='*60}")
    print(f"📊 tasks 마이그레이션 결과")
    print(f"   성공: {migrated_count}개")
    print(f"   실패: {error_count}개")
    print(f"{'='*60}\n")
    
    return migrated_count


def main():
    """메인 마이그레이션 함수"""
    print(f"\n{'='*60}")
    print(f"🚀 Realtime Database → Firestore 마이그레이션 시작")
    print(f"{'='*60}\n")
    
    # Realtime Database에서 데이터 가져오기
    rtdb_data, id_token = get_realtime_database_data()
    
    if not rtdb_data or not id_token:
        print("❌ Realtime Database에서 데이터를 가져올 수 없습니다.")
        return
    
    print(f"\n✓ Realtime Database 데이터 구조:")
    print(f"   컬렉션: {list(rtdb_data.keys())}\n")
    
    total_migrated = 0
    
    # users 컬렉션 마이그레이션
    if "users" in rtdb_data:
        count = migrate_users_to_firestore(rtdb_data["users"], id_token)
        total_migrated += count
    
    # payments 컬렉션 마이그레이션
    if "payments" in rtdb_data:
        count = migrate_payments_to_firestore(rtdb_data["payments"], id_token)
        total_migrated += count
    
    # tasks 컬렉션 마이그레이션
    if "tasks" in rtdb_data:
        count = migrate_tasks_to_firestore(rtdb_data["tasks"], id_token)
        total_migrated += count
    
    # 기타 컬렉션 처리
    for collection_name in rtdb_data.keys():
        if collection_name not in ["users", "payments", "tasks"]:
            print(f"⚠ 알 수 없는 컬렉션: {collection_name} (건너뜀)")
    
    print(f"\n{'='*60}")
    print(f"✅ 마이그레이션 완료!")
    print(f"   총 마이그레이션된 문서: {total_migrated}개")
    print(f"{'='*60}\n")
    
    print("📝 다음 단계:")
    print("   1. Firebase Console > Firestore Database에서 데이터 확인")
    print("   2. 모든 데이터가 정상적으로 마이그레이션되었는지 확인")
    print("   3. Realtime Database 삭제 (선택사항)")


if __name__ == "__main__":
    main()

