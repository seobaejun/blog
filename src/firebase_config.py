"""
Firebase 설정 및 초기화 모듈
"""
import json
from pathlib import Path
import pyrebase4


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
        """config.json에서 Firebase 설정 로드"""
        config_path = Path(__file__).parent.parent / "config.json"
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            
            if "firebase" not in config_data:
                raise ValueError("Firebase 설정이 config.json에 없습니다.")
            
            self.config = config_data["firebase"]
            
            # databaseURL이 없으면 자동 생성
            if "databaseURL" not in self.config:
                project_id = self.config.get("projectId")
                if project_id:
                    self.config["databaseURL"] = f"https://{project_id}-default-rtdb.firebaseio.com"
        
        except FileNotFoundError:
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"config.json 파일이 올바른 JSON 형식이 아닙니다.")
    
    def _initialize_firebase(self):
        """Firebase 초기화"""
        try:
            self.firebase = pyrebase4.initialize_app(self.config)
            self.auth = self.firebase.auth()
            self.db = self.firebase.database()
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
            raise RuntimeError("Firebase가 초기화되지 않았습니다.")
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

