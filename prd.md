# 🧩 네이버 블로그 자동화 프로그램 PRD

## 1. 프로젝트 개요

**프로젝트명:**  
네이버 블로그 자동 상호이웃 & 공감·댓글 자동화 프로그램  

**개발도구:**  
- Python 3.11+  
- Cursor AI (자동 코드 생성 및 보조 개발)  
- Firebase Authentication (로그인 인증 관리)  
- Firebase Firestore (데이터 저장 및 로그 관리)  
- Selenium 또는 Playwright (웹 자동화 엔진)  
- PyInstaller (실행파일 빌드용)

**목표:**  
반복적인 블로그 운영 업무를 자동화하여  
- **서로이웃추가**,  
- **공감(좋아요)**,  
- **댓글 작성**  
을 효율적으로 수행할 수 있는 개인용 프로그램 제작.

---

## 2. 주요 기능

### ✅ 사용자 인증 및 회원가입 시스템
- **회원가입**
  - Firebase Authentication을 이용한 이메일·비밀번호 회원가입
  - 회원가입 시 사용자 정보를 Firestore에 저장
  - 회원가입 직후에는 `approved: false` 상태로 설정
  - 관리자 승인 전까지는 로그인 불가

- **로그인 및 인증**
  - Firebase Authentication을 이용한 사용자 로그인
  - 로그인 시 관리자 승인 상태 확인 (`approved: true` 필수)
  - 승인되지 않은 사용자는 로그인 차단 및 안내 메시지 표시
  - 로그인 후 세션 토큰을 로컬에 저장하여 자동 로그인 유지
  - 첫 로그인 날짜 기록 (`first_login_date`)

### ✅ 이용 기간 관리 시스템
- **30일 이용 기간 관리**
  - 첫 로그인 날짜(`first_login_date`)부터 30일간 이용 가능
  - 이용 기간은 `expiry_date = first_login_date + 30일`로 계산
  - 프로그램 실행 시마다 이용 기간 확인
  - 이용 기간 만료 시 자동으로 결제 알림 창 표시

- **결제 및 연장 시스템**
  - 이용 기간 만료 시 결제 안내 다이얼로그 표시
  - 사용자는 결제 정보를 관리자에게 전달
  - 관리자 페이지에서 결제 확인 후 `expiry_date`를 30일 연장
  - 결제 확인 시 `last_payment_date` 업데이트

### ✅ 관리자 페이지 (웹 기반)
- **관리자 인증**
  - 별도의 관리자 계정으로 로그인
  - 관리자 권한 확인 (`is_admin: true`)

- **회원 관리**
  - 회원가입 대기 목록 표시 (`approved: false`)
  - 회원 승인/거부 기능
  - 승인 시 `approved: true`로 변경

- **결제 관리**
  - 결제 대기 목록 표시 (`payment_pending: true`)
  - 결제 확인 후 `expiry_date`를 30일 연장
  - 결제 내역 기록 및 관리

- **사용자 목록 및 통계**
  - 전체 사용자 목록 조회
  - 사용자별 이용 기간 상태 확인
  - 사용자 활동 로그 확인

### ✅ 자동화 기능
1. **서로이웃추가**
   - 대상 블로그 URL 목록 불러오기
   - 자동 방문 → 프로필 클릭 → "서로이웃 요청"
   - 랜덤 메시지로 이웃신청 문구 자동 입력
2. **공감(좋아요)**
   - 포스팅 URL 또는 RSS 기반으로 목록 수집
   - "공감" 버튼 자동 클릭 (이미 눌린 글은 스킵)
3. **댓글 작성**
   - 사전에 Firestore에 저장된 댓글 문장 Pool에서 랜덤 선택
   - 특정 키워드 기반 맞춤형 댓글 작성
   - 중복 댓글 방지 로직 포함

### ✅ Firebase 연동 (데이터 구조)
- `users` 컬렉션: 사용자 정보 저장
  ```json
  {
    "user_id": "firebase_uid",
    "email": "user@example.com",
    "approved": false,  // 관리자 승인 여부
    "is_admin": false,  // 관리자 여부
    "first_login_date": "2024-01-01T00:00:00",  // 첫 로그인 날짜
    "expiry_date": "2024-01-31T23:59:59",  // 이용 만료일
    "last_payment_date": null,  // 마지막 결제 확인일
    "payment_pending": false,  // 결제 대기 여부
    "created_at": "2024-01-01T00:00:00",  // 회원가입일
    "login_history": []  // 로그인 기록
  }
  ```
- `tasks` 컬렉션: 작업 로그(성공/실패, 시간, 대상URL) 저장  
- `comments` 컬렉션: 댓글 템플릿 데이터 관리
- `payments` 컬렉션: 결제 내역 관리
  ```json
  {
    "user_id": "firebase_uid",
    "payment_date": "2024-01-15T00:00:00",
    "amount": 10000,
    "status": "confirmed",  // pending, confirmed, rejected
    "confirmed_by": "admin_uid",
    "confirmed_at": "2024-01-15T10:00:00"
  }
  ```

### ✅ 작업 제어 및 로그
- 진행상황 실시간 표시 (성공/실패 카운트)
- 작업 중지/재시작 버튼
- 속도 조절 슬라이더 (랜덤 3~7초 딜레이)
- Firestore에 모든 작업 로그 자동 업로드

---

## 3. 시스템 구조

```plaintext
📁 project_root
 ┣ 📂 src
 ┃ ┣ main.py
 ┃ ┣ firebase_config.py
 ┃ ┣ auth_manager.py          # 인증 관리 (회원가입, 로그인, 승인 확인)
 ┃ ┣ subscription_manager.py   # 이용 기간 관리 (30일 체크, 만료 알림)
 ┃ ┣ naver_login.py
 ┃ ┣ blog_search.py
 ┃ ┣ neighbor_add.py
 ┃ ┣ like_post.py
 ┃ ┗ comment_post.py
 ┣ 📂 ui
 ┃ ┣ app_gui.py               # 메인 GUI (로그인 화면 포함)
 ┃ ┣ login_window.py          # 로그인/회원가입 창
 ┃ ┗ payment_dialog.py        # 결제 알림 다이얼로그
 ┣ 📂 admin_web                # 관리자 페이지 (웹)
 ┃ ┣ app.py                   # Flask/FastAPI 서버
 ┃ ┣ templates/               # HTML 템플릿
 ┃ ┃ ┣ login.html
 ┃ ┃ ┣ dashboard.html
 ┃ ┃ ┣ users.html
 ┃ ┃ ┣ payments.html
 ┃ ┣ static/                  # CSS, JS 파일
 ┃ ┗ requirements.txt
 ┣ 📂 data
 ┃ ┣ cookies.json
 ┃ ┗ session.json
 ┣ requirements.txt
 ┗ config.json
```

## 4. 구현 방법 및 기술 스택

### 4.1 클라이언트 프로그램 (Python GUI)

#### 4.1.1 회원가입 및 로그인 화면
- **구현 위치**: `ui/login_window.py`
- **기능**:
  - 회원가입 폼 (이메일, 비밀번호, 비밀번호 확인)
  - 로그인 폼 (이메일, 비밀번호)
  - Firebase Authentication으로 회원가입/로그인 처리
  - 회원가입 시 Firestore에 사용자 정보 저장
  - 승인 상태 확인 후 메인 화면 진입

#### 4.1.2 이용 기간 관리 모듈
- **구현 위치**: `src/subscription_manager.py`
- **주요 함수**:
  ```python
  class SubscriptionManager:
      def check_subscription_status(self, user_id) -> dict
      def is_subscription_active(self, user_id) -> bool
      def get_remaining_days(self, user_id) -> int
      def show_payment_dialog(self) -> None
  ```
- **로직**:
  1. 프로그램 시작 시 `check_subscription_status()` 호출
  2. `expiry_date`와 현재 날짜 비교
  3. 만료 시 `show_payment_dialog()` 호출
  4. 결제 대기 상태로 `payment_pending: true` 설정

#### 4.1.3 메인 프로그램 진입점 수정
- **구현 위치**: `src/main.py`, `ui/app_gui.py`
- **변경 사항**:
  - 프로그램 시작 시 로그인 화면 먼저 표시
  - 로그인 성공 후 이용 기간 확인
  - 이용 기간 만료 시 결제 다이얼로그 표시 후 프로그램 종료
  - 모든 조건 통과 시 메인 화면 표시

### 4.2 관리자 페이지 (웹 애플리케이션)

#### 4.2.1 기술 스택 선택
- **옵션 1: Flask (Python) - 추천**
  - 장점: 기존 Python 코드베이스와 통합 용이
  - 단점: 프론트엔드 개발 필요
  - 프레임워크: Flask + Jinja2 템플릿

- **옵션 2: FastAPI (Python)**
  - 장점: RESTful API, 자동 문서화
  - 단점: 별도 프론트엔드 필요 (React/Vue 등)
  - 프레임워크: FastAPI + React

- **옵션 3: Firebase Hosting + HTML/JS**
  - 장점: Firebase 통합, 빠른 배포
  - 단점: 서버 로직 제한적
  - 프레임워크: 순수 JavaScript + Firebase SDK

#### 4.2.2 관리자 페이지 구조 (Flask 기반)
- **구현 위치**: `admin_web/app.py`
- **주요 라우트**:
  ```python
  /admin/login              # 관리자 로그인
  /admin/dashboard          # 대시보드
  /admin/users              # 회원 목록
  /admin/users/approve/<uid> # 회원 승인
  /admin/payments            # 결제 대기 목록
  /admin/payments/confirm/<uid> # 결제 확인
  ```

#### 4.2.3 관리자 인증
- Firebase Authentication으로 관리자 계정 로그인
- Firestore에서 `is_admin: true` 확인
- 세션 관리 (Flask-Session 또는 JWT)

#### 4.2.4 회원 승인 기능
- Firestore 쿼리: `users` 컬렉션에서 `approved: false` 조회
- 승인 버튼 클릭 시 `approved: true` 업데이트
- 실시간 업데이트를 위해 Firestore 리스너 사용 (선택사항)

#### 4.2.5 결제 확인 기능
- Firestore 쿼리: `users` 컬렉션에서 `payment_pending: true` 조회
- 결제 확인 시:
  1. `expiry_date`를 현재 날짜 + 30일로 업데이트
  2. `payment_pending: false`로 변경
  3. `last_payment_date` 업데이트
  4. `payments` 컬렉션에 결제 내역 기록

### 4.3 Firebase 데이터베이스 구조

#### 4.3.1 Firestore 보안 규칙
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 사용자는 자신의 정보만 읽기 가능
    match /users/{userId} {
      allow read: if request.auth != null && request.auth.uid == userId;
      allow write: if false; // 클라이언트에서 직접 수정 불가
    }
    
    // 관리자는 모든 사용자 정보 읽기/쓰기 가능
    match /users/{userId} {
      allow read, write: if get(/databases/$(database)/documents/users/$(request.auth.uid)).data.is_admin == true;
    }
  }
}
```

#### 4.3.2 데이터베이스 초기화
- 관리자 계정을 Firebase Console에서 수동 생성
- Firestore에 관리자 문서 생성:
  ```json
  {
    "user_id": "admin_firebase_uid",
    "email": "admin@example.com",
    "is_admin": true,
    "approved": true
  }
  ```

### 4.4 구현 순서

#### Phase 1: 회원가입 및 로그인 시스템
1. ✅ `ui/login_window.py` 생성 (회원가입/로그인 UI)
2. ✅ `src/auth_manager.py` 수정 (승인 상태 확인 로직 추가)
3. ✅ `src/main.py` 수정 (로그인 화면 먼저 표시)
4. ✅ Firestore 데이터 구조 설계 및 테스트

#### Phase 2: 이용 기간 관리 시스템
1. ✅ `src/subscription_manager.py` 생성
2. ✅ `ui/payment_dialog.py` 생성 (결제 알림 다이얼로그)
3. ✅ `ui/app_gui.py` 수정 (프로그램 시작 시 이용 기간 확인)
4. ✅ 첫 로그인 날짜 기록 로직 구현

#### Phase 3: 관리자 페이지 개발
1. ✅ `admin_web/app.py` 생성 (Flask 서버)
2. ✅ `admin_web/templates/` 디렉토리 생성 및 HTML 템플릿 작성
3. ✅ 관리자 인증 로직 구현
4. ✅ 회원 승인 기능 구현
5. ✅ 결제 확인 기능 구현
6. ✅ 배포 및 테스트

#### Phase 4: 통합 테스트 및 최적화
1. ✅ 전체 시스템 통합 테스트
2. ✅ 에러 핸들링 개선
3. ✅ 보안 검토 및 개선
4. ✅ 사용자 문서 작성

## 5. 데이터 흐름도

### 5.1 회원가입 흐름
```
사용자 → 회원가입 폼 입력 → Firebase Auth 회원가입
  → Firestore에 사용자 정보 저장 (approved: false)
  → "관리자 승인 대기 중" 메시지 표시
```

### 5.2 로그인 흐름
```
사용자 → 로그인 폼 입력 → Firebase Auth 로그인
  → Firestore에서 승인 상태 확인
  → 승인되지 않음: "관리자 승인 대기 중" 메시지
  → 승인됨: 이용 기간 확인
    → 만료: 결제 다이얼로그 표시
    → 유효: 메인 화면 진입
```

### 5.3 결제 연장 흐름
```
사용자 → 이용 기간 만료 → 결제 다이얼로그 표시
  → 결제 정보를 관리자에게 전달
  → 관리자 페이지에서 결제 확인
  → Firestore 업데이트 (expiry_date + 30일)
  → 사용자 재로그인 시 이용 가능
```

## 6. 보안 고려사항

1. **Firebase 보안 규칙**: Firestore 보안 규칙을 적절히 설정하여 무단 접근 방지
2. **관리자 권한**: 관리자 계정은 수동으로만 생성하고 보안 강화
3. **세션 관리**: 관리자 페이지 세션 타임아웃 설정
4. **HTTPS**: 관리자 페이지는 반드시 HTTPS로 배포
5. **입력 검증**: 모든 사용자 입력값 검증 및 sanitization

## 7. 배포 방법

### 7.1 관리자 페이지 배포
- **옵션 1: Firebase Hosting** (추천)
  - Firebase CLI로 배포
  - 자동 HTTPS 지원
  - 무료 티어 제공

- **옵션 2: Heroku/Vercel**
  - Flask/FastAPI 앱 배포
  - 환경 변수로 Firebase 설정 관리

- **옵션 3: 로컬 서버**
  - 내부 네트워크에서만 접근
  - 포트 포워딩 설정

### 7.2 클라이언트 프로그램 배포
- PyInstaller로 실행 파일 생성
- 사용자에게 배포 및 설치 가이드 제공
