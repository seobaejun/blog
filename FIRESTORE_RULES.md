# Firestore 보안 규칙 설정 가이드

## 관리자 사용자를 Firestore에 저장하기 위한 규칙

Firebase Console에서 Firestore Database > 규칙 탭으로 이동하여 다음 규칙을 설정하세요:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // users 컬렉션 규칙
    match /users/{userId} {
      // 읽기: 인증된 사용자는 자신의 데이터를 읽을 수 있음
      allow read: if request.auth != null && (
        request.auth.token.email == resource.data.email ||
        resource.data.is_admin == true
      );
      
      // 쓰기: 인증된 사용자는 자신의 데이터를 쓸 수 있음
      // 또는 관리자는 모든 사용자 데이터를 쓸 수 있음
      allow write: if request.auth != null && (
        request.auth.token.email == resource.data.email ||
        request.auth.uid == resource.data.user_id ||
        get(/databases/$(database)/documents/users/$(request.auth.token.email)).data.is_admin == true
      );
      
      // 새 문서 생성: 인증된 사용자는 자신의 데이터를 생성할 수 있음
      allow create: if request.auth != null && (
        request.auth.token.email == request.resource.data.email ||
        request.resource.data.is_admin == true
      );
    }
    
    // 임시로 모든 읽기/쓰기 허용 (개발용)
    // 프로덕션에서는 위의 규칙을 사용하세요
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

## 간단한 규칙 (개발/테스트용)

개발 중이거나 테스트를 위해 임시로 모든 인증된 사용자에게 읽기/쓰기 권한을 부여하려면:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

## 설정 방법

1. Firebase Console 접속: https://console.firebase.google.com/
2. 프로젝트 'blog-cdc9b' 선택
3. 왼쪽 메뉴에서 **Firestore Database** 클릭
4. **규칙** 탭 클릭
5. 위의 규칙 중 하나를 복사하여 붙여넣기
6. **게시** 버튼 클릭

## 참고

- 규칙을 변경하면 즉시 적용됩니다
- 개발 중에는 간단한 규칙을 사용하고, 프로덕션에서는 보안 규칙을 강화하세요


