# Realtime Database 완전 비활성화 가이드

## 방법 1: Firebase Console에서 Realtime Database 삭제 (권장)

### 단계별 가이드

1. **Firebase Console 접속**
   - https://console.firebase.google.com/ 접속
   - 프로젝트 `blog-cdc9b` 선택

2. **Realtime Database 삭제**
   - 왼쪽 메뉴에서 **"Realtime Database"** 클릭
   - 상단의 **"..." (점 3개)** 메뉴 클릭
   - **"데이터베이스 삭제"** 선택
   - 확인 메시지에 **"데이터베이스 이름 입력"** 후 삭제 확인

3. **완료 확인**
   - Realtime Database 메뉴가 사라지거나 비활성화됨

## 방법 2: 코드에서 완전히 제거 (이미 완료됨)

### 확인 사항

1. **config.json 확인**
   ```json
   {
     "firebase": {
       "apiKey": "...",
       "authDomain": "...",
       "projectId": "...",
       "storageBucket": "...",
       "messagingSenderId": "...",
       "appId": "...",
       "measurementId": "..."
       // databaseURL이 없어야 함!
     }
   }
   ```

2. **코드 확인**
   - `src/firebase_config.py`: `databaseURL` 자동 제거 로직 있음
   - `src/auth_manager.py`: `self.db` 사용 안 함
   - `admin_web/app.py`: `db` 사용 안 함

## 방법 3: 환경 변수에서 제거

Vercel이나 다른 배포 환경에서:
- `FIREBASE_DATABASE_URL` 환경 변수 제거

## 확인 방법

프로그램 실행 시 다음 메시지가 나와야 함:
```
⚠ databaseURL이 제거되었습니다. Realtime Database는 사용하지 않습니다.
✓ Firebase 초기화 완료 (Auth만 사용, Realtime Database는 사용하지 않음)
```

## 문제 해결

만약 여전히 Realtime Database가 사용된다면:

1. **캐시 삭제**
   - Python `__pycache__` 폴더 삭제
   - 프로그램 재시작

2. **config.json 재확인**
   - `databaseURL`이 정말 없는지 확인
   - JSON 형식이 올바른지 확인

3. **Firebase Console 확인**
   - Realtime Database가 삭제되었는지 확인

