"""
네이버 블로그 자동화 프로그램 메인 진입점
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ui.app_gui import run_gui


if __name__ == "__main__":
    run_gui()
