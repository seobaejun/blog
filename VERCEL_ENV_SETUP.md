# Vercel 환경 변수 설정 가이드

## 필요한 환경 변수

Vercel 대시보드에서 다음 환경 변수들을 설정해야 합니다:

### 1. Flask 설정

```
FLASK_ENV=production
FLASK_SECRET_KEY=yqU7Qsxdvef9dUqVO7NY71m2UpkM39byrGUEvJq2Me4
```

**중요**: `FLASK_SECRET_KEY`는 반드시 강력한 랜덤 문자열로 설정하세요!

**SECRET_KEY 생성 방법**:
- Python으로 생성: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- 또는 온라인 랜덤 문자열 생성기 사용
- **절대 공개 저장소에 실제 키를 커밋하지 마세요!**

### 2. Firebase 설정 (필수)

**중요**: 환경 변수를 설정하지 않으면 `config.json` 파일을 사용하지만, Vercel에서는 환경 변수 사용을 권장합니다.

```
FIREBASE_API_KEY=AIzaSyBnttw13ZLjQy4KWEDY3KVi3GTBUqeXOyo
FIREBASE_AUTH_DOMAIN=blog-cdc9b.firebaseapp.com
FIREBASE_PROJECT_ID=blog-cdc9b
FIREBASE_STORAGE_BUCKET=blog-cdc9b.firebasestorage.app
FIREBASE_MESSAGING_SENDER_ID=1025951916921
FIREBASE_APP_ID=1:1025951916921:web:7ecf732013c947810045a8
FIREBASE_MEASUREMENT_ID=G-R1VMNHG7WL
FIREBASE_DATABASE_URL=https://blog-cdc9b-default-rtdb.firebaseio.com
```

**참고**: 환경 변수가 모두 설정되어 있으면 환경 변수를 우선 사용하고, 없으면 `config.json` 파일을 사용합니다.

## 설정 방법

1. Vercel 대시보드 접속: https://vercel.com/dashboard
2. 프로젝트 선택
3. **Settings** > **Environment Variables** 메뉴 클릭
4. 위의 환경 변수들을 하나씩 추가:
   - **Name**: 환경 변수 이름 (예: `FLASK_SECRET_KEY`)
   - **Value**: 환경 변수 값
   - **Environment**: Production, Preview, Development 모두 선택 (또는 Production만)
5. **Save** 클릭

## 주의사항

- `FLASK_SECRET_KEY`는 보안을 위해 반드시 강력한 랜덤 문자열로 설정하세요
- 환경 변수는 Production, Preview, Development 환경별로 다르게 설정할 수 있습니다
- 환경 변수 변경 후에는 재배포가 필요합니다

## 로컬 개발용 .env 파일

로컬 개발 시 `.env.example` 파일을 복사하여 `.env` 파일을 만들고 값을 설정하세요:

```bash
cp .env.example .env
```

`.env` 파일은 Git에 커밋하지 마세요! (이미 .gitignore에 포함되어 있습니다)

