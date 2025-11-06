"""
네이버 블로그 검색 모듈
Playwright를 사용하여 블로그 검색 수행
"""
import time
import asyncio
from playwright.async_api import async_playwright, Browser, Page


class BlogSearch:
    """네이버 블로그 검색 클래스"""
    
    RECOMMENDATION_URL = "https://m.blog.naver.com/Recommendation.naver"
    SEARCH_URL = "https://m.blog.naver.com/SectionSearch.naver"
    
    def __init__(self):
        """검색 모듈 초기화"""
        self.browser = None
        self.page = None
        self.playwright = None
    
    async def start_browser(self, headless=False):
        """
        브라우저 시작
        
        Args:
            headless: 헤드리스 모드 여부 (기본값: False)
        """
        self.playwright = await async_playwright().start()
        
        # 브라우저 옵션 설정
        browser_options = {
            "headless": headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-infobars",
                "--disable-notifications",
                "--start-maximized",
            ]
        }
        
        self.browser = await self.playwright.chromium.launch(**browser_options)
        
        # 새 컨텍스트 생성 (봇 탐지 회피)
        context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )
        
        # webdriver 속성 제거
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.chrome = {
                runtime: {}
            };
        """)
        
        self.page = await context.new_page()
    
    async def close_browser(self):
        """브라우저 종료"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def find_search_button_on_recommendation(self):
        """
        Recommendation 페이지에서 검색 버튼 찾기
        
        Returns:
            검색 버튼 요소 또는 None
        """
        try:
            # 페이지가 완전히 로드될 때까지 대기
            await self.page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)  # 추가 대기
            
            # 검색 버튼 선택자들 (모바일 블로그 페이지)
            search_button_selectors = [
                'button[class*="search"]',
                'button[aria-label*="검색"]',
                'button[title*="검색"]',
                'a[href*="search"]',
                'a[href*="SectionSearch"]',
                '.btn_search',
                '.search_btn',
                '.search_button',
                'button._search',
                'svg[class*="search"]',  # SVG 아이콘
                '[data-testid*="search"]',  # 테스트 ID로 검색 버튼 찾기
            ]
            
            # 모든 링크와 버튼 확인
            all_links = await self.page.query_selector_all('a[href*="search"], a[href*="SectionSearch"]')
            all_buttons = await self.page.query_selector_all('button')
            
            # 먼저 링크에서 검색 페이지로 가는 링크 찾기
            for link in all_links:
                try:
                    href = await link.get_attribute("href") or ""
                    if "SectionSearch" in href or "search" in href.lower():
                        is_visible = await link.is_visible()
                        if is_visible:
                            return link
                except:
                    continue
            
            # 버튼 선택자로 찾기
            for selector in search_button_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        if is_visible:
                            return element
                except:
                    continue
            
            # 모든 버튼 중에서 검색 관련 속성이 있는 버튼 찾기
            for btn in all_buttons:
                try:
                    is_visible = await btn.is_visible()
                    if is_visible:
                        btn_class = await btn.get_attribute("class") or ""
                        btn_title = await btn.get_attribute("title") or ""
                        btn_aria = await btn.get_attribute("aria-label") or ""
                        btn_text = await btn.inner_text() or ""
                        
                        if any(keyword in attr.lower() for keyword in ["검색", "search"] 
                               for attr in [btn_class, btn_title, btn_aria, btn_text]):
                            return btn
                except:
                    continue
            
            return None
        
        except Exception as e:
            print(f"검색 버튼 찾기 실패: {str(e)}")
            return None
    
    async def find_search_input_after_click(self):
        """
        검색 버튼 클릭 후 나타나는 검색 입력 필드 찾기
        
        Returns:
            검색 입력 필드 요소 또는 None
        """
        try:
            await asyncio.sleep(1)  # 검색창이 나타날 때까지 대기
            
            # 검색 입력 필드 찾기
            input_selectors = [
                'input[type="text"]',
                'input[type="search"]',
                'input[placeholder*="검색"]',
                'input[name*="search"]',
                'input[id*="search"]',
                'input[class*="search"]',
            ]
            
            for selector in input_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        if is_visible:
                            return element
                except:
                    continue
            
            # 모든 input 요소 확인
            all_inputs = await self.page.query_selector_all('input[type="text"], input[type="search"]')
            for inp in all_inputs:
                try:
                    if await inp.is_visible():
                        return inp
                except:
                    continue
            
            return None
        
        except Exception as e:
            print(f"검색 입력 필드 찾기 실패: {str(e)}")
            return None
    
    async def find_search_input_direct(self):
        """
        SectionSearch 페이지에서 직접 검색 입력 필드 찾기
        
        Returns:
            검색 입력 필드 요소 또는 None
        """
        try:
            await self.page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)  # 페이지 로딩 대기
            
            # 검색 입력 필드 찾기 (여러 선택자 시도)
            search_input_selectors = [
                'input[type="text"][placeholder*="검색"]',
                'input[type="search"]',
                'input[type="text"]',
                'input[class*="search"]',
                'input[name*="search"]',
                'input[id*="search"]',
                'input[placeholder*="블로그"]',
                'input._search_input',
            ]
            
            for selector in search_input_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        if is_visible:
                            return element
                except:
                    continue
            
            # 모든 text 타입 input 확인
            all_inputs = await self.page.query_selector_all('input[type="text"], input[type="search"]')
            for inp in all_inputs:
                try:
                    if await inp.is_visible():
                        placeholder = await inp.get_attribute("placeholder") or ""
                        inp_id = await inp.get_attribute("id") or ""
                        inp_name = await inp.get_attribute("name") or ""
                        inp_class = await inp.get_attribute("class") or ""
                        
                        # 검색 관련 속성이 있는 input 찾기
                        if any(keyword in attr.lower() for keyword in ["검색", "search"] 
                               for attr in [placeholder, inp_id, inp_name, inp_class]):
                            return inp
                except:
                    continue
            
            # 마지막 시도: 첫 번째 보이는 text input 사용
            for inp in all_inputs:
                try:
                    if await inp.is_visible():
                        return inp
                except:
                    continue
            
            return None
        
        except Exception as e:
            print(f"검색 입력 필드 찾기 실패: {str(e)}")
            return None
    
    async def search(self, keyword, blog_url=None):
        """
        Recommendation 페이지에서 검색 버튼 클릭 후 SectionSearch 페이지로 이동하여 검색 수행
        
        Args:
            keyword: 검색어
            blog_url: 블로그 페이지 URL (기본값: RECOMMENDATION_URL)
        
        Returns:
            bool: 검색 성공 여부
        """
        try:
            if not self.page:
                await self.start_browser(headless=False)
            
            # 1. Recommendation 페이지로 이동
            target_url = blog_url or self.RECOMMENDATION_URL
            await self.page.goto(target_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(3)  # 페이지 로딩 대기
            
            # 2. 검색 버튼 찾기
            search_button = await self.find_search_button_on_recommendation()
            
            if not search_button:
                # 추가 대기 후 다시 시도
                await asyncio.sleep(2)
                search_button = await self.find_search_button_on_recommendation()
                
                if not search_button:
                    raise Exception("검색 버튼을 찾을 수 없습니다. Recommendation 페이지 구조를 확인해주세요.")
            
            # 3. 검색 버튼 클릭
            await search_button.click()
            await asyncio.sleep(2)  # 검색 페이지로 이동할 때까지 대기
            
            # 4. SectionSearch 페이지로 이동 확인 (URL 확인)
            current_url = self.page.url
            if "SectionSearch" not in current_url:
                # 직접 이동 시도
                await self.page.goto(self.SEARCH_URL, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)
            
            # 5. 검색 입력 필드 찾기
            search_input = await self.find_search_input_direct()
            
            if not search_input:
                # 추가 대기 후 다시 시도
                await asyncio.sleep(2)
                search_input = await self.find_search_input_direct()
                
                if not search_input:
                    raise Exception("검색 입력 필드를 찾을 수 없습니다. SectionSearch 페이지 구조를 확인해주세요.")
            
            # 6. 검색어 입력
            await search_input.click()
            await asyncio.sleep(0.5)  # 클릭 후 대기
            
            # 기존 내용 지우기 (있는 경우)
            await search_input.fill("")
            await asyncio.sleep(0.3)
            
            # 검색어 입력
            await search_input.fill(keyword)
            await asyncio.sleep(1)  # 입력 대기
            
            # 7. Enter 키로 검색 실행
            await search_input.press("Enter")
            await asyncio.sleep(3)  # 검색 결과 로딩 대기
            
            return True
        
        except Exception as e:
            raise Exception(f"검색 중 오류 발생: {str(e)}")
    
    def search_sync(self, keyword, blog_url=None):
        """
        동기식 검색 메서드 (GUI에서 호출용)
        
        Args:
            keyword: 검색어
            blog_url: 블로그 페이지 URL (기본값: RECOMMENDATION_URL)
        
        Returns:
            bool: 검색 성공 여부
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.search(keyword, blog_url))
            return result
        finally:
            loop.close()
    
    async def get_page_source(self):
        """현재 페이지 소스 반환 (디버깅용)"""
        if self.page:
            return await self.page.content()
        return None

