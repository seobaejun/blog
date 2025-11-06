"""
네이버 블로그 공감(좋아요) 모듈
Selenium을 사용하여 블로그 포스트에 공감 수행
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class LikePost:
    """네이버 블로그 공감 클래스"""
    
    def __init__(self, driver):
        """
        공감 모듈 초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def find_like_button(self):
        """
        공감 버튼 찾기 (검색 결과 페이지 또는 포스트 상세 페이지)
        
        Returns:
            공감 버튼 요소 또는 None
        """
        try:
            # 페이지 로딩 대기 (동적 콘텐츠 로딩 대기)
            time.sleep(2)
            
            # 페이지가 완전히 로드될 때까지 대기
            try:
                WebDriverWait(self.driver, 5).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            except:
                pass
            
            # 네이버 블로그 공감 버튼 선택자들 (최신 구조 반영)
            like_button_selectors = [
                # 최신 네이버 블로그 구조
                'button[aria-label*="공감"]',
                'button[title*="공감"]',
                'a[aria-label*="공감"]',
                'a[title*="공감"]',
                # 클래스명 기반 (더 구체적인 선택자)
                'button[class*="like"]',
                'button[class*="공감"]',
                'button[class*="Like"]',
                'a[class*="like"]',
                'a[class*="공감"]',
                'span[class*="like"]',
                'span[class*="공감"]',
                # 아이콘 기반
                'svg[class*="like"]',
                'i[class*="like"]',
                # 일반적인 선택자
                '.btn_like',
                '.like_btn',
                '.like_button',
                '.btn-like',
                '[data-testid*="like"]',
                '[data-action*="like"]',
                # 네이버 블로그 특화 선택자
                'button[type="button"][class*="btn"]',
                'a[role="button"]',
            ]
            
            # 각 선택자로 시도
            for selector in like_button_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        try:
                            if element.is_displayed():
                                # 텍스트나 속성 확인
                                text = element.text.strip()
                                aria_label = element.get_attribute("aria-label") or ""
                                title = element.get_attribute("title") or ""
                                class_attr = element.get_attribute("class") or ""
                                
                                # 공감 관련 키워드 확인
                                if any(keyword in attr.lower() for keyword in ["공감", "like"] 
                                       for attr in [text, aria_label, title, class_attr]):
                                    # 스크롤하여 보이게 만들기
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                                    time.sleep(0.5)
                                    return element
                        except:
                            continue
                except:
                    continue
            
            # XPath로 공감 관련 버튼 찾기
            xpath_selectors = [
                "//button[contains(text(), '공감')]",
                "//a[contains(text(), '공감')]",
                "//button[contains(@class, 'like')]",
                "//a[contains(@class, 'like')]",
                "//button[contains(@aria-label, '공감')]",
                "//a[contains(@aria-label, '공감')]",
                "//span[contains(text(), '공감')]/parent::button",
                "//span[contains(text(), '공감')]/parent::a",
                "//span[contains(text(), '공감')]/ancestor::button[1]",
                "//span[contains(text(), '공감')]/ancestor::a[1]",
                "//button[contains(@title, '공감')]",
                "//a[contains(@title, '공감')]",
            ]
            
            for xpath in xpath_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for element in elements:
                        try:
                            if element.is_displayed():
                                # 스크롤하여 보이게 만들기
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                                time.sleep(0.5)
                                return element
                        except:
                            continue
                except:
                    continue
            
            # 모든 버튼과 링크를 확인 (더 넓은 범위)
            # 먼저 버튼 요소만 확인 (공감은 보통 버튼)
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for element in all_buttons:
                try:
                    if not element.is_displayed():
                        continue
                    
                    text = element.text.strip()
                    class_attr = element.get_attribute("class") or ""
                    aria_label = element.get_attribute("aria-label") or ""
                    title = element.get_attribute("title") or ""
                    onclick = element.get_attribute("onclick") or ""
                    data_action = element.get_attribute("data-action") or ""
                    
                    # 공감 관련 키워드 확인 (더 넓은 범위)
                    search_text = (text + " " + class_attr + " " + aria_label + " " + title + " " + onclick + " " + data_action).lower()
                    if "공감" in search_text or ("like" in search_text and "unlike" not in search_text):
                        # 스크롤하여 보이게 만들기
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        time.sleep(0.5)
                        return element
                except:
                    continue
            
            # 링크 요소 확인
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            for element in all_links:
                try:
                    if not element.is_displayed():
                        continue
                    
                    text = element.text.strip()
                    class_attr = element.get_attribute("class") or ""
                    aria_label = element.get_attribute("aria-label") or ""
                    title = element.get_attribute("title") or ""
                    
                    search_text = (text + " " + class_attr + " " + aria_label + " " + title).lower()
                    if "공감" in search_text or ("like" in search_text and "unlike" not in search_text):
                        # 스크롤하여 보이게 만들기
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        time.sleep(0.5)
                        return element
                except:
                    continue
            
            return None
            
        except Exception as e:
            print(f"공감 버튼 찾기 실패: {str(e)}")
            return None
    
    def handle_popup(self):
        """
        팝업 처리 (더이상 공감을 추가할 수 없다는 메시지 등)
        
        Returns:
            bool: 팝업이 처리되었는지 여부
        """
        try:
            # 팝업/알림 관련 선택자들
            popup_selectors = [
                'div[class*="alert"]',
                'div[class*="popup"]',
                'div[class*="modal"]',
                'div[class*="dialog"]',
                '.alert',
                '.popup',
                '.modal',
                '.dialog',
            ]
            
            # 확인 버튼 선택자들
            confirm_button_selectors = [
                'button[class*="confirm"]',
                'button[class*="확인"]',
                'button[class*="ok"]',
                'button:has-text("확인")',
                'button:has-text("OK")',
                'a[class*="confirm"]',
                'a:has-text("확인")',
            ]
            
            # 팝업 찾기
            for selector in popup_selectors:
                try:
                    popup = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if popup.is_displayed():
                        # 팝업 내에서 확인 버튼 찾기
                        for btn_selector in confirm_button_selectors:
                            try:
                                confirm_btn = popup.find_element(By.CSS_SELECTOR, btn_selector)
                                if confirm_btn.is_displayed():
                                    confirm_btn.click()
                                    time.sleep(1)
                                    return True
                            except:
                                continue
                        
                        # XPath로 확인 버튼 찾기
                        try:
                            confirm_btn = popup.find_element(By.XPATH, ".//button[contains(text(), '확인')] | .//a[contains(text(), '확인')]")
                            if confirm_btn.is_displayed():
                                confirm_btn.click()
                                time.sleep(1)
                                return True
                        except:
                            pass
                        
                        # ESC 키로 닫기 시도
                        try:
                            from selenium.webdriver.common.keys import Keys
                            popup.send_keys(Keys.ESCAPE)
                            time.sleep(1)
                            return True
                        except:
                            pass
                except:
                    continue
            
            # 알림 텍스트 확인 (더이상 공감을 추가할 수 없다는 메시지)
            page_text = self.driver.page_source
            if "더이상 공감을 추가할 수 없" in page_text or "공감을 추가할 수 없" in page_text:
                # 확인 버튼 찾기
                for selector in confirm_button_selectors:
                    try:
                        confirm_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if confirm_btn.is_displayed():
                            confirm_btn.click()
                            time.sleep(1)
                            return True
                    except:
                        continue
                
                # XPath로 확인 버튼 찾기
                try:
                    confirm_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), '확인')] | //a[contains(text(), '확인')]")
                    if confirm_btn.is_displayed():
                        confirm_btn.click()
                        time.sleep(1)
                        return True
                except:
                    pass
                
                # ESC 키로 닫기
                try:
                    from selenium.webdriver.common.keys import Keys
                    self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    time.sleep(1)
                    return True
                except:
                    pass
            
            return False
            
        except Exception as e:
            print(f"팝업 처리 실패: {str(e)}")
            return False
    
    def find_like_button_in_element(self, parent_element):
        """
        특정 요소 내에서 공감 버튼 찾기
        
        Args:
            parent_element: 부모 요소
        
        Returns:
            공감 버튼 요소 또는 None
        """
        try:
            # 부모 요소 내에서 공감 버튼 찾기
            like_selectors = [
                './/button[contains(@aria-label, "공감")]',
                './/a[contains(@aria-label, "공감")]',
                './/button[contains(@class, "like")]',
                './/a[contains(@class, "like")]',
                './/span[contains(text(), "공감")]/parent::button',
                './/span[contains(text(), "공감")]/parent::a',
            ]
            
            for selector in like_selectors:
                try:
                    elements = parent_element.find_elements(By.XPATH, selector)
                    for element in elements:
                        try:
                            if element.is_displayed():
                                return element
                        except:
                            continue
                except:
                    continue
            return None
        except:
            return None
    
    def click_like_button_element(self, like_button):
        """
        찾은 공감 버튼 요소 클릭
        
        Args:
            like_button: 공감 버튼 요소
            
        Returns:
            dict: 작업 결과
        """
        try:
            # 요소가 보이도록 스크롤
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", like_button)
            time.sleep(1)  # 스크롤 대기
            
            # 요소가 클릭 가능한지 확인
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable(like_button)
                )
            except:
                pass  # 클릭 가능하지 않아도 계속 진행
            
            # 클릭 시도 (여러 방법)
            clicked = False
            try:
                # 1. 일반 클릭
                like_button.click()
                clicked = True
            except:
                try:
                    # 2. JavaScript 클릭
                    self.driver.execute_script("arguments[0].click();", like_button)
                    clicked = True
                except:
                    try:
                        # 3. ActionChains 사용
                        from selenium.webdriver.common.action_chains import ActionChains
                        ActionChains(self.driver).move_to_element(like_button).click().perform()
                        clicked = True
                    except:
                        pass
            
            if not clicked:
                return {'success': False, 'message': '공감 버튼 클릭 실패', 'popup_shown': False}
            
            time.sleep(2)  # 클릭 후 대기 (팝업이 나타날 시간)
            
            # 팝업 확인 및 처리
            popup_shown = self.handle_popup()
            
            if popup_shown:
                return {'success': True, 'message': '공감 클릭 완료 (팝업 처리됨)', 'popup_shown': True}
            else:
                return {'success': True, 'message': '공감 클릭 완료', 'popup_shown': False}
                
        except Exception as e:
            return {'success': False, 'message': f'공감 클릭 중 오류: {str(e)}', 'popup_shown': False}
    
    def click_like_button(self):
        """
        공감 버튼 클릭
        
        Returns:
            dict: 작업 결과 {'success': bool, 'message': str, 'popup_shown': bool}
        """
        try:
            # 공감 버튼 찾기
            like_button = self.find_like_button()
            
            if not like_button:
                return {'success': False, 'message': '공감 버튼을 찾을 수 없습니다.', 'popup_shown': False}
            
            # 공감 버튼 클릭
            try:
                like_button.click()
            except:
                # JavaScript로 클릭 시도
                try:
                    self.driver.execute_script("arguments[0].click();", like_button)
                except:
                    return {'success': False, 'message': '공감 버튼 클릭 실패', 'popup_shown': False}
            
            time.sleep(1)  # 클릭 후 대기
            
            # 팝업 확인 및 처리
            popup_shown = self.handle_popup()
            
            if popup_shown:
                return {'success': True, 'message': '공감 클릭 완료 (팝업 처리됨)', 'popup_shown': True}
            else:
                return {'success': True, 'message': '공감 클릭 완료', 'popup_shown': False}
                
        except Exception as e:
            return {'success': False, 'message': f'공감 클릭 중 오류: {str(e)}', 'popup_shown': False}
    
    def start_like_work(self, max_posts, delay, progress_callback=None, check_stop=None, check_pause=None):
        """
        공감 작업 시작
        
        Args:
            max_posts: 최대 처리할 포스트 수
            delay: 작업 간 딜레이 (초)
            progress_callback: 진행 상황 콜백 함수 (success_count, fail_count, current_total, max_total)
        
        Returns:
            dict: 작업 결과
        """
        success_count = 0
        fail_count = 0
        current_total = 0
        
        try:
            # 검색 결과 페이지에서 포스트 목록 찾기
            # neighbor_add.py와 동일한 방식으로 포스트 찾기
            post_selectors = [
                'a.text_link__w6SIY[href*="PostView.naver"]',
                'a[href*="PostView.naver"][class*="text_link"]',
                'a[href*="m.blog.naver.com/PostView.naver"]',
                'a[href*="/PostView.naver"]',
                'a[href*="/PostView"]',
            ]
            
            posts = []
            for selector in post_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        try:
                            if elem.is_displayed():
                                href = elem.get_attribute("href") or ""
                                if "PostView.naver" in href and elem not in posts:
                                    posts.append(elem)
                                    if len(posts) >= max_posts:
                                        break
                        except:
                            continue
                    if len(posts) >= max_posts:
                        break
                except:
                    continue
            
            # 추가로 href에 PostView.naver가 포함된 링크 찾기
            if len(posts) < max_posts:
                try:
                    all_links = self.driver.find_elements(By.TAG_NAME, "a")
                    for link in all_links:
                        try:
                            href = link.get_attribute("href") or ""
                            if "PostView.naver" in href and link.is_displayed():
                                if link not in posts:
                                    posts.append(link)
                                    if len(posts) >= max_posts:
                                        break
                        except:
                            continue
                except:
                    pass
            
            if not posts:
                return {
                    'success': False,
                    'message': '포스트를 찾을 수 없습니다.',
                    'success_count': 0,
                    'fail_count': 0,
                    'total': 0
                }
            
            # 최대 처리 개수만큼 제한
            posts_to_process = posts[:max_posts]
            
            self.driver.execute_script("window.scrollTo(0, 0);")  # 페이지 상단으로
            time.sleep(2)  # 페이지 로딩 대기
            
            for i, post in enumerate(posts_to_process):
                try:
                    # 작업 중지 체크
                    if check_stop and check_stop():
                        return {
                            'success': False,
                            'message': '작업이 중지되었습니다.',
                            'success_count': success_count,
                            'fail_count': fail_count,
                            'total': i
                        }
                    
                    # 작업 일시정지 체크
                    if check_pause and check_pause():
                        return {
                            'success': False,
                            'message': '작업이 중지되었습니다.',
                            'success_count': success_count,
                            'fail_count': fail_count,
                            'total': i
                        }
                    
                    current_total = i + 1
                    
                    # 포스트 상세 페이지로 이동 (공감 버튼은 상세 페이지에 있음)
                    try:
                        # href로 직접 이동하는 것이 더 안정적
                        href = post.get_attribute("href")
                        if href:
                            self.driver.get(href)
                            time.sleep(3)  # 페이지 로딩 대기 (공감 버튼이 로드될 때까지)
                        else:
                            # href가 없으면 클릭 시도
                            post.click()
                            time.sleep(3)
                    except Exception as e:
                        print(f"포스트 페이지 이동 실패: {str(e)}")
                        fail_count += 1
                        if progress_callback:
                            progress_callback(success_count, fail_count, current_total, max_posts)
                        continue
                    
                    # 공감 버튼 찾기 (상세 페이지에서)
                    # 여러 번 시도 (동적 로딩 대응)
                    like_button = None
                    for attempt in range(3):
                        like_button = self.find_like_button()
                        if like_button:
                            break
                        time.sleep(1)  # 재시도 대기
                    
                    if not like_button:
                        fail_count += 1
                        if progress_callback:
                            progress_callback(success_count, fail_count, current_total, max_posts)
                        # 검색 결과 페이지로 돌아가기
                        try:
                            self.driver.back()
                            time.sleep(1)
                        except:
                            pass
                        continue
                    
                    # 공감 버튼 클릭
                    result = self.click_like_button_element(like_button)
                    
                    # 결과 로깅 (디버깅용)
                    if not result['success']:
                        print(f"공감 버튼 클릭 실패: {result['message']}")
                        # 현재 페이지의 모든 버튼 정보 출력 (디버깅용)
                        try:
                            all_btns = self.driver.find_elements(By.TAG_NAME, "button")
                            print(f"페이지에 버튼 개수: {len(all_btns)}")
                            for idx, btn in enumerate(all_btns[:5]):  # 처음 5개만
                                try:
                                    btn_text = btn.text.strip()[:20]
                                    btn_class = btn.get_attribute("class")[:50] if btn.get_attribute("class") else ""
                                    btn_aria = btn.get_attribute("aria-label") or ""
                                    print(f"  버튼 {idx+1}: text='{btn_text}', class='{btn_class}', aria='{btn_aria}'")
                                except:
                                    pass
                        except:
                            pass
                    
                    if result['success']:
                        success_count += 1
                    else:
                        fail_count += 1
                    
                    # 진행 상황 업데이트
                    if progress_callback:
                        progress_callback(success_count, fail_count, current_total, max_posts)
                    
                    # 딜레이
                    if i < len(posts_to_process) - 1:  # 마지막이 아니면 딜레이
                        # 딜레이 중에도 중지/일시정지 체크
                        elapsed = 0
                        while elapsed < delay:
                            if check_stop and check_stop():
                                return {
                                    'success': False,
                                    'message': '작업이 중지되었습니다.',
                                    'success_count': success_count,
                                    'fail_count': fail_count,
                                    'total': current_total
                                }
                            if check_pause:
                                if check_pause():
                                    return {
                                        'success': False,
                                        'message': '작업이 중지되었습니다.',
                                        'success_count': success_count,
                                        'fail_count': fail_count,
                                        'total': current_total
                                    }
                            time.sleep(0.5)
                            elapsed += 0.5
                    
                    # 이전 페이지로 돌아가기 (또는 다음 포스트로)
                    try:
                        self.driver.back()
                        time.sleep(1)
                    except:
                        # 검색 결과 페이지로 다시 이동
                        try:
                            self.driver.execute_script("window.history.back();")
                            time.sleep(1)
                        except:
                            pass
                    
                except Exception as e:
                    fail_count += 1
                    if progress_callback:
                        progress_callback(success_count, fail_count, current_total, max_posts)
                    continue
            
            return {
                'success': True,
                'message': '공감 작업 완료',
                'success_count': success_count,
                'fail_count': fail_count,
                'total': current_total
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'공감 작업 중 오류: {str(e)}',
                'success_count': success_count,
                'fail_count': fail_count,
                'total': current_total
            }

