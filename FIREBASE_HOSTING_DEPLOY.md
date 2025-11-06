# Firebase Hosting 배포 가이드

## 배포 방법

Firebase Hosting은 정적 웹사이트를 호스팅하는 서비스입니다. 현재 Flask 애플리케이션을 배포하려면 다음 중 하나의 방법을 선택해야 합니다:

### 방법 1: Firebase Hosting + Firebase Functions (권장)

Flask 애플리케이션을 Firebase Functions로 변환하여 배포합니다.

#### 1. Firebase CLI 설치

```bash
npm install -g firebase-tools
firebase login
```

#### 2. Firebase Functions 설정

1. `firebase_functions` 디렉토리 생성
2. Flask 애플리케이션을 Functions로 변환
3. `firebase.json` 파일에서 Functions 설정 확인

#### 3. 정적 파일 준비

관리자 페이지의 정적 파일(HTML, CSS, JS)을 `firebase_hosting` 디렉토리에 복사

#### 4. 배포

```bash
firebase deploy --only hosting
firebase deploy --only functions
```

### 방법 2: Cloud Run 배포 (대안)

Flask 애플리케이션을 Google Cloud Run에 배포하고, 정적 파일만 Firebase Hosting에 배포할 수 있습니다.

#### 1. Cloud Run 배포

```bash
gcloud run deploy admin-web \
  --source admin_web \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated
```

#### 2. Firebase Hosting에서 Cloud Run 프록시

`firebase.json`에 rewrites 규칙 추가:

```json
{
  "hosting": {
    "rewrites": [
      {
        "source": "/api/**",
        "run": {
          "serviceId": "admin-web",
          "region": "asia-northeast1"
        }
      }
    ]
  }
}
```

### 방법 3: 완전한 정적 사이트로 변환

관리자 페이지를 완전한 클라이언트 사이드 애플리케이션으로 변환 (Firebase SDK 사용)

## 현재 권장 방법

관리자 페이지는 서버 사이드 로직이 필요하므로, **방법 1 (Firebase Hosting + Firebase Functions)**을 권장합니다.

### 배포 단계

1. Firebase CLI 설치 및 로그인
2. 프로젝트 초기화 확인
3. Functions 코드 작성
4. Hosting 파일 준비
5. 배포 실행

## 참고

- Firebase Hosting은 정적 파일만 호스팅 가능
- Flask 세션은 Functions에서 처리해야 함
- Firebase Authentication을 사용하여 인증 처리


