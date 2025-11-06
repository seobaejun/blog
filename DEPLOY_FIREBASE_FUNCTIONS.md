# Firebase Functions 배포 가이드

## 배포 준비

### 1. Firebase CLI 설치 및 로그인

```bash
# Node.js가 설치되어 있어야 합니다
npm install -g firebase-tools

# Firebase 로그인
firebase login
```

### 2. 프로젝트 확인

```bash
# 프로젝트 설정 확인
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

### 4. Functions URL 확인

배포 후 Firebase Console에서 Functions URL을 확인하세요:
- Firebase Console > Functions > 함수 목록
- 또는 `firebase functions:list` 명령어 사용

## Functions 구조

```
firebase_functions/
├── main.py          # Flask 앱 엔트리 포인트
├── requirements.txt # Python 의존성
└── .gcloudignore    # 업로드 제외 파일
```

## 주의사항

1. **환경 변수**: Firebase Functions에서 환경 변수를 사용하려면:
   ```bash
   firebase functions:config:set secret.key="your-secret-key"
   ```

2. **의존성**: `requirements.txt`에 모든 의존성이 포함되어 있어야 합니다.

3. **런타임**: Python 3.11 사용 (firebase.json에서 설정)

4. **메모리 및 타임아웃**: Functions 설정에서 조정 가능

## 트러블슈팅

### Functions 배포 실패 시

1. Python 버전 확인: Python 3.11 필요
2. 의존성 확인: `requirements.txt` 확인
3. 로그 확인: `firebase functions:log`

### Import 오류 시

- `sys.path` 설정 확인
- 프로젝트 루트 경로 확인
- 상대 경로 vs 절대 경로 확인

## Functions URL 사용

배포 후 Functions URL은 다음과 같은 형식입니다:
```
https://asia-northeast1-blog-cdc9b.cloudfunctions.net/app
```

이 URL을 관리자 페이지에서 사용하거나, Firebase Hosting에서 프록시할 수 있습니다.


