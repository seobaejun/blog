"""
Firebase Hosting 배포를 위한 디렉토리 구조 생성
"""
import os
import shutil
from pathlib import Path

def setup_firebase_hosting():
    """Firebase Hosting 디렉토리 구조 생성"""
    project_root = Path(__file__).parent.parent
    admin_web_dir = project_root / "admin_web"
    hosting_dir = project_root / "firebase_hosting"
    
    # firebase_hosting 디렉토리 생성
    hosting_dir.mkdir(exist_ok=True)
    
    # 정적 파일 복사
    static_src = admin_web_dir / "static"
    static_dst = hosting_dir / "static"
    
    if static_src.exists():
        if static_dst.exists():
            shutil.rmtree(static_dst)
        shutil.copytree(static_src, static_dst)
        print(f"✓ 정적 파일 복사 완료: {static_dst}")
    
    # index.html 생성 (리다이렉트용)
    index_html = hosting_dir / "index.html"
    if not index_html.exists():
        index_html.write_text("""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>관리자 페이지</title>
    <meta http-equiv="refresh" content="0; url=/login.html">
</head>
<body>
    <p>리다이렉트 중...</p>
    <script>
        window.location.href = '/login.html';
    </script>
</body>
</html>""", encoding="utf-8")
        print(f"✓ index.html 생성 완료")
    
    # 템플릿 파일을 HTML로 변환 (기본 구조만)
    templates_dir = admin_web_dir / "templates"
    if templates_dir.exists():
        for template_file in templates_dir.glob("*.html"):
            # login.html은 직접 복사 가능
            if template_file.name == "login.html":
                dst_file = hosting_dir / template_file.name
                shutil.copy2(template_file, dst_file)
                print(f"✓ {template_file.name} 복사 완료")
    
    print("\n" + "=" * 60)
    print("Firebase Hosting 디렉토리 구조 생성 완료!")
    print("=" * 60)
    print(f"\n디렉토리: {hosting_dir}")
    print("\n다음 단계:")
    print("1. Node.js 설치 확인: node --version")
    print("2. Firebase CLI 설치: npm install -g firebase-tools")
    print("3. Firebase 로그인: firebase login")
    print("4. 프로젝트 확인: firebase use blog-cdc9b")
    print("5. 배포: firebase deploy --only hosting")
    print("\n주의: Flask 백엔드는 Firebase Functions로 별도 배포 필요")

if __name__ == "__main__":
    setup_firebase_hosting()


