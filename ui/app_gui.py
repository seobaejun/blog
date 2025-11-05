"""
네이버 블로그 자동화 프로그램 GUI
기능 구현 없이 레이아웃만 구성
"""
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import sys
from pathlib import Path
import threading

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.naver_login import NaverLogin
from src.blog_search import BlogSearch
from src.neighbor_add import NeighborAdd


class NaverAutoGUI:
    """네이버 블로그 자동화 프로그램 메인 GUI"""
    
    def __init__(self, root):
        """GUI 초기화"""
        self.root = root
        self.root.title("네이버 블로그 자동화 프로그램")
        self.root.geometry("667x533")
        self.root.resizable(True, True)
        
        # 상태 변수
        self.is_running = False
        self.success_count = 0
        self.fail_count = 0
        self.total_work_count = 0  # 전체 작업 수
        self.naver_login = None
        self.blog_search = None
        
        # GUI 생성
        self._create_widgets()
        
    
    def _create_widgets(self):
        """위젯 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 상단: 로그인 섹션과 탭 영역
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        top_frame.columnconfigure(1, weight=1)
        
        # 1. 로그인 섹션 (왼쪽)
        login_frame = ttk.LabelFrame(top_frame, text="로그인", padding="10")
        login_frame.grid(row=0, column=0, sticky=(tk.W, tk.N), padx=(0, 10))
        
        ttk.Label(login_frame, text="아이디:").grid(row=0, column=0, padx=(0, 5), pady=5, sticky=tk.W)
        self.email_entry = ttk.Entry(login_frame, width=25)
        self.email_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(login_frame, text="비밀번호:").grid(row=1, column=0, padx=(0, 5), pady=5, sticky=tk.W)
        self.password_entry = ttk.Entry(login_frame, width=25, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.login_status_label = ttk.Label(login_frame, text="로그인 상태: 미로그인", foreground="red")
        self.login_status_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        # 검색어 입력 섹션 추가
        search_frame = ttk.LabelFrame(login_frame, text="블로그 검색", padding="10")
        search_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="검색어:").grid(row=0, column=0, padx=(0, 5), pady=5, sticky=tk.W)
        self.search_entry = ttk.Entry(search_frame, width=25)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # 2. 탭 영역 (오른쪽)
        tab_frame = ttk.Frame(top_frame)
        tab_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        tab_frame.columnconfigure(0, weight=1)
        tab_frame.rowconfigure(1, weight=1)
        
        # 노트북 (탭 컨테이너)
        self.notebook = ttk.Notebook(tab_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 서로이웃 추가 탭
        neighbor_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(neighbor_tab, text="서로이웃 추가")
        neighbor_tab.columnconfigure(0, weight=1)
        
        neighbor_frame = ttk.Frame(neighbor_tab)
        neighbor_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        neighbor_frame.columnconfigure(0, weight=1)
        
        # 옵션 체크박스
        option_frame = ttk.Frame(neighbor_frame)
        option_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.include_neighbor_var = tk.BooleanVar(value=False)
        self.mutual_only_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(option_frame, text="이웃추가 포함", variable=self.include_neighbor_var).grid(row=0, column=0, padx=5, sticky=tk.W)
        ttk.Checkbutton(option_frame, text="서로이웃만", variable=self.mutual_only_var).grid(row=0, column=1, padx=5, sticky=tk.W)
        
        # 서로이웃 추가 수량 입력
        count_frame = ttk.Frame(neighbor_frame)
        count_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(count_frame, text="서로이웃 추가 수량:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.neighbor_count_entry = ttk.Entry(count_frame, width=10)
        self.neighbor_count_entry.insert(0, "10")  # 기본값 10
        self.neighbor_count_entry.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        # 시작 버튼
        btn_frame = ttk.Frame(neighbor_frame)
        btn_frame.grid(row=2, column=0, pady=10)
        
        ttk.Button(btn_frame, text="서로이웃 추가 시작", command=self._start_neighbor_add, width=20).pack()
        
        # 공감 탭
        like_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(like_tab, text="공감")
        like_tab.columnconfigure(0, weight=1)
        
        like_frame = ttk.Frame(like_tab)
        like_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        like_frame.columnconfigure(1, weight=1)
        
        ttk.Label(like_frame, text="URL 파일:").grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        self.like_url_entry = ttk.Entry(like_frame, width=40)
        self.like_url_entry.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        self.like_url_entry.insert(0, "URL 목록 파일 선택...")
        self.like_url_entry.config(state=tk.DISABLED)
        
        ttk.Button(like_frame, text="파일 선택", command=self._select_like_file).grid(row=0, column=2, padx=5)
        ttk.Button(like_frame, text="시작", command=self._start_like).grid(row=0, column=3, padx=5)
        
        # 댓글 작성 탭
        comment_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(comment_tab, text="댓글 작성")
        comment_tab.columnconfigure(0, weight=1)
        
        comment_frame = ttk.Frame(comment_tab)
        comment_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        comment_frame.columnconfigure(1, weight=1)
        
        ttk.Label(comment_frame, text="URL 파일:").grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        self.comment_url_entry = ttk.Entry(comment_frame, width=40)
        self.comment_url_entry.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        self.comment_url_entry.insert(0, "URL 목록 파일 선택...")
        self.comment_url_entry.config(state=tk.DISABLED)
        
        ttk.Button(comment_frame, text="파일 선택", command=self._select_comment_file).grid(row=0, column=2, padx=5)
        ttk.Button(comment_frame, text="시작", command=self._start_comment).grid(row=0, column=3, padx=5)
        
        # 3. 하단: 작업 제어, 진행상황, 로그 (세로 배치)
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.rowconfigure(2, weight=1)
        
        # 작업 제어 및 진행상황 (가로 배치)
        control_progress_frame = ttk.Frame(bottom_frame)
        control_progress_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        control_progress_frame.columnconfigure(0, weight=1)
        control_progress_frame.columnconfigure(1, weight=1)
        
        # 작업 제어 섹션
        control_frame = ttk.LabelFrame(control_progress_frame, text="작업 제어", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 5))
        control_frame.columnconfigure(0, weight=1)
        
        # 속도 조절
        speed_frame = ttk.Frame(control_frame)
        speed_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        speed_frame.columnconfigure(1, weight=1)
        
        ttk.Label(speed_frame, text="작업 속도 (딜레이):").grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        self.speed_scale = ttk.Scale(speed_frame, from_=5, to=60, orient=tk.HORIZONTAL, length=200)
        self.speed_scale.set(30)  # 기본값 30초
        self.speed_scale.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        self.speed_label = ttk.Label(speed_frame, text="30.0초")
        self.speed_label.grid(row=0, column=2, padx=5)
        self.speed_scale.configure(command=self._update_speed_label)
        
        # 작업 제어 버튼
        btn_frame = ttk.Frame(control_frame)
        btn_frame.grid(row=1, column=0, pady=10)
        
        self.stop_btn = ttk.Button(btn_frame, text="작업 중지", command=self._stop_work, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_btn = ttk.Button(btn_frame, text="일시정지", command=self._pause_work, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        self.resume_btn = ttk.Button(btn_frame, text="재시작", command=self._resume_work, state=tk.DISABLED)
        self.resume_btn.pack(side=tk.LEFT, padx=5)
        
        # 진행상황 표시 섹션
        progress_frame = ttk.LabelFrame(control_progress_frame, text="진행상황", padding="10")
        progress_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N), padx=(5, 0))
        progress_frame.columnconfigure(0, weight=1)
        
        # 성공/실패 카운트
        count_frame = ttk.Frame(progress_frame)
        count_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.success_label = ttk.Label(count_frame, text="성공: 0", foreground="green", font=("Arial", 10, "bold"))
        self.success_label.pack(side=tk.LEFT, padx=10)
        
        self.fail_label = ttk.Label(count_frame, text="실패: 0", foreground="red", font=("Arial", 10, "bold"))
        self.fail_label.pack(side=tk.LEFT, padx=10)
        
        total_count = self.success_count + self.fail_count
        self.total_label = ttk.Label(count_frame, text=f"총 작업: {total_count}", font=("Arial", 10))
        self.total_label.pack(side=tk.LEFT, padx=10)
        
        # 진행률 표시
        self.progress_var = tk.StringVar(value="0%")
        ttk.Label(progress_frame, text="진행률:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        progress_bar_frame = ttk.Frame(progress_frame)
        progress_bar_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        progress_bar_frame.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(progress_bar_frame, mode='determinate', length=200)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.progress_label = ttk.Label(progress_bar_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=1)
        
        # 로그 표시 섹션 (더 넓게)
        log_frame = ttk.LabelFrame(bottom_frame, text="작업 로그", padding="10")
        log_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = ScrolledText(log_frame, height=15, width=100, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.log_text.config(state=tk.DISABLED)
    
    def _log_message(self, message):
        """로그 메시지 추가"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _update_progress(self, success_count, fail_count, total_count):
        """
        진행상황 업데이트
        
        Args:
            success_count: 성공 건수
            fail_count: 실패 건수
            total_count: 전체 작업 수
        """
        self.success_count = success_count
        self.fail_count = fail_count
        self.total_work_count = total_count
        
        # 성공/실패/총 작업 라벨 업데이트
        self.success_label.config(text=f"성공: {success_count}")
        self.fail_label.config(text=f"실패: {fail_count}")
        total = success_count + fail_count
        self.total_label.config(text=f"총 작업: {total} / {total_count}")
        
        # 진행률 계산 및 업데이트
        if total_count > 0:
            progress_percent = int((total / total_count) * 100)
            self.progress_bar['value'] = progress_percent
            self.progress_var.set(f"{progress_percent}%")
        else:
            self.progress_bar['value'] = 0
            self.progress_var.set("0%")
    
    def _reset_progress(self, total_count):
        """
        진행상황 초기화
        
        Args:
            total_count: 전체 작업 수
        """
        self.success_count = 0
        self.fail_count = 0
        self.total_work_count = total_count
        
        self.success_label.config(text="성공: 0")
        self.fail_label.config(text="실패: 0")
        self.total_label.config(text=f"총 작업: 0 / {total_count}")
        
        self.progress_bar['value'] = 0
        self.progress_var.set("0%")
    
    def _handle_logout(self):
        """로그아웃 처리 (기능 미구현)"""
        pass
    
    def _select_neighbor_file(self):
        """서로이웃 추가용 파일 선택 (기능 미구현)"""
        pass
    
    def _select_like_file(self):
        """공감(좋아요) 대상 파일 선택 (기능 미구현)"""
        pass
    
    def _select_comment_file(self):
        """댓글 작성 대상 파일 선택 (기능 미구현)"""
        pass
    
    def _start_neighbor_add(self):
        """서로이웃 추가 시작 (로그인 + 검색 + 서로이웃 추가 통합)"""
        # 입력값 확인
        username = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        search_keyword = self.search_entry.get().strip()
        
        if not username or not password:
            self._log_message("오류: 아이디와 비밀번호를 입력해주세요.")
            return
        
        if not search_keyword:
            self._log_message("오류: 검색어를 입력해주세요.")
            return
        
        # 서로이웃 추가 수량 확인
        try:
            neighbor_count = int(self.neighbor_count_entry.get().strip())
            if neighbor_count <= 0:
                raise ValueError("수량은 1 이상이어야 합니다.")
        except ValueError as e:
            self._log_message(f"오류: 서로이웃 추가 수량을 올바르게 입력해주세요. (1 이상의 숫자)")
            return
        
        # 옵션 읽기
        include_neighbor = self.include_neighbor_var.get()
        mutual_only = self.mutual_only_var.get()
        delay = float(self.speed_scale.get())
        
        self._log_message("통합 작업을 시작합니다 (로그인 → 검색 → 서로이웃 추가)...")
        self._log_message(f"옵션 - 이웃추가 포함: {include_neighbor}, 서로이웃만: {mutual_only}")
        self._log_message(f"서로이웃 추가 수량: {neighbor_count}개")
        
        # 작업 버튼 활성화
        self.stop_btn.config(state=tk.NORMAL)
        self.is_running = True
        
        # 별도 스레드에서 통합 작업 실행
        work_thread = threading.Thread(
            target=self._perform_full_workflow,
            args=(username, password, search_keyword, include_neighbor, mutual_only, delay, neighbor_count),
            daemon=True
        )
        work_thread.start()
    
    def _perform_full_workflow(self, username, password, keyword, include_neighbor, mutual_only, delay, neighbor_count):
        """전체 워크플로우 수행 (로그인 → 검색 → 서로이웃 추가) (별도 스레드)"""
        try:
            # 1. 로그인 수행
            self.root.after(0, lambda: self._log_message("네이버 로그인을 시작합니다..."))
            self.naver_login = NaverLogin()
            self.root.after(0, lambda: self._log_message("브라우저를 시작합니다..."))
            
            login_success = self.naver_login.login(username, password)
            
            if not login_success:
                self.root.after(0, lambda: self._log_message("로그인 실패: 알 수 없는 오류"))
                self.root.after(0, lambda: self.login_status_label.config(text="로그인 상태: 로그인 실패", foreground="red"))
                return
            
            self.root.after(0, lambda: self._log_message("로그인 성공!"))
            self.root.after(0, lambda: self.login_status_label.config(text="로그인 상태: 로그인됨", foreground="green"))
            
            # 2. 검색 수행
            self.root.after(0, lambda: self._log_message(f"검색어 '{keyword}'로 검색을 시작합니다..."))
            search_success = self.naver_login.search_on_section_search(keyword)
            
            if not search_success:
                self.root.after(0, lambda: self._log_message("검색 실패: 알 수 없는 오류"))
                return
            
            self.root.after(0, lambda: self._log_message(f"검색 완료: '{keyword}'"))
            
            # 3. 서로이웃 추가 작업 수행
            self.root.after(0, lambda: self._log_message(f"서로이웃 추가 작업을 시작합니다... (대상: {neighbor_count}개)"))
            
            if not self.naver_login or not self.naver_login.driver:
                self.root.after(0, lambda: self._log_message("오류: 브라우저가 실행되지 않았습니다."))
                return
            
            # 진행상황 초기화
            self.root.after(0, lambda: self._reset_progress(neighbor_count))
            
            # 진행 상황 업데이트를 위한 콜백 함수 정의
            def progress_callback(current_success, current_fail, current_total, max_total):
                """작업 진행 상황 업데이트 콜백"""
                self.root.after(0, lambda: self._update_progress(current_success, current_fail, max_total))
            
            # NeighborAdd 인스턴스 생성
            neighbor_add = NeighborAdd(self.naver_login.driver)
            
            # 작업 시작 (진행 상황 콜백 전달)
            result = neighbor_add.start_neighbor_add_work(
                include_neighbor=include_neighbor,
                mutual_only=mutual_only,
                max_posts=neighbor_count,  # 사용자가 입력한 수량만큼 처리
                delay=delay,
                progress_callback=progress_callback
            )
            
            # 최종 결과 업데이트
            if result['success']:
                self.root.after(0, lambda: self._update_progress(
                    result['success_count'], 
                    result['fail_count'], 
                    result['total']
                ))
                self.root.after(0, lambda: self._log_message(f"작업 완료: 총 {result['total']}개"))
                self.root.after(0, lambda: self._log_message(f"성공: {result['success_count']}개 (서로이웃: {result.get('mutual_count', 0)}개, 일반이웃: {result.get('neighbor_count', 0)}개)"))
                self.root.after(0, lambda: self._log_message(f"실패: {result['fail_count']}개"))
            else:
                self.root.after(0, lambda: self._log_message(f"작업 실패: {result['message']}"))
        
        except Exception as e:
            self.root.after(0, lambda: self._log_message(f"오류 발생: {str(e)}"))
            self.root.after(0, lambda: self.login_status_label.config(text="로그인 상태: 오류 발생", foreground="red"))
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
    
    def _start_like(self):
        """공감(좋아요) 시작 (기능 미구현)"""
        pass
    
    def _start_comment(self):
        """댓글 작성 시작 (기능 미구현)"""
        pass
    
    def _stop_work(self):
        """작업 중지 (기능 미구현)"""
        pass
    
    def _pause_work(self):
        """작업 일시정지 (기능 미구현)"""
        pass
    
    def _resume_work(self):
        """작업 재시작 (기능 미구현)"""
        pass
    
    def _update_speed_label(self, value):
        """속도 슬라이더 레이블 업데이트"""
        speed = float(value)
        if speed >= 60:
            self.speed_label.config(text="60.0초 (1분)")
        else:
            self.speed_label.config(text=f"{speed:.1f}초")
    


def run_gui():
    """GUI 실행"""
    root = tk.Tk()
    app = NaverAutoGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
