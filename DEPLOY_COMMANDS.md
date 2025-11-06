# Firebase Functions 배포 명령어

## 배포 방법

### 방법 1: 배포 스크립트 사용 (권장)

```bash
# Windows
deploy.bat

# 또는 직접 실행
.\deploy.bat
```

### 방법 2: 수동 배포

#### 1단계: Firebase 로그인

```bash
firebase login
```

브라우저가 열리면 Google 계정으로 로그인하세요.

#### 2단계: 프로젝트 설정

```bash
firebase use blog-cdc9b
```

#### 3단계: Functions 배포

```bash
firebase deploy --only functions
```

## 배포 확인

배포가 완료되면 Functions URL을 확인할 수 있습니다:

```bash
firebase functions:list
```

또는 Firebase Console에서:
1. https://console.firebase.google.com/ 접속
2. 프로젝트 'blog-cdc9b' 선택
3. Functions 메뉴 클릭
4. 함수 목록에서 URL 확인

## Functions URL 형식

```
https://asia-northeast1-blog-cdc9b.cloudfunctions.net/app
```

이 URL을 통해 관리자 페이지에 접근할 수 있습니다.

## 트러블슈팅

### Firebase CLI가 없을 때

```bash
npm install -g firebase-tools
```

### 로그인 실패 시

```bash
firebase login --no-localhost
```

### 프로젝트를 찾을 수 없을 때

```bash
firebase projects:list
firebase use <프로젝트ID>
```


