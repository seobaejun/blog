# Realtime Database 완전 차단 - 규칙 설정 방법

## 방법: Realtime Database 규칙으로 쓰기 완전 차단

### 단계별 가이드

1. **Firebase Console 접속**
   - https://console.firebase.google.com/
   - 프로젝트 `blog-cdc9b` 선택

2. **Realtime Database 규칙 설정**
   - 왼쪽 메뉴에서 **"Realtime Database"** 클릭
   - 상단 탭에서 **"규칙"** 클릭

3. **규칙 입력**
   - 기존 규칙을 모두 삭제하고 다음 규칙 입력:
   ```json
   {
     "rules": {
       ".read": false,
       ".write": false
     }
   }
   ```

4. **게시**
   - **"게시"** 버튼 클릭 (반드시!)
   - 확인 메시지에서 **"게시"** 다시 클릭

5. **완료 확인**
   - 규칙이 저장되었는지 확인
   - 이제 아무도 Realtime Database에 쓸 수 없음

## 결과

- ✅ Realtime Database에 데이터 저장 불가능
- ✅ 모든 데이터는 Firestore에만 저장됨
- ✅ 코드는 이미 Firestore만 사용하도록 수정됨

## 참고

- 규칙을 설정하면 즉시 적용됩니다
- Realtime Database를 삭제할 필요 없이 규칙만으로 차단 가능합니다
- Firestore는 별도의 데이터베이스이므로 영향 없습니다

