# Firebase 규칙 저장 오류 해결 방법

## 문제
규칙 저장 시 다음 오류 발생:
```
Line 1: mismatched input '{' expecting ('function', 'import', 'service', 'rules_version')
```

## 원인
이 오류는 **Firestore Security Rules** 형식 오류입니다. 
Realtime Database 규칙 탭을 사용해야 합니다.

## 해결 방법

### 1단계: 올바른 탭 확인
- Firebase Console → **Realtime Database** (Firestore가 아님!)
- 왼쪽 메뉴에서 "Realtime Database" 클릭
- 상단의 **"규칙"** 탭 클릭 (반드시 Realtime Database의 규칙 탭)

### 2단계: 규칙 입력
규칙 편집기에 **정확히** 다음을 복사하여 붙여넣기:

```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

### 3단계: 주의사항
- **첫 줄부터 시작** (빈 줄 없이)
- **전체를 한 번에 복사** (줄번호 제외)
- **중괄호와 따옴표 정확히** 입력
- **마지막 줄 뒤에 빈 줄 없이**

### 4단계: 게시
- 오른쪽 상단 **"게시"** 버튼 클릭

## 만약 여전히 오류가 발생하면

### 대안 1: 규칙 편집기에서 직접 타이핑
1. 기존 내용 모두 삭제
2. 다음을 직접 타이핑:
   ```
   { 엔터
     "rules": { 엔터
       ".read": true, 엔터
       ".write": true 엔터
     } 엔터
   }
   ```

### 대안 2: 브라우저 개발자 도구 확인
1. F12 키 누르기
2. Console 탭 확인
3. 오류 메시지 확인

### 대안 3: 다른 브라우저 시도
- Chrome, Firefox, Edge 등 다른 브라우저에서 시도

## 확인 방법
규칙이 올바르게 저장되었는지 확인:
- 규칙 탭에서 규칙이 표시되는지 확인
- 오류 메시지가 없는지 확인
- "게시됨" 상태인지 확인


