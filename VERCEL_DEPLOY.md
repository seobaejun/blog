# Vercel 배포 가이드

## 배포 준비

### 1. Vercel CLI 설치

```bash
npm install -g vercel
```

### 2. Vercel 로그인

```bash
vercel login
```

### 3. 배포

```bash
# 프로젝트 루트에서 실행
vercel

# 프로덕션 배포
vercel --prod
```

## 배포 구조

```
프로젝트/
├── api/
│   └── index.py          # Vercel 서버리스 함수 엔트리 포인트
├── admin_web/
│   └── app.py            # Flask 애플리케이션
├── src/                  # 소스 코드
├── vercel.json           # Vercel 설정
└── requirements.txt      # Python 의존성
```

## 환경 변수 설정

Vercel 대시보드에서 환경 변수를 설정하세요:

1. https://vercel.com/dashboard 접속
2. 프로젝트 선택
3. Settings > Environment Variables
4. 필요한 환경 변수 추가

### 주요 환경 변수

- `FLASK_ENV=production`
- Firebase 설정 관련 환경 변수 (필요시)

## 주의사항

1. **세션 관리**: Vercel은 서버리스 환경이므로 세션을 외부 저장소(Redis 등)에 저장해야 할 수 있습니다.

2. **파일 업로드**: 임시 파일은 Vercel의 제한된 저장 공간을 사용하므로 주의가 필요합니다.

3. **타임아웃**: Vercel의 서버리스 함수는 실행 시간 제한이 있습니다 (Hobby 플랜: 10초, Pro: 60초).

## 배포 확인

배포 후 Vercel이 제공하는 URL을 확인하세요:

```bash
vercel ls
```

또는 Vercel 대시보드에서 확인할 수 있습니다.

