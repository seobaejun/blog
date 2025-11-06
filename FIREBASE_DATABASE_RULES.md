# Firebase Realtime Database 규칙 설정 가이드

## 현재 상황
Firebase Realtime Database가 활성화되지 않아 404 오류가 발생하고 있습니다.

## 규칙 설정 방법

### 1. Firebase Console 접속
- https://console.firebase.google.com/
- 프로젝트: `blog-cdc9b` 선택

### 2. Realtime Database 활성화
1. 왼쪽 메뉴에서 **"Realtime Database"** 클릭
2. **"데이터베이스 만들기"** 클릭
3. 위치 선택 (가장 가까운 지역 선택)
4. **"완료"** 클릭

### 3. 규칙 설정

#### 방법 A: 개발 단계 (모든 접근 허용)
**주의**: 개발/테스트용입니다. 프로덕션에서는 사용하지 마세요.

```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

#### 방법 B: 안전한 규칙 (인증된 사용자만)
**권장**: 인증된 사용자만 읽기/쓰기 가능

```json
{
  "rules": {
    "users": {
      "$uid": {
        ".read": "$uid === auth.uid || root.child('users').child(auth.uid).child('is_admin').val() === true",
        ".write": "$uid === auth.uid || root.child('users').child(auth.uid).child('is_admin').val() === true"
      },
      ".read": "auth != null && root.child('users').child(auth.uid).child('is_admin').val() === true",
      ".write": "auth != null && root.child('users').child(auth.uid).child('is_admin').val() === true"
    },
    "payments": {
      ".read": "auth != null && root.child('users').child(auth.uid).child('is_admin').val() === true",
      ".write": "auth != null && root.child('users').child(auth.uid).child('is_admin').val() === true"
    }
  }
}
```

#### 방법 C: 개발용 임시 규칙 (관리자 이메일 확인)
개발 단계에서 사용 가능한 간단한 규칙:

```json
{
  "rules": {
    ".read": true,
    ".write": true,
    ".validate": "newData.hasChildren(['user_id', 'email']) || root.child('users').child(auth.uid).child('is_admin').val() === true"
  }
}
```

### 4. 규칙 적용
1. **"규칙"** 탭 클릭
2. 위 규칙 중 하나를 복사하여 붙여넣기
3. **"게시"** 클릭

## 추천 설정 순서

### 1단계: 개발 초기 (데이터베이스 활성화)
```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```
- 이 규칙으로 데이터베이스가 제대로 작동하는지 확인
- 관리자 정보가 저장되는지 테스트

### 2단계: 데이터 저장 확인 후 (안전한 규칙 적용)
```json
{
  "rules": {
    "users": {
      "$uid": {
        ".read": "$uid === auth.uid || root.child('users').child(auth.uid).child('is_admin').val() === true",
        ".write": "$uid === auth.uid || root.child('users').child(auth.uid).child('is_admin').val() === true"
      },
      ".read": "auth != null && root.child('users').child(auth.uid).child('is_admin').val() === true",
      ".write": "auth != null && root.child('users').child(auth.uid).child('is_admin').val() === true"
    },
    "payments": {
      ".read": "auth != null && root.child('users').child(auth.uid).child('is_admin').val() === true",
      ".write": "auth != null && root.child('users').child(auth.uid).child('is_admin').val() === true"
    }
  }
}
```

## 주의사항
- **방법 A (모든 접근 허용)**는 개발 단계에서만 사용
- 프로덕션 환경에서는 반드시 **방법 B** 또는 더 엄격한 규칙 사용
- 규칙 변경 후 **"게시"**를 클릭해야 적용됩니다

## 문제 해결
- 규칙 적용 후에도 404 오류가 발생하면: 데이터베이스가 제대로 생성되었는지 확인
- 인증 오류가 발생하면: 방법 A로 임시 변경 후 관리자 정보 저장 확인


