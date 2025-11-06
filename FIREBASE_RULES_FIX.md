# Firebase Realtime Database 규칙 오류 해결

## 문제
규칙 저장 시 다음 오류 발생:
```
규칙 저장 오류 - Line 1: mismatched input '{' expecting ('function', 'import', 'service', 'rules_version')
```

## 원인
Firebase Realtime Database 규칙은 JSON 형식이지만, 올바른 구조를 따라야 합니다.

## 해결 방법

### Firebase Console에서 다음 규칙을 복사하여 붙여넣기:

```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

### 단계별 가이드:

1. **Firebase Console 접속**
   - https://console.firebase.google.com/
   - 프로젝트 `blog-cdc9b` 선택

2. **Realtime Database로 이동**
   - 왼쪽 메뉴에서 "Realtime Database" 클릭

3. **규칙 탭 클릭**
   - 상단의 "규칙" 탭 클릭

4. **기존 내용 모두 삭제**
   - 편집기에서 모든 내용 삭제

5. **다음 규칙 복사하여 붙여넣기:**
   ```json
   {
     "rules": {
       ".read": true,
       ".write": true
     }
   }
   ```

6. **게시 버튼 클릭**
   - 오른쪽 상단의 "게시" 버튼 클릭
   - 규칙이 저장됩니다

## 주의사항

- 규칙은 반드시 `{ "rules": { ... } }` 형식이어야 합니다
- 첫 번째 줄에 `{`만 있으면 안 됩니다
- `rules` 키가 반드시 있어야 합니다
- `.read`와 `.write`는 문자열이 아닌 `true`/`false` 값이어야 합니다

## 규칙 확인

규칙이 올바르게 저장되었는지 확인:
- 규칙 탭에서 규칙이 표시되는지 확인
- 오류 메시지가 없는지 확인
- "게시됨" 상태인지 확인


