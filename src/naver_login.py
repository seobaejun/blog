"""
네이버 로그인 모듈
Selenium을 사용하여 네이버 로그인 수행
"""
import time
import os
import sys
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class NaverLogin:
    """네이버 로그인 클래스"""
    
    NAVER_LOGIN_URL = "https://nid.naver.com/nidlogin.login?realname=Y&type=modal&svctype=262144&returl=https%3A%2F%2Fmy.naver.com"
    
    def __init__(self):
        """네이버 로그인 초기화"""
        self.driver = None
        self.is_logged_in = False
    
    def start_browser(self, headless=False):
        """
        브라우저 시작
        
        Args:
            headless: 헤드리스 모드 여부 (기본값: False)
        """
        options = Options()
        
        # 자동화 탐지 회피 설정들
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 봇 탐지 회피를 위한 추가 Chrome 옵션
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--start-maximized")
        
        # User-Agent 설정
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
        
        # ChromeDriver 경로 찾기
        chromedriver_path = None
        
        # 1. EXE와 같은 디렉토리에서 chromedriver.exe 찾기
        if getattr(sys, 'frozen', False):
            # EXE로 빌드된 경우
            exe_dir = os.path.dirname(sys.executable)
            chromedriver_path = os.path.join(exe_dir, "chromedriver.exe")
            if not os.path.exists(chromedriver_path):
                chromedriver_path = None
        else:
            # Python 스크립트로 실행된 경우
            script_dir = os.path.dirname(os.path.abspath(__file__))
            chromedriver_path = os.path.join(script_dir, "chromedriver.exe")
            if not os.path.exists(chromedriver_path):
                chromedriver_path = None
        
        # 2. ChromeDriver 자동 설치 시도 (webdriver_manager 사용)
        if not chromedriver_path:
            try:
                print("ChromeDriver 자동 다운로드 시도 중...")
                chromedriver_path = ChromeDriverManager().install()
                print(f"ChromeDriver 다운로드 완료: {chromedriver_path}")
            except Exception as e:
                print(f"⚠ ChromeDriver 자동 다운로드 실패: {str(e)}")
                raise Exception(
                    "ChromeDriver를 찾을 수 없습니다.\n\n"
                    "해결 방법:\n"
                    "1. Chrome 브라우저가 설치되어 있는지 확인하세요.\n"
                    "2. 프로그램과 같은 폴더에 'chromedriver.exe' 파일을 배치하세요.\n"
                    "3. 인터넷 연결을 확인하고 다시 시도하세요.\n"
                    f"\n오류 상세: {str(e)}"
                )
        
        # ChromeDriver 서비스 설정
        try:
            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            error_msg = str(e)
            if "session not created" in error_msg.lower() or "chrome instance exited" in error_msg.lower():
                raise Exception(
                    "Chrome 브라우저를 시작할 수 없습니다.\n\n"
                    "가능한 원인:\n"
                    "1. Chrome 브라우저가 설치되어 있지 않습니다.\n"
                    "2. Chrome 브라우저 버전과 ChromeDriver 버전이 맞지 않습니다.\n"
                    "3. 다른 Chrome 프로세스가 실행 중입니다.\n"
                    "4. Chrome 브라우저가 손상되었습니다.\n\n"
                    "해결 방법:\n"
                    "1. Chrome 브라우저를 최신 버전으로 업데이트하세요.\n"
                    "2. 실행 중인 모든 Chrome 창을 닫고 다시 시도하세요.\n"
                    "3. 컴퓨터를 재시작한 후 다시 시도하세요.\n"
                    f"\n오류 상세: {error_msg}"
                )
            else:
                raise Exception(f"브라우저 시작 실패: {error_msg}")
        
        # webdriver 속성 제거 (JavaScript 실행)
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                window.chrome = {
                    runtime: {}
                };
            '''
        })
    
    def close_browser(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def login(self, username, password):
        """
        네이버 로그인 수행
        
        Args:
            username: 네이버 아이디
            password: 네이버 비밀번호
        
        Returns:
            bool: 로그인 성공 여부
        
        Raises:
            Exception: 로그인 실패 시
        """
        try:
            # 브라우저 시작
            self.start_browser(headless=False)
            
            # 네이버 로그인 페이지 이동
            self.driver.get(self.NAVER_LOGIN_URL)
            time.sleep(2)  # 페이지 로딩 대기
            
            # 아이디 입력 필드 찾기 및 클릭
            id_input = self.driver.find_element(By.ID, "id")
            id_input.click()
            time.sleep(0.5)
            
            # 클립보드 복사 후 붙여넣기 (Ctrl+V)
            pyperclip.copy(username)
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(5)  # 아이디 입력 후 5초 대기
            
            # 비밀번호 입력 필드 찾기 및 클릭
            pw_input = self.driver.find_element(By.ID, "pw")
            pw_input.click()
            time.sleep(0.5)
            
            # 클립보드 복사 후 붙여넣기 (Ctrl+V)
            pyperclip.copy(password)
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(5)  # 비밀번호 입력 후 5초 대기
            
            # 로그인 버튼 클릭
            try:
                login_btn = self.driver.find_element(By.ID, "log.login")
                login_btn.click()
            except:
                # 대체 방법: submit_btn 사용
                try:
                    login_btn = self.driver.find_element(By.ID, "submit_btn")
                    login_btn.click()
                except:
                    # Enter 키로 대체
                    pw_input.send_keys(Keys.RETURN)
            
            time.sleep(3)  # 로그인 완료 대기
            
            # "새로운 기기 등록" 팝업 처리 (있는 경우)
            try:
                cancel_btn = self.driver.find_element(By.CSS_SELECTOR, "span.btn_cancel")
                cancel_btn.click()
                time.sleep(2)
            except:
                pass
            
            # 로그인 완료 후 블로그 검색 페이지로 바로 이동
            blog_url = "https://m.blog.naver.com/SectionSearch.naver"
            self.driver.get(blog_url)
            time.sleep(3)  # 페이지 로딩 대기
            
            self.is_logged_in = True
            return True
        
        except Exception as e:
            self.is_logged_in = False
            raise Exception(f"로그인 중 오류 발생: {str(e)}")
    
    def check_login_status(self):
        """로그인 상태 확인 (테스트용 - 미구현)"""
        return self.is_logged_in
    
    def search_on_section_search(self, keyword):
        """
        SectionSearch 페이지에서 검색어 입력 및 검색 수행
        
        Args:
            keyword: 검색어
        
        Returns:
            bool: 검색 성공 여부
        """
        try:
            if not self.driver:
                raise Exception("브라우저가 실행되지 않았습니다. 먼저 로그인을 수행해주세요.")
            
            # 현재 URL 확인
            current_url = self.driver.current_url
            if "SectionSearch" not in current_url:
                # SectionSearch 페이지로 이동
                self.driver.get("https://m.blog.naver.com/SectionSearch.naver")
                time.sleep(3)  # 페이지 로딩 대기
            
            # 검색 입력 필드 찾기
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            
            # 여러 선택자로 검색 입력 필드 찾기
            search_input_selectors = [
                (By.ID, "query"),
                (By.NAME, "query"),
                (By.CSS_SELECTOR, "input[type='text'][placeholder*='검색']"),
                (By.CSS_SELECTOR, "input[type='search']"),
                (By.CSS_SELECTOR, "input[type='text']"),
                (By.CLASS_NAME, "search_input"),
                (By.ID, "searchInput"),
            ]
            
            search_input = None
            for by, selector in search_input_selectors:
                try:
                    search_input = self.driver.find_element(by, selector)
                    if search_input and search_input.is_displayed():
                        break
                except:
                    continue
            
            if not search_input:
                # 모든 텍스트 입력 필드 확인
                try:
                    all_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='search']")
                    for inp in all_inputs:
                        if inp.is_displayed():
                            placeholder = inp.get_attribute("placeholder") or ""
                            inp_id = inp.get_attribute("id") or ""
                            inp_name = inp.get_attribute("name") or ""
                            
                            if any(keyword in attr.lower() for keyword in ["검색", "search"] 
                                   for attr in [placeholder, inp_id, inp_name]):
                                search_input = inp
                                break
                    
                    # 마지막 시도: 첫 번째 보이는 텍스트 입력 사용
                    if not search_input:
                        for inp in all_inputs:
                            if inp.is_displayed():
                                search_input = inp
                                break
                except:
                    pass
            
            if not search_input:
                raise Exception("검색 입력 필드를 찾을 수 없습니다.")
            
            # 검색어 입력
            search_input.click()
            time.sleep(0.5)
            
            # 기존 내용 지우기
            search_input.clear()
            time.sleep(0.3)
            
            # 검색어 입력
            search_input.send_keys(keyword)
            time.sleep(1)
            
            # Enter 키로 검색 실행
            search_input.send_keys(Keys.RETURN)
            time.sleep(3)  # 검색 결과 로딩 대기
            
            return True
        
        except Exception as e:
            raise Exception(f"검색 중 오류 발생: {str(e)}")
