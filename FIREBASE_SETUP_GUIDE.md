# Firebase Realtime Database 설정 가이드

## 문제 해결: 관리자 정보가 데이터베이스에 저장되지 않는 문제

### 1. Firebase Realtime Database 활성화

1. **Firebase Console 접속**
   - https://console.firebase.google.com/
   - 프로젝트 선택: `blog-cdc9b`

2. **Realtime Database 생성**
   - 왼쪽 메뉴에서 "Realtime Database" 클릭
   - "데이터베이스 만들기" 버튼 클릭
   - 위치 선택 (가장 가까운 지역 선택)
   - 보안 규칙: "테스트 모드로 시작" 선택 (나중에 변경 가능)
   - "완료" 클릭

### 2. 데이터베이스 규칙 설정

1. **규칙 탭 클릭**
2. **다음 규칙으로 변경:**

```json
{
  "rules": {
    "users": {
      "$uid": {
        ".read": true,
        ".write": true
      }
    },
    "tasks": {
      ".read": true,
      ".write": true
    },
    "payments": {
      ".read": true,
      ".write": true
    }
  }
}
```

3. **게시 버튼 클릭**

### 3. 관리자 정보 수동 설정 (선택사항)

만약 자동 저장이 안 되면, Firebase Console에서 수동으로 설정:

1. **데이터 탭으로 이동**
2. **다음 경로에 데이터 추가:**
   ```
   users/GVRsKWtrqwMr32HQumlIL3CTqE62
   ```
3. **다음 필드 추가:**
   - `is_admin`: `true` (boolean)
   - `approved`: `true` (boolean)
   - `email`: `sprince1004@naver.com`
   - `name`: `관리자`

### 4. 관리자 계정 정보

- **이메일**: `sprince1004@naver.com`
- **비밀번호**: `skybj6942`
- **사용자 ID**: `GVRsKWtrqwMr32HQumlIL3CTqE62`

## 로그인 후 페이지 연결 문제 해결

1. **서버가 실행 중인지 확인**
   ```powershell
   cd C:\blog-master\admin_web
   C:\Python313\python.exe app.py
   ```

2. **브라우저에서 접속**
   - `http://localhost:5000` 또는 `http://127.0.0.1:5000`

3. **로그인 후 대시보드 접근 확인**
   - 로그인 후 `/dashboard` 경로로 리다이렉트됩니다.
   - 문제가 계속되면 브라우저 개발자 도구(F12)에서 오류 확인

## 확인 사항

- [ ] Firebase Realtime Database가 생성되었는가?
- [ ] 데이터베이스 규칙이 올바르게 설정되었는가?
- [ ] 관리자 계정 정보가 데이터베이스에 저장되었는가?
- [ ] 서버가 정상적으로 실행 중인가?
- [ ] 브라우저에서 localhost:5000으로 접속 가능한가?

