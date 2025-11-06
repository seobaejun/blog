# 관리자 페이지

블로그 자동화 프로그램의 관리자 페이지입니다.

## 기능

- **관리자 로그인**: 관리자 계정으로 로그인
- **대시보드**: 전체 통계 및 요약 정보
- **회원 관리**: 회원 목록 조회 및 승인
- **결제 관리**: 결제 대기 목록 및 결제 내역 관리

## 설치 방법

1. 의존성 설치:
```bash
cd admin_web
pip install -r requirements.txt
```

2. 관리자 계정 생성:
   - Firebase Console에서 관리자 계정을 생성
   - Firestore에서 해당 사용자 문서에 `is_admin: true` 설정

## 실행 방법

```bash
cd admin_web
python app.py
```

서버가 시작되면 브라우저에서 `http://localhost:5000`으로 접속하세요.

## 프로덕션 배포

### Flask 서버 실행 옵션

프로덕션 환경에서는 다음 명령어로 실행하는 것을 권장합니다:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 환경 변수 설정

프로덕션 환경에서는 `app.secret_key`를 환경 변수로 관리하세요:

```python
import os
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key')
```

## 주요 라우트

- `/` - 메인 페이지 (대시보드로 리다이렉트)
- `/login` - 관리자 로그인
- `/dashboard` - 대시보드
- `/users` - 회원 목록 및 관리
- `/payments` - 결제 관리
- `/users/approve/<user_id>` - 회원 승인 (POST)
- `/payments/confirm/<user_id>` - 결제 확인 (POST)

## 보안 고려사항

1. **시크릿 키**: 프로덕션 환경에서는 반드시 강력한 시크릿 키를 사용하세요.
2. **HTTPS**: 프로덕션 환경에서는 HTTPS를 사용하세요.
3. **방화벽**: 관리자 페이지는 관리자만 접근할 수 있도록 방화벽 설정을 권장합니다.
4. **세션 타임아웃**: 필요시 세션 타임아웃을 설정하세요.

