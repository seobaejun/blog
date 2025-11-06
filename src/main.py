"""
네이버 블로그 자동화 프로그램 메인 진입점
"""
import sys
from pathlib import Path
import tkinter as tk

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ui.login_window import show_login_window
from ui.app_gui import run_gui
from src.auth_manager import AuthManager


def on_login_success():
    """로그인 성공 시 메인 화면 실행"""
    run_gui()


if __name__ == "__main__":
    # 항상 로그인 화면부터 표시
    show_login_window(on_login_success)
