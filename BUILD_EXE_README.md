# exe 파일 빌드 가이드

## 빌드 방법

### 1. 의존성 설치

```bash
pip install -r requirements_client.txt
pip install pyinstaller
```

### 2. exe 빌드

```bash
build_exe.bat
```

또는 직접 실행:

```bash
pyinstaller build_exe.spec --clean
```

### 3. 빌드 결과

- `dist/NaverBlogAuto.exe` - 실행 파일
- `build/` - 빌드 임시 파일 (삭제 가능)

## 배포 방법

### 필수 파일

1. **NaverBlogAuto.exe** - 메인 실행 파일
2. **config.json** - Firebase 설정 파일 (exe와 같은 폴더에 배치)

### config.json 생성

`config.json.example` 파일을 참고하여 `config.json` 파일을 생성하세요.

**중요**: 
- `config.json`에는 실제 Firebase 설정 값이 들어갑니다
- 이 파일은 exe에 포함되지 않으며, 별도로 배포해야 합니다
- 고객에게 배포할 때는 실제 Firebase 설정 값이 포함된 `config.json`을 함께 제공해야 합니다

### 배포 구조

```
배포 폴더/
├── NaverBlogAuto.exe
└── config.json
```

## 보안 주의사항

1. **config.json은 exe에 포함되지 않습니다**
   - Firebase API 키는 exe 파일에 하드코딩되지 않습니다
   - 런타임에 `config.json` 파일을 읽어서 사용합니다

2. **config.json 파일 보호**
   - 고객에게 배포할 때는 실제 Firebase 설정이 포함된 `config.json`을 제공해야 합니다
   - 이 파일은 민감한 정보를 포함하므로 안전하게 관리하세요

3. **Firebase 보안 규칙**
   - Firebase Database/Firestore 보안 규칙을 적절히 설정하여 무단 접근을 방지하세요

## 문제 해결

### exe 실행 시 오류 발생

1. **"config.json을 찾을 수 없습니다"**
   - exe 파일과 같은 폴더에 `config.json` 파일이 있는지 확인하세요

2. **"Firebase 초기화 실패"**
   - `config.json`의 Firebase 설정 값이 올바른지 확인하세요
   - 인터넷 연결을 확인하세요

3. **"모듈을 찾을 수 없습니다"**
   - `requirements_client.txt`의 모든 의존성이 설치되었는지 확인하세요
   - PyInstaller를 최신 버전으로 업데이트하세요: `pip install --upgrade pyinstaller`

## 빌드 옵션 수정

`build_exe.spec` 파일을 수정하여 빌드 옵션을 변경할 수 있습니다:

- `console=False` → `console=True`: 콘솔 창 표시 (디버깅용)
- `name='NaverBlogAuto'`: exe 파일 이름 변경
- `icon=None`: 아이콘 파일 경로 지정 (예: `icon='icon.ico'`)

