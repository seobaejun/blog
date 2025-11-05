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

### ✅ 로그인 및 인증
- Firebase Authentication을 이용한 사용자 로그인
- 이메일·비밀번호 또는 Google 계정 로그인 지원
- 로그인 후 세션 토큰을 로컬에 저장하여 자동 로그인 유지

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

### ✅ Firebase 연동
- `users` 컬렉션: 사용자 정보, 로그인 기록 저장  
- `tasks` 컬렉션: 작업 로그(성공/실패, 시간, 대상URL) 저장  
- `comments` 컬렉션: 댓글 템플릿 데이터 관리  

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
 ┃ ┣ auth_manager.py
 ┃ ┣ naver_auto.py
 ┃ ┣ neighbor_add.py
 ┃ ┣ like_post.py
 ┃ ┣ comment_post.py
 ┃ ┗ utils.py
 ┣ 📂 ui
 ┃ ┗ app_gui.py
 ┣ 📂 data
 ┃ ┗ cookies.json
 ┣ requirements.txt
 ┗ config.json
