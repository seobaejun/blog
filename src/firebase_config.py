"""
Firebase 설정 및 초기화 모듈
"""
import json
import sys
from pathlib import Path
import pyrebase


class FirebaseConfig:
    """Firebase 설정 및 초기화 클래스"""
    
    def __init__(self):
        """Firebase 설정 로드 및 초기화"""
        self.config = None
        self.firebase = None
        self.auth = None
        self.db = None
        self._load_config()
        self._initialize_firebase()
    
    def _load_config(self):
        """환경 변수 또는 config.json에서 Firebase 설정 로드"""
        import os
        
        # 환경 변수에서 Firebase 설정 로드 시도
        firebase_config = {}
        env_keys = {
            'apiKey': 'FIREBASE_API_KEY',
            'authDomain': 'FIREBASE_AUTH_DOMAIN',
            'projectId': 'FIREBASE_PROJECT_ID',
            'storageBucket': 'FIREBASE_STORAGE_BUCKET',
            'messagingSenderId': 'FIREBASE_MESSAGING_SENDER_ID',
            'appId': 'FIREBASE_APP_ID',
            'measurementId': 'FIREBASE_MEASUREMENT_ID',
        }
        
        # 환경 변수에서 모든 값이 있는지 확인
        env_available = all(os.getenv(key) for key in env_keys.values())
        
        if env_available:
            # 환경 변수에서 로드
            for config_key, env_key in env_keys.items():
                value = os.getenv(env_key)
                if value:
                    firebase_config[config_key] = value
            self.config = firebase_config
            print("✓ Firebase 설정을 환경 변수에서 로드했습니다.")
        else:
            # config.json에서 로드
            # exe로 빌드된 경우와 일반 실행 모두 지원
            if getattr(sys, 'frozen', False):
                # PyInstaller로 빌드된 경우
                exe_dir = Path(sys.executable).parent
                config_path = exe_dir / "config.json"
            else:
                # 일반 Python 실행
                config_path = Path(__file__).parent.parent / "config.json"
            
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                
                if "firebase" not in config_data:
                    raise ValueError("Firebase 설정이 config.json에 없습니다.")
                
                self.config = config_data["firebase"]
                print("✓ Firebase 설정을 config.json에서 로드했습니다.")
            except FileNotFoundError:
                raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}\n설정 파일을 exe와 같은 폴더에 배치해주세요.")
            except json.JSONDecodeError:
                raise ValueError(f"config.json 파일이 올바른 JSON 형식이 아닙니다.")
        
        # databaseURL이 없으면 자동으로 추가 (Realtime Database 사용)
        if "databaseURL" not in self.config:
            # projectId를 사용하여 databaseURL 생성
            project_id = self.config.get("projectId", "blog-cdc9b")
            self.config["databaseURL"] = f"https://{project_id}-default-rtdb.firebaseio.com"
            print(f"✓ databaseURL이 자동으로 추가되었습니다: {self.config['databaseURL']}")
    
    def _initialize_firebase(self):
        """Firebase 초기화 (Realtime Database 사용)"""
        try:
            # config 복사본 생성 (원본 수정 방지)
            init_config = self.config.copy()
            
            # databaseURL이 없으면 자동으로 추가
            if "databaseURL" not in init_config:
                project_id = init_config.get("projectId", "blog-cdc9b")
                init_config["databaseURL"] = f"https://{project_id}-default-rtdb.firebaseio.com"
                print(f"✓ databaseURL이 자동으로 추가되었습니다: {init_config['databaseURL']}")
            
            self.firebase = pyrebase.initialize_app(init_config)
            self.auth = self.firebase.auth()
            self.db = self.firebase.database()
            
            print("✓ Firebase 초기화 완료 (Auth + Realtime Database)")
        except Exception as e:
            raise RuntimeError(f"Firebase 초기화 실패: {str(e)}")
    
    def get_auth(self):
        """Firebase Auth 인스턴스 반환"""
        if self.auth is None:
            raise RuntimeError("Firebase가 초기화되지 않았습니다.")
        return self.auth
    
    def get_db(self):
        """Firebase Database 인스턴스 반환"""
        if self.db is None:
            raise RuntimeError("Firebase Database가 초기화되지 않았습니다.")
        return self.db


# 전역 Firebase 인스턴스
_firebase_instance = None


def get_firebase():
    """Firebase 설정 인스턴스 싱글톤 반환"""
    global _firebase_instance
    if _firebase_instance is None:
        _firebase_instance = FirebaseConfig()
    return _firebase_instance


def get_auth():
    """Firebase Auth 인스턴스 반환"""
    return get_firebase().get_auth()


def get_db():
    """Firebase Database 인스턴스 반환"""
    return get_firebase().get_db()

