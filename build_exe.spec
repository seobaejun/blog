# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec 파일
클라이언트 exe 빌드용 설정
"""

import sys
from pathlib import Path

# 프로젝트 루트 경로
project_root = Path(SPECPATH)

block_cipher = None

# 분석할 파일들
a = Analysis(
    ['src/main.py'],  # 메인 진입점
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # config.json은 포함하지 않음 (별도 배포)
        # 필요한 데이터 파일이 있다면 여기에 추가
    ],
    hiddenimports=[
        'pyrebase4',
        'selenium',
        'webdriver_manager',
        'pyperclip',
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'src.auth_manager',
        'src.firebase_config',
        'src.naver_login',
        'src.blog_search',
        'src.neighbor_add',
        'src.like_post',
        'ui.app_gui',
        'ui.login_window',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'admin_web',  # 관리자 웹은 제외
        'firebase_functions',  # Firebase Functions 제외
        'firebase_hosting',  # Firebase Hosting 제외
        'scripts',  # 스크립트 제외
        'Flask',  # Flask는 클라이언트에서 불필요
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NaverBlogAuto',  # exe 파일 이름
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI 앱이므로 콘솔 창 숨김
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 아이콘 파일이 있다면 경로 지정
)

