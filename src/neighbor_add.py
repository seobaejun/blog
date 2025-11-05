"""
네이버 블로그 서로이웃 추가 모듈
검색 결과에서 블로그를 찾아 서로이웃 추가 수행
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class NeighborAdd:
    """네이버 블로그 서로이웃 추가 클래스"""
    
    def __init__(self, driver):
        """
        서로이웃 추가 모듈 초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
        """
        self.driver = driver
    
    def find_blog_posts(self, max_posts=10):
        """
        검색 결과 페이지에서 블로그 포스트 목록 찾기
        
        Args:
            max_posts: 최대 찾을 포스트 개수
        
        Returns:
            list: 블로그 포스트 요소 리스트
        """
        try:
            posts = []
            
            # 먼저 제공된 HTML 구조에 맞는 선택자로 찾기
            # a[href*="PostView.naver"] 또는 class="text_link__w6SIY" 포함된 링크
            post_selectors = [
                'a.text_link__w6SIY[href*="PostView.naver"]',
                'a[href*="PostView.naver"][class*="text_link"]',
                'a[href*="m.blog.naver.com/PostView.naver"]',
                'a[href*="/PostView.naver"]',
                'a[href*="/PostList.naver"]',
            ]
            
            for selector in post_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        try:
                            if elem.is_displayed():
                                href = elem.get_attribute("href") or ""
                                # PostView.naver가 포함된 링크만 선택
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
            
            return posts[:max_posts]
        
        except Exception as e:
            print(f"블로그 포스트 찾기 실패: {str(e)}")
            return []
    
    def click_blog_post(self, post_element):
        """
        블로그 포스트 클릭
        
        Args:
            post_element: 블로그 포스트 요소
        
        Returns:
            bool: 클릭 성공 여부
        """
        try:
            # 새 탭에서 열릴 수 있으므로 원래 창 핸들 저장
            original_window = self.driver.current_window_handle
            window_count_before = len(self.driver.window_handles)
            
            # 포스트 클릭 (JavaScript 사용하여 새 탭에서 열기)
            href = post_element.get_attribute("href")
            if href:
                # JavaScript로 새 탭에서 열기
                self.driver.execute_script(f"window.open('{href}', '_blank');")
                time.sleep(2)
            else:
                # 직접 클릭
                post_element.click()
                time.sleep(3)  # 페이지 로딩 대기
            
            # 새 탭이 열렸다면 전환
            if len(self.driver.window_handles) > window_count_before:
                for handle in self.driver.window_handles:
                    if handle != original_window:
                        self.driver.switch_to.window(handle)
                        break
                time.sleep(2)  # 새 페이지 로딩 대기
            
            return True
        
        except Exception as e:
            print(f"블로그 포스트 클릭 실패: {str(e)}")
            return False
    
    def find_neighbor_add_button(self):
        """
        이웃추가 버튼 찾기
        
        Returns:
            버튼 요소 또는 None
        """
        try:
            # 이웃추가 버튼 선택자들
            button_selectors = [
                'button[class*="이웃"]',
                'button[class*="neighbor"]',
                'a[href*="neighbor"]',
                'button[onclick*="neighbor"]',
                '.btn_neighbor',
                '.neighbor_btn',
                'button[title*="이웃"]',
                'button[aria-label*="이웃"]',
                'a[title*="이웃추가"]',
            ]
            
            for selector in button_selectors:
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if button.is_displayed():
                        return button
                except:
                    continue
            
            # 텍스트로 찾기
            try:
                all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                all_links = self.driver.find_elements(By.TAG_NAME, "a")
                all_elements = all_buttons + all_links
                
                for elem in all_elements:
                    try:
                        if not elem.is_displayed():
                            continue
                        
                        text = elem.text or ""
                        title = elem.get_attribute("title") or ""
                        aria_label = elem.get_attribute("aria-label") or ""
                        
                        if any(keyword in attr for keyword in ["이웃추가", "이웃 추가", "neighbor"] 
                               for attr in [text, title, aria_label]):
                            return elem
                    except:
                        continue
            except:
                pass
            
            return None
        
        except Exception as e:
            print(f"이웃추가 버튼 찾기 실패: {str(e)}")
            return None
    
    def find_mutual_neighbor_button(self):
        """
        서로이웃 추가 버튼 찾기
        label[for="bothBuddyRadio"] 또는 input#bothBuddyRadio 형식
        
        Returns:
            버튼 요소 또는 None
        """
        try:
            # 먼저 제공된 HTML 구조에 맞는 선택자로 찾기
            mutual_selectors = [
                'label[for="bothBuddyRadio"]',
                'input#bothBuddyRadio',
                'input[id="bothBuddyRadio"]',
                'input[name*="bothBuddy"]',
                'input[type="radio"][id*="bothBuddy"]',
                'label[for*="bothBuddy"]',
            ]
            
            for selector in mutual_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        # label인 경우 클릭 가능
                        if element.tag_name == "label":
                            return element
                        # input인 경우도 클릭 가능
                        elif element.tag_name == "input":
                            return element
                except:
                    continue
            
            # 기존 방식으로도 찾기 (하위 호환성)
            button_selectors = [
                'button[class*="서로이웃"]',
                'button[class*="mutual"]',
                'a[href*="mutual"]',
                'button[onclick*="mutual"]',
                '.btn_mutual',
                '.mutual_neighbor_btn',
                'button[title*="서로이웃"]',
                'button[aria-label*="서로이웃"]',
                'a[title*="서로이웃"]',
            ]
            
            for selector in button_selectors:
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if button.is_displayed():
                        return button
                except:
                    continue
            
            # 텍스트로 찾기 (label, input, button 등)
            try:
                all_labels = self.driver.find_elements(By.TAG_NAME, "label")
                all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                all_links = self.driver.find_elements(By.TAG_NAME, "a")
                all_elements = all_labels + all_inputs + all_buttons + all_links
                
                for elem in all_elements:
                    try:
                        if not elem.is_displayed():
                            continue
                        
                        text = elem.text or ""
                        title = elem.get_attribute("title") or ""
                        aria_label = elem.get_attribute("aria-label") or ""
                        for_attr = elem.get_attribute("for") or ""
                        
                        # "서로이웃을 신청합니다" 또는 "서로이웃" 텍스트 포함
                        if any(keyword in attr for keyword in ["서로이웃을 신청합니다", "서로이웃", "서로 이웃", "mutual"] 
                               for attr in [text, title, aria_label, for_attr]):
                            return elem
                    except:
                        continue
            except:
                pass
            
            return None
        
        except Exception as e:
            print(f"서로이웃 추가 버튼 찾기 실패: {str(e)}")
            return None
    
    def find_complete_button(self):
        """
        확인 버튼 찾기 (서로이웃 추가 후)
        <a href="#" class="btn_ok" ng-click="...">확인</a> 형식
        
        Returns:
            버튼 요소 또는 None
        """
        try:
            # 먼저 제공된 HTML 구조에 맞는 선택자로 찾기
            complete_selectors = [
                'a.btn_ok',
                'a[class*="btn_ok"]',
                'a[class="btn_ok"]',
                'button.btn_ok',
                'button[class*="btn_ok"]',
            ]
            
            for selector in complete_selectors:
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if button.is_displayed():
                        # 텍스트가 "확인"인지 확인
                        text = button.text or ""
                        if "확인" in text or button.tag_name == "a":
                            return button
                except:
                    continue
            
            # 기존 방식으로도 찾기 (하위 호환성)
            button_selectors = [
                'button[class*="완료"]',
                'button[class*="확인"]',
                'button[class*="닫기"]',
                'button[title*="완료"]',
                'button[title*="확인"]',
                'button[title*="닫기"]',
                'button[aria-label*="완료"]',
                'button[aria-label*="확인"]',
                'button[aria-label*="닫기"]',
                '.btn_confirm',
                '.btn_close',
                '.btn_complete',
            ]
            
            for selector in button_selectors:
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if button.is_displayed():
                        return button
                except:
                    continue
            
            # 텍스트로 찾기 (a, button, span 등)
            try:
                all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                all_links = self.driver.find_elements(By.TAG_NAME, "a")
                all_spans = self.driver.find_elements(By.TAG_NAME, "span")
                all_elements = all_buttons + all_links + all_spans
                
                for elem in all_elements:
                    try:
                        if not elem.is_displayed():
                            continue
                        
                        text = elem.text or ""
                        title = elem.get_attribute("title") or ""
                        aria_label = elem.get_attribute("aria-label") or ""
                        
                        if any(keyword in attr for keyword in ["확인", "완료", "닫기", "OK", "ok"] 
                               for attr in [text, title, aria_label]):
                            # 링크나 버튼이면 바로 반환
                            if elem.tag_name in ["a", "button"]:
                                return elem
                            # span이면 부모 링크나 버튼 찾기
                            elif elem.tag_name == "span":
                                try:
                                    parent = elem.find_element(By.XPATH, "./ancestor::a[1]")
                                    if parent:
                                        return parent
                                except:
                                    try:
                                        parent = elem.find_element(By.XPATH, "./ancestor::button[1]")
                                        if parent:
                                            return parent
                                    except:
                                        pass
                    except:
                        continue
            except:
                pass
            
            return None
        
        except Exception as e:
            print(f"완료 버튼 찾기 실패: {str(e)}")
            return None
    
    def check_mutual_neighbor_success(self):
        """
        서로이웃 추가 성공 여부 확인
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 성공 메시지나 상태 확인
            success_indicators = [
                "서로이웃이 되었습니다",
                "서로이웃 추가 완료",
                "서로이웃",
                "mutual neighbor",
            ]
            
            page_text = self.driver.page_source
            
            for indicator in success_indicators:
                if indicator in page_text:
                    return True
            
            return False
        
        except:
            return False
    
    def add_neighbor(self, include_neighbor=False):
        """
        일반 이웃추가 수행 (서로이웃 실패 시)
        
        Args:
            include_neighbor: 이웃추가 포함 옵션
        
        Returns:
            bool: 성공 여부
        """
        try:
            neighbor_button = self.find_neighbor_add_button()
            if neighbor_button:
                neighbor_button.click()
                time.sleep(2)
                return True
            return False
        except:
            return False
    
    def close_current_tab(self):
        """현재 탭 닫기 (검색 결과 페이지로 돌아가기)"""
        try:
            if len(self.driver.window_handles) > 1:
                self.driver.close()
                # 검색 결과 페이지로 전환 (첫 번째 창)
                if self.driver.window_handles:
                    self.driver.switch_to.window(self.driver.window_handles[0])
                time.sleep(1)
        except:
            pass
    
    def process_blog_post(self, post_element, include_neighbor=False, mutual_only=True):
        """
        단일 블로그 포스트에 대한 서로이웃 추가 처리
        
        Args:
            post_element: 블로그 포스트 요소
            include_neighbor: 이웃추가 포함 옵션
            mutual_only: 서로이웃만 옵션
        
        Returns:
            dict: 처리 결과 {'success': bool, 'type': 'mutual' or 'neighbor' or 'failed'}
        """
        original_handles = self.driver.window_handles.copy()
        
        try:
            # 1. 블로그 포스트 클릭
            if not self.click_blog_post(post_element):
                return {'success': False, 'type': 'failed', 'reason': '포스트 클릭 실패'}
            
            time.sleep(3)  # 페이지 로딩 대기
            
            # 이웃추가 버튼 찾기 (서로이웃 버튼은 이웃추가 버튼 클릭 후 나타날 수 있음)
            neighbor_button = self.find_neighbor_add_button()
            if not neighbor_button:
                self.close_current_tab()
                return {'success': False, 'type': 'failed', 'reason': '이웃추가 버튼 없음'}
            
            # 서로이웃만 옵션인 경우 (이웃추가 포함이 체크 안됨)
            if mutual_only and not include_neighbor:
                # 이웃추가 버튼 클릭하여 서로이웃 버튼이 나타나도록 함
                try:
                    neighbor_button.click()
                    time.sleep(2)  # 모달/팝업 표시 대기
                except:
                    # 클릭 실패 시 JavaScript로 시도
                    try:
                        self.driver.execute_script("arguments[0].click();", neighbor_button)
                        time.sleep(2)
                    except:
                        self.close_current_tab()
                        return {'success': False, 'type': 'failed', 'reason': '이웃추가 버튼 클릭 실패'}
                
                # 서로이웃 버튼 찾기
                mutual_button = self.find_mutual_neighbor_button()
                
                if mutual_button:
                    # 서로이웃 버튼 클릭
                    try:
                        mutual_button.click()
                        time.sleep(2)  # 라디오 버튼 선택 대기
                    except:
                        # JavaScript로 시도
                        try:
                            self.driver.execute_script("arguments[0].click();", mutual_button)
                            time.sleep(2)
                        except:
                            self.close_current_tab()
                            return {'success': False, 'type': 'failed', 'reason': '서로이웃 버튼 클릭 실패'}
                    
                    # label을 클릭한 경우 실제 라디오 버튼이 선택되었는지 확인
                    if mutual_button.tag_name == "label":
                        try:
                            # label의 for 속성으로 연결된 라디오 버튼 확인
                            for_attr = mutual_button.get_attribute("for")
                            if for_attr:
                                radio_input = self.driver.find_element(By.ID, for_attr)
                                # 라디오 버튼이 선택되지 않았다면 직접 클릭
                                if not radio_input.is_selected():
                                    radio_input.click()
                                    time.sleep(1)
                        except:
                            pass
                    
                    # 확인 버튼을 찾기 위해 약간 더 대기
                    time.sleep(1)
                    
                    # 완료 버튼 찾아서 클릭
                    complete_button = self.find_complete_button()
                    if complete_button:
                        try:
                            # 확인 버튼이 보일 때까지 스크롤
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", complete_button)
                            time.sleep(0.5)
                            complete_button.click()
                            time.sleep(2)  # 확인 버튼 클릭 후 처리 대기
                        except:
                            try:
                                # JavaScript로 클릭 시도
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", complete_button)
                                time.sleep(0.5)
                                self.driver.execute_script("arguments[0].click();", complete_button)
                                time.sleep(2)
                            except Exception as e:
                                print(f"확인 버튼 클릭 실패: {str(e)}")
                                self.close_current_tab()
                                return {'success': False, 'type': 'failed', 'reason': '확인 버튼 클릭 실패'}
                    else:
                        self.close_current_tab()
                        return {'success': False, 'type': 'failed', 'reason': '확인 버튼을 찾을 수 없음'}
                    
                    # 성공 여부 확인
                    if self.check_mutual_neighbor_success():
                        self.close_current_tab()
                        return {'success': True, 'type': 'mutual'}
                    else:
                        # 서로이웃 실패 시 빠져나오기 (일반 이웃추가는 하지 않음)
                        self.close_current_tab()
                        return {'success': False, 'type': 'failed', 'reason': '서로이웃 추가 실패'}
                else:
                    # 서로이웃 버튼이 없으면 빠져나오기
                    self.close_current_tab()
                    return {'success': False, 'type': 'failed', 'reason': '서로이웃 버튼 없음'}
            
            # 이웃추가 포함 옵션인 경우
            # 먼저 서로이웃 시도, 실패하면 이웃추가로 진행
            else:
                # 1단계: 이웃추가 버튼 클릭하여 서로이웃 버튼이 나타나도록 함
                try:
                    neighbor_button.click()
                    time.sleep(2)  # 모달/팝업 표시 대기
                except:
                    # 클릭 실패 시 JavaScript로 시도
                    try:
                        self.driver.execute_script("arguments[0].click();", neighbor_button)
                        time.sleep(2)
                    except:
                        self.close_current_tab()
                        return {'success': False, 'type': 'failed', 'reason': '이웃추가 버튼 클릭 실패'}
                
                # 2단계: 서로이웃 버튼 찾기
                mutual_button = self.find_mutual_neighbor_button()
                
                if mutual_button:
                    # 서로이웃 버튼이 있으면 먼저 서로이웃 시도
                    try:
                        mutual_button.click()
                        time.sleep(2)  # 라디오 버튼 선택 대기
                    except:
                        # JavaScript로 시도
                        try:
                            self.driver.execute_script("arguments[0].click();", mutual_button)
                            time.sleep(2)
                        except:
                            pass
                    
                    # label을 클릭한 경우 실제 라디오 버튼이 선택되었는지 확인
                    if mutual_button.tag_name == "label":
                        try:
                            # label의 for 속성으로 연결된 라디오 버튼 확인
                            for_attr = mutual_button.get_attribute("for")
                            if for_attr:
                                radio_input = self.driver.find_element(By.ID, for_attr)
                                # 라디오 버튼이 선택되지 않았다면 직접 클릭
                                if not radio_input.is_selected():
                                    radio_input.click()
                                    time.sleep(1)
                        except:
                            pass
                    
                    # 확인 버튼을 찾기 위해 약간 더 대기
                    time.sleep(1)
                    
                    # 완료 버튼 찾아서 클릭
                    complete_button = self.find_complete_button()
                    if complete_button:
                        try:
                            # 확인 버튼이 보일 때까지 스크롤
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", complete_button)
                            time.sleep(0.5)
                            complete_button.click()
                            time.sleep(2)  # 확인 버튼 클릭 후 처리 대기
                        except:
                            try:
                                # JavaScript로 클릭 시도
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", complete_button)
                                time.sleep(0.5)
                                self.driver.execute_script("arguments[0].click();", complete_button)
                                time.sleep(2)
                            except:
                                pass
                    
                    # 서로이웃 성공 여부 확인
                    if self.check_mutual_neighbor_success():
                        self.close_current_tab()
                        return {'success': True, 'type': 'mutual'}
                    
                    # 서로이웃 실패 시 이웃추가로 진행
                    time.sleep(1)
                    # 이미 이웃추가 버튼을 눌렀으므로 일반 이웃추가로 완료된 것으로 간주
                    self.close_current_tab()
                    return {'success': True, 'type': 'neighbor'}
                else:
                    # 서로이웃 버튼이 없으면 일반 이웃추가로 완료 (이미 이웃추가 버튼을 눌렀으므로)
                    time.sleep(1)
                    self.close_current_tab()
                    return {'success': True, 'type': 'neighbor'}
        
        except Exception as e:
            # 에러 발생 시 페이지 닫기
            self.close_current_tab()
            return {'success': False, 'type': 'failed', 'reason': f'오류: {str(e)}'}
    
    def start_neighbor_add_work(self, include_neighbor=False, mutual_only=True, max_posts=10, delay=30, progress_callback=None, work_control=None):
        """
        서로이웃 추가 작업 시작
        
        Args:
            include_neighbor: 이웃추가 포함 옵션
            mutual_only: 서로이웃만 옵션
            max_posts: 최대 처리할 포스트 수
            delay: 각 작업 사이 딜레이 (초)
            progress_callback: 진행 상황 업데이트 콜백 함수 (success_count, fail_count, current_total, max_total)
            work_control: 작업 제어 딕셔너리 {'stop': bool, 'pause': bool}
        
        Returns:
            dict: 작업 결과
        """
        try:
            # 검색 결과 페이지에서 블로그 포스트 찾기
            posts = self.find_blog_posts(max_posts=max_posts)
            
            if not posts:
                return {
                    'success': False,
                    'message': '블로그 포스트를 찾을 수 없습니다.',
                    'total': 0,
                    'success_count': 0,
                    'fail_count': 0
                }
            
            success_count = 0
            fail_count = 0
            mutual_count = 0
            neighbor_count = 0
            total_posts = len(posts)
            
            for i, post in enumerate(posts, 1):
                try:
                    # 작업 중지 체크
                    if work_control and work_control.get('stop', False):
                        return {
                            'success': False,
                            'message': '사용자에 의해 작업이 중지되었습니다.',
                            'total': total_posts,
                            'success_count': success_count,
                            'fail_count': fail_count,
                            'mutual_count': mutual_count,
                            'neighbor_count': neighbor_count
                        }
                    
                    # 작업 일시정지 체크 (일시정지가 해제될 때까지 대기)
                    if work_control and work_control.get('pause', False):
                        while work_control.get('pause', False) and not work_control.get('stop', False):
                            time.sleep(0.5)  # 0.5초마다 일시정지 상태 확인
                        
                        # 일시정지 중에 중지 요청이 있었다면 중지
                        if work_control.get('stop', False):
                            return {
                                'success': False,
                                'message': '사용자에 의해 작업이 중지되었습니다.',
                                'total': total_posts,
                                'success_count': success_count,
                                'fail_count': fail_count,
                                'mutual_count': mutual_count,
                                'neighbor_count': neighbor_count
                            }
                    
                    # 검색 결과 페이지로 돌아가기 (첫 번째 포스트가 아니고 새 탭이 열렸다면)
                    if i > 1 and len(self.driver.window_handles) > 1:
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        time.sleep(1)
                    
                    # 포스트 처리
                    result = self.process_blog_post(post, include_neighbor, mutual_only)
                    
                    if result['success']:
                        success_count += 1
                        if result['type'] == 'mutual':
                            mutual_count += 1
                        elif result['type'] == 'neighbor':
                            neighbor_count += 1
                    else:
                        fail_count += 1
                    
                    # 진행 상황 업데이트 콜백 호출
                    if progress_callback:
                        current_total = success_count + fail_count
                        try:
                            progress_callback(success_count, fail_count, current_total, total_posts)
                        except:
                            pass  # 콜백 실행 중 오류가 발생해도 작업은 계속 진행
                    
                    # 딜레이 (마지막 포스트 제외)
                    if i < len(posts):
                        # 딜레이 중에도 중지/일시정지 체크
                        elapsed = 0
                        check_interval = 0.5  # 0.5초마다 체크
                        while elapsed < delay:
                            if work_control and work_control.get('stop', False):
                                return {
                                    'success': False,
                                    'message': '사용자에 의해 작업이 중지되었습니다.',
                                    'total': total_posts,
                                    'success_count': success_count,
                                    'fail_count': fail_count,
                                    'mutual_count': mutual_count,
                                    'neighbor_count': neighbor_count
                                }
                            if work_control and work_control.get('pause', False):
                                while work_control.get('pause', False) and not work_control.get('stop', False):
                                    time.sleep(check_interval)
                                if work_control.get('stop', False):
                                    return {
                                        'success': False,
                                        'message': '사용자에 의해 작업이 중지되었습니다.',
                                        'total': total_posts,
                                        'success_count': success_count,
                                        'fail_count': fail_count,
                                        'mutual_count': mutual_count,
                                        'neighbor_count': neighbor_count
                                    }
                            time.sleep(min(check_interval, delay - elapsed))
                            elapsed += check_interval
                
                except Exception as e:
                    fail_count += 1
                    print(f"포스트 {i} 처리 중 오류: {str(e)}")
                    # 진행 상황 업데이트 (오류 발생 시)
                    if progress_callback:
                        current_total = success_count + fail_count
                        try:
                            progress_callback(success_count, fail_count, current_total, total_posts)
                        except:
                            pass
                    continue
            
            return {
                'success': True,
                'message': '서로이웃 추가 작업 완료',
                'total': len(posts),
                'success_count': success_count,
                'fail_count': fail_count,
                'mutual_count': mutual_count,
                'neighbor_count': neighbor_count
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'작업 중 오류 발생: {str(e)}',
                'total': 0,
                'success_count': 0,
                'fail_count': 0
            }
