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
        
        # databaseURL 제거 (Realtime Database는 사용하지 않음)
        if "databaseURL" in self.config:
            # Realtime Database URL 제거 (Firestore만 사용)
            del self.config["databaseURL"]
            print("⚠ databaseURL이 제거되었습니다. Realtime Database는 사용하지 않습니다.")
    
    def _initialize_firebase(self):
        """Firebase 초기화 (Realtime Database는 완전히 차단)"""
        try:
            # databaseURL이 없으면 pyrebase가 Realtime Database를 초기화하지 않음
            # Firestore는 REST API로 직접 사용하므로 pyrebase 초기화는 Auth만 필요
            
            # config 복사본 생성 (원본 수정 방지)
            init_config = self.config.copy()
            
            # databaseURL이 있으면 제거 (혹시 모를 경우 대비)
            if "databaseURL" in init_config:
                del init_config["databaseURL"]
                print("⚠ databaseURL이 제거되었습니다.")
            
            self.firebase = pyrebase.initialize_app(init_config)
            self.auth = self.firebase.auth()
            
            # Realtime Database는 절대 초기화하지 않음
            # self.db = self.firebase.database()  # 완전히 제거됨
            self.db = None
            
            print("✓ Firebase 초기화 완료 (Auth만 사용)")
            print("⚠ Realtime Database는 완전히 차단되었습니다.")
            print("   모든 데이터는 Firestore에만 저장됩니다.")
        except KeyError as e:
            if "databaseURL" in str(e):
                # databaseURL이 없어서 발생한 오류는 정상 (의도된 동작)
                # config에서 databaseURL을 제거하고 다시 시도
                init_config = self.config.copy()
                if "databaseURL" in init_config:
                    del init_config["databaseURL"]
                self.firebase = pyrebase.initialize_app(init_config)
                self.auth = self.firebase.auth()
                self.db = None
                print("✓ Firebase 초기화 완료 (databaseURL 제거 후 재시도)")
            else:
                raise RuntimeError(f"Firebase 초기화 실패: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Firebase 초기화 실패: {str(e)}")
    
    def get_auth(self):
        """Firebase Auth 인스턴스 반환"""
        if self.auth is None:
            raise RuntimeError("Firebase가 초기화되지 않았습니다.")
        return self.auth
    
    def get_db(self):
        """Firebase Database 인스턴스 반환 (더 이상 사용하지 않음)"""
        # Realtime Database는 더 이상 사용하지 않음
        raise RuntimeError("Realtime Database는 더 이상 사용하지 않습니다. Firestore를 사용하세요.")


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

