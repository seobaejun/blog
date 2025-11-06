# Firebase Functions 배포 가이드

## 배포 준비

### 1. Firebase CLI 설치 (Node.js 필요)

```bash
# Node.js 설치 확인
node --version
npm --version

# Firebase CLI 설치
npm install -g firebase-tools

# Firebase 로그인
firebase login
```

### 2. 프로젝트 초기화 확인

```bash
# 프로젝트 확인
firebase use blog-cdc9b

# 현재 프로젝트 확인
firebase projects:list
```

### 3. Functions 배포

```bash
# Functions만 배포
firebase deploy --only functions

# 또는 전체 배포 (Hosting + Functions)
firebase deploy
```

## 배포 후 확인

### Functions URL 확인

배포가 완료되면 다음 명령어로 Functions URL을 확인할 수 있습니다:

```bash
firebase functions:list
```

또는 Firebase Console에서:
- Firebase Console > Functions > 함수 목록
- Functions URL 형식: `https://asia-northeast1-blog-cdc9b.cloudfunctions.net/app`

### Functions 접근

Firebase Functions는 Flask 앱을 호스팅하므로 모든 라우트가 동일하게 작동합니다:
- `/` - 메인 페이지
- `/login` - 로그인 페이지
- `/dashboard` - 대시보드
- `/users` - 회원 관리
- `/payments` - 결제 관리

## Firebase Hosting과 연결 (선택사항)

Firebase Hosting에서 Functions로 프록시하려면 `firebase.json`의 rewrites를 수정:

```json
{
  "hosting": {
    "rewrites": [
      {
        "source": "/api/**",
        "function": "app"
      },
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
```

## 트러블슈팅

### Python 버전 오류

Firebase Functions는 Python 3.11을 사용합니다. 로컬에서 Python 3.11이 설치되어 있는지 확인하세요.

### 의존성 오류

`requirements.txt`에 모든 필요한 패키지가 포함되어 있는지 확인하세요.

### Import 오류

Functions에서 프로젝트 구조를 인식할 수 있도록 `sys.path`가 올바르게 설정되어 있는지 확인하세요.

## 환경 변수 설정

Firebase Functions에서 환경 변수를 사용하려면:

```bash
# 환경 변수 설정
firebase functions:config:set secret.key="your-secret-key"

# 환경 변수 확인
firebase functions:config:get

# 배포 후 적용
firebase deploy --only functions
```

코드에서 사용:
```python
import os
secret_key = os.environ.get('secret.key', 'default-key')
```

## 로그 확인

```bash
# Functions 로그 확인
firebase functions:log

# 실시간 로그
firebase functions:log --only app
```


