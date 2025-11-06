"""
로그인 및 회원가입 창
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.auth_manager import AuthManager

# 현대적인 스타일 설정
STYLE_CONFIG = {
    "bg_color": "#f5f5f5",
    "primary_color": "#007bff",
    "primary_hover": "#0056b3",
    "success_color": "#28a745",
    "text_color": "#333333",
    "entry_bg": "#ffffff",
    "font_family": "맑은 고딕",
    "font_size": 10
}


class LoginWindow:
    """로그인 및 회원가입 창 클래스"""
    
    def __init__(self, root, on_login_success=None):
        """
        로그인 창 초기화
        
        Args:
            root: Tkinter 루트 윈도우
            on_login_success: 로그인 성공 시 호출할 콜백 함수
        """
        self.root = root
        self.root.title("네이버 블로그 자동화 프로그램")
        self.root.geometry("420x580")
        self.root.resizable(False, False)
        self.root.configure(bg=STYLE_CONFIG["bg_color"])
        
        # 로그인 성공 콜백
        self.on_login_success = on_login_success
        
        # 인증 관리자 초기화
        self.auth_manager = AuthManager()
        
        # GUI 생성
        self._create_widgets()
        
        # 중앙 정렬
        self._center_window()
    
    def _center_window(self):
        """창을 화면 중앙에 배치"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_widgets(self):
        """위젯 생성"""
        # 메인 프레임
        main_frame = tk.Frame(self.root, bg=STYLE_CONFIG["bg_color"], padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 타이틀
        title_label = tk.Label(
            main_frame, 
            text="네이버 블로그 자동화 프로그램", 
            font=(STYLE_CONFIG["font_family"], 15, "bold"),
            bg=STYLE_CONFIG["bg_color"],
            fg=STYLE_CONFIG["text_color"]
        )
        title_label.pack(pady=(0, 12))
        
        # 탭 노트북 생성
        style = ttk.Style()
        style.theme_use('clam')
        
        # 탭 스타일 설정
        style.configure("TNotebook", background=STYLE_CONFIG["bg_color"], borderwidth=0)
        style.configure("TNotebook.Tab", 
                       padding=[15, 8],
                       font=(STYLE_CONFIG["font_family"], 10, "bold"),
                       background="#e0e0e0",
                       foreground=STYLE_CONFIG["text_color"])
        style.map("TNotebook.Tab",
                 background=[("selected", STYLE_CONFIG["primary_color"])],
                 foreground=[("selected", "white")],
                 expand=[("selected", [1, 1, 1, 0])])
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 0))
        
        # 로그인 탭
        login_frame = tk.Frame(self.notebook, bg=STYLE_CONFIG["bg_color"], padx=15, pady=15)
        self.notebook.add(login_frame, text="로그인")
        self._create_login_form(login_frame)
        
        # 회원가입 탭
        signup_frame = tk.Frame(self.notebook, bg=STYLE_CONFIG["bg_color"], padx=15, pady=12)
        self.notebook.add(signup_frame, text="회원가입")
        self._create_signup_form(signup_frame)
    
    def _create_login_form(self, parent):
        """로그인 폼 생성"""
        # 이메일 입력
        email_frame = tk.Frame(parent, bg=STYLE_CONFIG["bg_color"])
        email_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(email_frame, text="이메일", 
                font=(STYLE_CONFIG["font_family"], 9),
                bg=STYLE_CONFIG["bg_color"],
                fg=STYLE_CONFIG["text_color"]).pack(anchor=tk.W, pady=(0, 3))
        
        self.login_email_entry = tk.Entry(
            email_frame, 
            width=35,
            font=(STYLE_CONFIG["font_family"], 10),
            bg=STYLE_CONFIG["entry_bg"],
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightbackground="#ccc",
            highlightcolor=STYLE_CONFIG["primary_color"]
        )
        self.login_email_entry.pack(fill=tk.X, ipady=6)
        
        # 비밀번호 입력
        password_frame = tk.Frame(parent, bg=STYLE_CONFIG["bg_color"])
        password_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(password_frame, text="비밀번호",
                font=(STYLE_CONFIG["font_family"], 9),
                bg=STYLE_CONFIG["bg_color"],
                fg=STYLE_CONFIG["text_color"]).pack(anchor=tk.W, pady=(0, 3))
        
        self.login_password_entry = tk.Entry(
            password_frame, 
            width=35,
            font=(STYLE_CONFIG["font_family"], 10),
            show="*",
            bg=STYLE_CONFIG["entry_bg"],
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightbackground="#ccc",
            highlightcolor=STYLE_CONFIG["primary_color"]
        )
        self.login_password_entry.pack(fill=tk.X, ipady=6)
        
        # 로그인 버튼
        login_btn = tk.Button(
            parent,
            text="로그인",
            command=self._handle_login,
            font=(STYLE_CONFIG["font_family"], 11, "bold"),
            bg=STYLE_CONFIG["primary_color"],
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=10,
            activebackground=STYLE_CONFIG["primary_hover"],
            activeforeground="white"
        )
        login_btn.pack(fill=tk.X, pady=(5, 0))
        
        # Enter 키 바인딩
        self.login_password_entry.bind("<Return>", lambda e: self._handle_login())
        self.login_email_entry.bind("<Return>", lambda e: self.login_password_entry.focus())
    
    def _create_signup_form(self, parent):
        """회원가입 폼 생성"""
        def _create_input_field(parent_frame, label_text):
            """입력 필드 생성 헬퍼 함수"""
            frame = tk.Frame(parent_frame, bg=STYLE_CONFIG["bg_color"])
            frame.pack(fill=tk.X, pady=(0, 7))
            
            tk.Label(frame, text=label_text,
                    font=(STYLE_CONFIG["font_family"], 9),
                    bg=STYLE_CONFIG["bg_color"],
                    fg=STYLE_CONFIG["text_color"]).pack(anchor=tk.W, pady=(0, 3))
            
            entry = tk.Entry(
                frame,
                width=35,
                font=(STYLE_CONFIG["font_family"], 10),
                bg=STYLE_CONFIG["entry_bg"],
                relief=tk.FLAT,
                bd=1,
                highlightthickness=1,
                highlightbackground="#ccc",
                highlightcolor=STYLE_CONFIG["primary_color"]
            )
            entry.pack(fill=tk.X, ipady=5)
            return entry
        
        # 이름 입력
        self.signup_name_entry = _create_input_field(parent, "이름")
        
        # 이메일 입력 (아이디로도 사용)
        self.signup_email_entry = _create_input_field(parent, "이메일 (아이디)")
        
        # 비밀번호 입력
        self.signup_password_entry = _create_input_field(parent, "비밀번호")
        self.signup_password_entry.config(show="*")
        
        # 비밀번호 확인 입력
        self.signup_password_confirm_entry = _create_input_field(parent, "비밀번호 확인")
        self.signup_password_confirm_entry.config(show="*")
        
        # 전화번호 입력
        self.signup_phone_entry = _create_input_field(parent, "전화번호")
        
        # 회원가입 버튼
        signup_btn = tk.Button(
            parent,
            text="회원가입",
            command=self._handle_signup,
            font=(STYLE_CONFIG["font_family"], 11, "bold"),
            bg=STYLE_CONFIG["success_color"],
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=12,
            activebackground="#218838",
            activeforeground="white"
        )
        signup_btn.pack(fill=tk.X, pady=(12, 8))
        
        # Enter 키 바인딩
        self.signup_phone_entry.bind("<Return>", lambda e: self._handle_signup())
    
    def _handle_login(self):
        """로그인 처리"""
        email = self.login_email_entry.get().strip()
        password = self.login_password_entry.get().strip()
        
        # 입력 검증
        if not email:
            messagebox.showerror("오류", "이메일을 입력해주세요.")
            return
        
        if not password:
            messagebox.showerror("오류", "비밀번호를 입력해주세요.")
            return
        
        try:
            # 로그인 시도
            result = self.auth_manager.login(email, password)
            
            if result.get("success"):
                # 로그인 창을 먼저 닫고 작업창 표시
                self.root.destroy()
                if self.on_login_success:
                    self.on_login_success()
        
        except Exception as e:
            error_message = str(e)
            # 이용만료일 체크
            if error_message == "EXPIRY_DATE_EXPIRED":
                # 이용만료 안내 팝업
                expiry_message = (
                    "이용 기간이 만료되었습니다.\n\n"
                    "부스트웹 3333-32-0313102 카카오뱅크\n"
                    "9,900원을 입금하시면 30일 연장됩니다.\n\n"
                    "입금 후 관리자에게 문의해주세요."
                )
                messagebox.showwarning("이용 기간 만료", expiry_message)
            else:
                messagebox.showerror("로그인 실패", error_message)
    
    def _handle_signup(self):
        """회원가입 처리"""
        name = self.signup_name_entry.get().strip()
        email = self.signup_email_entry.get().strip()
        password = self.signup_password_entry.get().strip()
        password_confirm = self.signup_password_confirm_entry.get().strip()
        phone = self.signup_phone_entry.get().strip()
        
        # 입력 검증
        if not name:
            messagebox.showerror("오류", "이름을 입력해주세요.")
            return
        
        if not email:
            messagebox.showerror("오류", "이메일을 입력해주세요.")
            return
        
        # 이메일 형식 검증
        if "@" not in email or "." not in email:
            messagebox.showerror("오류", "올바른 이메일 형식을 입력해주세요.")
            return
        
        # 아이디는 이메일과 동일하게 사용
        username = email
        
        if not password:
            messagebox.showerror("오류", "비밀번호를 입력해주세요.")
            return
        
        if password != password_confirm:
            messagebox.showerror("오류", "비밀번호가 일치하지 않습니다.")
            return
        
        if len(password) < 6:
            messagebox.showerror("오류", "비밀번호는 6자 이상이어야 합니다.")
            return
        
        if not phone:
            messagebox.showerror("오류", "전화번호를 입력해주세요.")
            return
        
        try:
            # 회원가입 시도
            print(f"\n{'='*60}")
            print(f"[GUI] 회원가입 시도")
            print(f"  이름: {name}")
            print(f"  이메일: {email}")
            print(f"  사용자명: {username}")
            print(f"  전화번호: {phone}")
            print(f"{'='*60}\n")
            
            result = self.auth_manager.signup(name, username, email, password, phone)
            
            print(f"\n[GUI] 회원가입 결과:")
            print(f"  Success: {result.get('success')}")
            print(f"  Message: {result.get('message')}")
            print(f"  User ID: {result.get('user_id')}\n")
            
            if result.get("success"):
                # Firestore 저장 확인
                try:
                    import requests
                    user_id = result.get('user_id')
                    if user_id:
                        # Firestore에서 확인
                        project_id = "blog-cdc9b"
                        firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users/{user_id}"
                        
                        # 토큰 가져오기 (회원가입 후 토큰)
                        token = self.auth_manager.token
                        if token:
                            headers = {
                                "Authorization": f"Bearer {token}",
                                "Content-Type": "application/json"
                            }
                            verify_response = requests.get(firestore_url, headers=headers, timeout=5)
                            if verify_response.status_code == 200:
                                saved_doc = verify_response.json()
                                if saved_doc and "fields" in saved_doc:
                                    saved_email = saved_doc["fields"].get("email", {}).get("stringValue", "")
                                    print(f"[GUI] ✓ Firestore 저장 확인 성공!")
                                    print(f"  저장된 이메일: {saved_email}")
                                else:
                                    print(f"[GUI] ⚠ Firestore에 데이터가 없습니다!")
                            else:
                                print(f"[GUI] ⚠ Firestore 확인 실패: HTTP {verify_response.status_code}")
                        else:
                            print(f"[GUI] ⚠ 토큰이 없어 확인할 수 없습니다.")
                except Exception as verify_error:
                    print(f"[GUI] ⚠ 저장 확인 중 오류: {str(verify_error)}")
                
                messagebox.showinfo(
                    "회원가입 완료", 
                    f"{result.get('message', '회원가입이 완료되었습니다.')}\n\n"
                    f"User ID: {result.get('user_id', 'N/A')}\n"
                    f"관리자 승인 후 로그인할 수 있습니다."
                )
                # 로그인 탭으로 전환
                self.notebook.select(0)
            else:
                messagebox.showerror("회원가입 실패", result.get("message", "회원가입에 실패했습니다."))
        
        except Exception as e:
            import traceback
            error_msg = str(e)
            print(f"\n[GUI] ❌ 회원가입 오류:")
            print(f"  {error_msg}")
            traceback.print_exc()
            messagebox.showerror("회원가입 실패", f"회원가입 중 오류가 발생했습니다:\n\n{error_msg}")


def show_login_window(on_login_success=None):
    """
    로그인 창 표시
    
    Args:
        on_login_success: 로그인 성공 시 호출할 콜백 함수
    
    Returns:
        bool: 로그인 성공 여부
    """
    root = tk.Tk()
    app = LoginWindow(root, on_login_success)
    root.mainloop()


if __name__ == "__main__":
    show_login_window()
