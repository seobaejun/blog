"""
Firebase Realtime Database 규칙 테스트 스크립트
"""
import requests
import json

def test_firebase_rules():
    """Firebase 규칙 테스트"""
    database_url = "https://blog-cdc9b-default-rtdb.firebaseio.com"
    
    print("=" * 60)
    print("Firebase Realtime Database 규칙 테스트")
    print("=" * 60)
    
    # 테스트 1: 루트 읽기
    print("\n1. 루트 읽기 테스트...")
    try:
        response = requests.get(f"{database_url}/.json", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        if response.status_code == 200:
            print("   ✓ 루트 읽기 성공!")
        elif response.status_code == 401:
            print("   ❌ Permission denied - 규칙이 읽기를 차단하고 있습니다")
        elif response.status_code == 404:
            print("   ❌ Not Found - 데이터베이스가 활성화되지 않았을 수 있습니다")
    except Exception as e:
        print(f"   ❌ 오류: {str(e)}")
    
    # 테스트 2: 루트 쓰기
    print("\n2. 루트 쓰기 테스트...")
    try:
        test_data = {"test": "value", "timestamp": "2025-11-06"}
        response = requests.put(f"{database_url}/test_node.json", json=test_data, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        if response.status_code == 200:
            print("   ✓ 루트 쓰기 성공!")
            # 테스트 데이터 삭제
            requests.delete(f"{database_url}/test_node.json")
        elif response.status_code == 401:
            print("   ❌ Permission denied - 규칙이 쓰기를 차단하고 있습니다")
        elif response.status_code == 404:
            print("   ❌ Not Found - 데이터베이스가 활성화되지 않았을 수 있습니다")
    except Exception as e:
        print(f"   ❌ 오류: {str(e)}")
    
    # 테스트 3: users 경로 쓰기
    print("\n3. users 경로 쓰기 테스트...")
    try:
        test_data = {"test_user": "test_value"}
        response = requests.put(f"{database_url}/users/test_user_id.json", json=test_data, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        if response.status_code == 200:
            print("   ✓ users 경로 쓰기 성공!")
            # 테스트 데이터 삭제
            requests.delete(f"{database_url}/users/test_user_id.json")
        elif response.status_code == 401:
            print("   ❌ Permission denied - 규칙이 users 경로 쓰기를 차단하고 있습니다")
        elif response.status_code == 404:
            print("   ❌ Not Found - 데이터베이스가 활성화되지 않았을 수 있습니다")
    except Exception as e:
        print(f"   ❌ 오류: {str(e)}")
    
    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)
    
    print("\n해석:")
    print("- Status 200: 규칙이 올바르게 설정됨")
    print("- Status 401: 규칙이 접근을 차단함 (규칙 확인 필요)")
    print("- Status 404: 데이터베이스가 활성화되지 않음")
    print("\n규칙이 올바르게 설정되어 있다면 모두 200이어야 합니다.")

if __name__ == "__main__":
    test_firebase_rules()


