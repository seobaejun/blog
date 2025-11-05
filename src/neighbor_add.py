"""
네이버 블로그 서로이웃 추가 모듈
검색 결과에서 블로그를 찾아 서로이웃 추가 수행
"""
import time
import os
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
    
    def find_neighbor_message_textarea(self):
        """
        서로이웃 메시지 입력 textarea 찾기
        <textarea rows="4" cols="35" class="textarea_t1 ng-pristine ng-valid ng-not-empty ng-touched" ng-model="data.inviteMessage">우리 서로이웃해요~</textarea>
        
        Returns:
            textarea 요소 또는 None
        """
        try:
            # textarea 선택자들
            textarea_selectors = [
                'textarea[ng-model="data.inviteMessage"]',
                'textarea[ng-model*="inviteMessage"]',
                'textarea[class*="textarea_t1"]',
                'textarea[class="textarea_t1"]',
            ]
            
            for selector in textarea_selectors:
                try:
                    textarea = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if textarea.is_displayed():
                        return textarea
                except:
                    continue
            
            # ng-model 속성으로 찾기
            try:
                all_textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                for textarea in all_textareas:
                    try:
                        if not textarea.is_displayed():
                            continue
                        
                        ng_model = textarea.get_attribute("ng-model") or ""
                        class_attr = textarea.get_attribute("class") or ""
                        
                        if "inviteMessage" in ng_model or "textarea_t1" in class_attr:
                            return textarea
                    except:
                        continue
            except:
                pass
            
            return None
        
        except Exception as e:
            print(f"서로이웃 메시지 textarea 찾기 실패: {str(e)}")
            return None
    
    def write_neighbor_message(self, message_text):
        """
        서로이웃 메시지 입력
        1. textarea 클릭
        2. "우리 서로이웃해요~" 디폴트 글씨 삭제
        3. 메시지 입력
        
        Args:
            message_text: 입력할 메시지 텍스트
        
        Returns:
            bool: 메시지 입력 성공 여부
        """
        try:
            # textarea 찾기
            textarea = self.find_neighbor_message_textarea()
            if not textarea:
                print("서로이웃 메시지 textarea를 찾을 수 없습니다.")
                return False
            
            # textarea를 보이도록 스크롤
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", textarea)
                time.sleep(0.5)
            except:
                pass
            
            # textarea 클릭
            try:
                textarea.click()
                time.sleep(0.5)
            except:
                try:
                    self.driver.execute_script("arguments[0].click();", textarea)
                    time.sleep(0.5)
                except:
                    pass
            
            # 기존 내용 삭제 ("우리 서로이웃해요~" 디폴트 글씨)
            try:
                # textarea의 값을 빈 문자열로 설정
                self.driver.execute_script("arguments[0].value = '';", textarea)
                time.sleep(0.3)
                
                # Angular 모델도 업데이트 (ng-model이 있는 경우)
                ng_model = textarea.get_attribute("ng-model")
                if ng_model:
                    # AngularJS 모델 업데이트
                    self.driver.execute_script(f"""
                        var element = arguments[0];
                        var scope = angular.element(element).scope();
                        if (scope) {{
                            scope.$apply(function() {{
                                {ng_model} = '';
                            }});
                        }}
                    """, textarea)
                    time.sleep(0.3)
            except:
                # JavaScript로 직접 삭제 시도
                try:
                    textarea.clear()
                    time.sleep(0.3)
                except:
                    pass
            
            # 메시지 입력
            try:
                # JavaScript로 직접 입력
                escaped_text = message_text.replace("'", "\\'").replace("\n", "\\n").replace("\\", "\\\\")
                self.driver.execute_script(f"arguments[0].value = '{escaped_text}';", textarea)
                time.sleep(0.3)
                
                # Angular 모델도 업데이트
                ng_model = textarea.get_attribute("ng-model")
                if ng_model:
                    # AngularJS 모델 업데이트
                    self.driver.execute_script(f"""
                        var element = arguments[0];
                        var scope = angular.element(element).scope();
                        if (scope) {{
                            scope.$apply(function() {{
                                {ng_model} = '{escaped_text}';
                            }});
                        }}
                    """, textarea)
                    time.sleep(0.3)
            except Exception as e:
                print(f"메시지 입력 실패 (JavaScript): {str(e)}, send_keys로 재시도")
                # send_keys로 시도
                try:
                    textarea.clear()
                    time.sleep(0.3)
                    textarea.send_keys(message_text)
                    time.sleep(0.5)
                except Exception as e2:
                    print(f"send_keys 입력도 실패: {str(e2)}")
                    return False
            
            return True
        
        except Exception as e:
            print(f"서로이웃 메시지 입력 실패: {str(e)}")
            return False
    
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
    
    def find_like_button(self):
        """
        공감 버튼 찾기
        <a class="u_likeit_button _face off"> 또는 <a class="u_likeit_list_button _button off" data-type="like">
        
        Returns:
            버튼 요소 또는 None
        """
        try:
            # 페이지를 스크롤하여 공감 버튼이 보이도록 함
            try:
                self.driver.execute_script("window.scrollTo(0, 0);")  # 페이지 상단으로
                time.sleep(0.5)
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")  # 페이지 중간으로
                time.sleep(0.5)
            except:
                pass
            
            # 먼저 제공된 HTML 구조에 맞는 선택자로 찾기
            # 클래스가 공백으로 구분되어 있으므로 [class*="..."] 형식 사용
            like_selectors = [
                'a[class*="u_likeit_button"][class*="_face"]',  # 메인 공감 버튼
                'a[class*="u_likeit_button"]',  # 일반 공감 버튼
                'div[class*="u_likeit_list_module"] a[class*="u_likeit_button"]',  # 모듈 내부 버튼
                'a[class*="u_likeit_list_button"][data-type="like"]',  # 공감 리스트 버튼
                'li[class*="u_likeit_list"][class*="like"] a',  # 공감 리스트 내부 링크
                'a[role="button"][aria-haspopup="true"][class*="u_likeit"]',  # aria 속성으로 찾기
                'a[onclick*="like"][class*="u_likeit"]',  # onclick 속성으로 찾기
            ]
            
            for selector in like_selectors:
                try:
                    # find_elements로 여러 개 찾기
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        try:
                            if button.is_displayed():
                                # 버튼이 보이는 영역으로 스크롤
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                                time.sleep(0.3)
                                return button
                        except:
                            continue
                except:
                    continue
            
            # XPath로 찾기
            try:
                xpath_selectors = [
                    "//a[contains(@class, 'u_likeit_button') and contains(@class, '_face')]",
                    "//a[contains(@class, 'u_likeit_button')]",
                    "//div[contains(@class, 'u_likeit_list_module')]//a[contains(@class, 'u_likeit_button')]",
                    "//a[@data-type='like' and contains(@class, 'u_likeit')]",
                ]
                
                for xpath in xpath_selectors:
                    try:
                        buttons = self.driver.find_elements(By.XPATH, xpath)
                        for button in buttons:
                            try:
                                if button.is_displayed():
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                                    time.sleep(0.3)
                                    return button
                            except:
                                continue
                    except:
                        continue
            except:
                pass
            
            # 텍스트로 찾기
            try:
                all_links = self.driver.find_elements(By.TAG_NAME, "a")
                for link in all_links:
                    try:
                        if not link.is_displayed():
                            continue
                        
                        class_attr = link.get_attribute("class") or ""
                        data_type = link.get_attribute("data-type") or ""
                        role = link.get_attribute("role") or ""
                        
                        # 공감 버튼 관련 클래스나 속성 확인
                        if ("u_likeit" in class_attr and "like" in data_type) or \
                           ("u_likeit_button" in class_attr) or \
                           ("u_likeit_list_button" in class_attr and data_type == "like") or \
                           (role == "button" and "u_likeit" in class_attr):
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                            time.sleep(0.3)
                            return link
                    except:
                        continue
            except:
                pass
            
            return None
        
        except Exception as e:
            print(f"공감 버튼 찾기 실패: {str(e)}")
            return None
    
    def click_like_button(self):
        """
        공감 버튼 클릭
        공감이 안되어 있으면 클릭하고, 이미 공감되어 있으면 넘어감
        팝업이 떠도 다음 작업으로 진행
        
        Returns:
            bool: 공감 시도 성공 여부 (팝업이 떠도 True 반환)
        """
        try:
            like_button = self.find_like_button()
            if not like_button:
                print("공감 버튼을 찾을 수 없습니다.")
                # 페이지 소스를 확인하여 공감 관련 요소가 있는지 확인
                try:
                    page_source = self.driver.page_source
                    if "u_likeit" in page_source:
                        print("페이지에 공감 관련 요소는 있지만 버튼을 찾지 못했습니다.")
                    else:
                        print("페이지에 공감 관련 요소가 없습니다.")
                except:
                    pass
                return False
            
            # 공감 상태 확인 (class에 "off"가 있으면 공감 안됨, "on"이 있으면 공감됨)
            class_attr = like_button.get_attribute("class") or ""
            
            # 이미 공감되어 있으면 넘어가기
            if "on" in class_attr and "off" not in class_attr:
                print("이미 공감되어 있음")
                return True
            
            # 공감 버튼 클릭
            try:
                # 공감 레이어가 열려야 할 수도 있으므로 먼저 버튼 클릭
                like_button.click()
                time.sleep(1.5)  # 공감 레이어가 열릴 시간 대기
                
                # 공감 리스트 버튼 찾기 (공감 메뉴에서)
                like_list_selectors = [
                    'li[class*="u_likeit_list"][class*="like"] a',  # 가장 구체적인 선택자
                    'a[class*="u_likeit_list_button"][data-type="like"]',  # data-type으로 찾기
                    'a[class*="u_likeit_list_button"][class*="_button"][data-type="like"]',
                    'a[role="button"][data-type="like"][class*="u_likeit"]',  # role과 data-type으로 찾기
                ]
                
                list_button_clicked = False
                for selector in like_list_selectors:
                    try:
                        list_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if list_button.is_displayed():
                            list_button.click()
                            time.sleep(1)
                            list_button_clicked = True
                            break
                    except:
                        continue
                
                # 공감 리스트 버튼을 찾지 못했어도 성공으로 처리 (팝업 가능성)
                return True
                
            except Exception as e:
                # 클릭 실패 시 JavaScript로 시도
                try:
                    self.driver.execute_script("arguments[0].click();", like_button)
                    time.sleep(1.5)  # 공감 레이어가 열릴 시간 대기
                    
                    # 공감 리스트 버튼도 JavaScript로 클릭 시도
                    like_list_selectors = [
                        'li[class*="u_likeit_list"][class*="like"] a',
                        'a[class*="u_likeit_list_button"][data-type="like"]',
                        'a[class*="u_likeit_list_button"][class*="_button"][data-type="like"]',
                        'a[role="button"][data-type="like"][class*="u_likeit"]',
                    ]
                    
                    for selector in like_list_selectors:
                        try:
                            list_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if list_button.is_displayed():
                                self.driver.execute_script("arguments[0].click();", list_button)
                                time.sleep(1)
                                break
                        except:
                            continue
                    
                    return True
                except:
                    # 팝업이 떠도 성공으로 처리
                    return True
        
        except Exception as e:
            print(f"공감 버튼 클릭 실패: {str(e)} (팝업 가능성)")
            # 팝업이 떠도 다음 작업으로 진행
            return True
    
    def load_comment_list(self, comment_file_path):
        """
        댓글 파일에서 댓글 목록 로드
        
        Args:
            comment_file_path: 댓글 파일 경로 (None이면 기본 댓글 사용)
        
        Returns:
            list: 댓글 목록 (한 줄에 하나씩)
        """
        DEFAULT_COMMENT = "잘 보고 갑니다!"
        
        if not comment_file_path or not os.path.exists(comment_file_path):
            return [DEFAULT_COMMENT]
        
        try:
            with open(comment_file_path, 'r', encoding='utf-8') as f:
                comments = [line.strip() for line in f.readlines() if line.strip()]
            
            # 빈 파일이거나 유효한 댓글이 없는 경우 기본 댓글 반환
            if not comments:
                return [DEFAULT_COMMENT]
            
            return comments
        except Exception as e:
            print(f"댓글 파일 읽기 실패: {str(e)}")
            return [DEFAULT_COMMENT]
    
    def load_neighbor_message_list(self, neighbor_file_path):
        """
        서로이웃 메시지 파일에서 메시지 목록 로드
        
        Args:
            neighbor_file_path: 서로이웃 메시지 파일 경로 (None이면 기본 메시지 사용하지 않음)
        
        Returns:
            list: 메시지 목록 (한 줄에 하나씩), 파일이 없으면 None
        """
        if not neighbor_file_path or not os.path.exists(neighbor_file_path):
            return None
        
        try:
            with open(neighbor_file_path, 'r', encoding='utf-8') as f:
                messages = [line.strip() for line in f.readlines() if line.strip()]
            
            # 빈 파일이거나 유효한 메시지가 없는 경우 None 반환
            if not messages:
                return None
            
            return messages
        except Exception as e:
            print(f"서로이웃 메시지 파일 읽기 실패: {str(e)}")
            return None
    
    def find_comment_button(self):
        """
        댓글 버튼 찾기 (댓글 영역 열기)
        <button type="button" class="comment_btn__TUucZ" data-click-area="pst.re">
        
        Returns:
            댓글 버튼 요소 또는 None
        """
        try:
            # 댓글 버튼 선택자들
            comment_button_selectors = [
                'button.comment_btn__TUucZ[data-click-area="pst.re"]',
                'button[class*="comment_btn"][data-click-area="pst.re"]',
                'button[class*="comment_btn"]',
                'button[data-click-area*="pst"]',
            ]
            
            for selector in comment_button_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        try:
                            if button.is_displayed():
                                # "댓글" 텍스트가 포함된 버튼인지 확인
                                text = button.text or ""
                                class_attr = button.get_attribute("class") or ""
                                if "comment" in class_attr.lower() or "댓글" in text:
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                                    time.sleep(0.5)
                                    return button
                        except:
                            continue
                except:
                    continue
            
            # 텍스트로 찾기
            try:
                all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for button in all_buttons:
                    try:
                        if not button.is_displayed():
                            continue
                        
                        class_attr = button.get_attribute("class") or ""
                        data_area = button.get_attribute("data-click-area") or ""
                        
                        if "comment_btn" in class_attr or ("comment" in class_attr.lower() and "pst" in data_area):
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                            time.sleep(0.5)
                            return button
                    except:
                        continue
            except:
                pass
            
            return None
        
        except Exception as e:
            print(f"댓글 버튼 찾기 실패: {str(e)}")
            return None
    
    def find_comment_placeholder(self):
        """
        댓글 placeholder 영역 찾기 (클릭하여 입력 영역 활성화)
        <div class="u_cbox_guide" data-action="write#placeholder" data-param="@event">댓글을 입력해주세요.</div>
        
        Returns:
            placeholder 요소 또는 None
        """
        try:
            # placeholder 선택자들
            placeholder_selectors = [
                'div.u_cbox_guide[data-action="write#placeholder"]',
                'div[class*="u_cbox_guide"][data-action*="write#placeholder"]',
                'div.u_cbox_guide',
                'div[data-action*="write#placeholder"]',
            ]
            
            for selector in placeholder_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        try:
                            if elem.is_displayed():
                                text = elem.text or ""
                                if "댓글을 입력해주세요" in text or "댓글" in text:
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                                    time.sleep(0.5)
                                    return elem
                        except:
                            continue
                except:
                    continue
            
            return None
        
        except Exception as e:
            print(f"댓글 placeholder 찾기 실패: {str(e)}")
            return None
    
    def find_comment_area(self):
        """
        댓글 입력 영역 찾기
        <div title="댓글" id="naverComment__write_textarea" class="u_cbox_text u_cbox_text_mention" contenteditable="true" data-area-code="RPC.input"></div>
        
        Returns:
            댓글 입력 영역 요소 또는 None
        """
        try:
            # 댓글 입력 영역 선택자들
            comment_area_selectors = [
                'div#naverComment__write_textarea.u_cbox_text',
                'div[id="naverComment__write_textarea"]',
                'div[class*="u_cbox_text"][contenteditable="true"]',
                'div[title="댓글"][contenteditable="true"]',
                'div[data-area-code="RPC.input"][contenteditable="true"]',
                'div[contenteditable="true"][class*="u_cbox_text"]',
            ]
            
            for selector in comment_area_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        try:
                            if elem.is_displayed():
                                elem_id = elem.get_attribute("id") or ""
                                elem_title = elem.get_attribute("title") or ""
                                contenteditable = elem.get_attribute("contenteditable") or ""
                                
                                if (elem_id == "naverComment__write_textarea" or 
                                    elem_title == "댓글" or 
                                    (contenteditable == "true" and "u_cbox_text" in (elem.get_attribute("class") or ""))):
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                                    time.sleep(0.5)
                                    return elem
                        except:
                            continue
                except:
                    continue
            
            # 마지막 시도: contenteditable div 중에서 찾기
            try:
                all_editable = self.driver.find_elements(By.CSS_SELECTOR, 'div[contenteditable="true"]')
                for elem in all_editable:
                    try:
                        if not elem.is_displayed():
                            continue
                        
                        elem_id = elem.get_attribute("id") or ""
                        elem_class = elem.get_attribute("class") or ""
                        
                        if "naverComment" in elem_id or "u_cbox_text" in elem_class:
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                            time.sleep(0.5)
                            return elem
                    except:
                        continue
            except:
                pass
            
            return None
        
        except Exception as e:
            print(f"댓글 입력 영역 찾기 실패: {str(e)}")
            return None
    
    def check_already_commented(self):
        """
        이미 댓글을 작성했는지 확인
        (댓글 영역이 이미 열려있거나, 댓글 입력 영역에 내용이 있는지 확인)
        
        Returns:
            bool: 이미 댓글을 작성했으면 True, 아니면 False
        """
        print("[댓글 확인] 댓글 작성 여부 확인을 시작합니다...")
        try:
            # 먼저 댓글 영역이 이미 열려있는지 확인
            comment_area = self.find_comment_area()
            
            # 댓글 영역이 없으면 댓글 버튼 클릭하여 열기
            if not comment_area:
                print("[댓글 확인] 댓글 영역이 열려있지 않습니다. 댓글 버튼을 클릭합니다...")
                comment_button = self.find_comment_button()
                if not comment_button:
                    print("[댓글 확인] 댓글 버튼을 찾을 수 없습니다.")
                    return False  # 댓글 버튼을 찾을 수 없으면 확인 불가
                
                try:
                    comment_button.click()
                    time.sleep(3)  # 댓글 영역이 열릴 때까지 충분히 대기
                except:
                    try:
                        self.driver.execute_script("arguments[0].click();", comment_button)
                        time.sleep(3)
                    except:
                        return False  # 댓글 버튼 클릭 실패
                
                # 댓글 영역이 로드될 때까지 대기 및 스크롤
                try:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)
                    # 댓글 영역으로 스크롤
                    comment_area_element = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="u_cbox"], div[id*="comment"]')
                    if comment_area_element:
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", comment_area_element[0])
                        time.sleep(1)
                except:
                    pass
                
                # 다시 댓글 영역 찾기
                comment_area = self.find_comment_area()
            
            # 1. 댓글 입력 영역에 이미 내용이 있는지 확인 (이건 임시로 입력한 내용일 수 있으므로 주의)
            # 이 부분은 주석 처리하고 다른 방법으로 확인
            # if comment_area:
            #     try:
            #         # contenteditable div의 내용 확인
            #         existing_text = self.driver.execute_script("return arguments[0].innerText;", comment_area)
            #         if existing_text and existing_text.strip():
            #             # 이미 내용이 있으면 작성된 것으로 간주
            #             print(f"[댓글 확인] 이미 작성된 댓글이 있습니다: {existing_text[:50]}...")
            #             return True
            #     except:
            #         pass
            
            # 2. 댓글 목록에서 내가 작성한 댓글 확인 (수정/삭제 버튼이 있는 댓글 찾기)
            # 댓글 목록이 로드될 때까지 추가 대기 및 스크롤
            time.sleep(3)  # 대기 시간 증가
            
            # 댓글 영역을 더 아래로 스크롤하여 모든 댓글이 로드되도록 함
            try:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                # 댓글 영역 내에서 스크롤
                comment_container = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="u_cbox"], div[id*="comment"], div[class*="comment"]')
                if comment_container:
                    for container in comment_container[:3]:  # 처음 3개만 확인
                        try:
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", container)
                            time.sleep(0.5)
                        except:
                            pass
            except:
                pass
            
            try:
                # 방법 1: 페이지 소스에서 "수정" 또는 "삭제" 키워드 확인 (더 빠름)
                try:
                    page_source = self.driver.page_source
                    # 댓글 영역 내에서 수정/삭제 버튼이 있는지 확인
                    if "수정" in page_source or "삭제" in page_source:
                        # 댓글 영역 내에서만 확인
                        comment_section = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="u_cbox"], div[id*="comment"], div[class*="comment"]')
                        for section in comment_section:
                            try:
                                section_html = section.get_attribute("outerHTML") or ""
                                section_text = section.text or ""
                                
                                # 수정/삭제 버튼이 댓글 영역 내에 있는지 확인
                                if ("수정" in section_text or "삭제" in section_text or 
                                    "modify" in section_html.lower() or "delete" in section_html.lower()):
                                    # 추가 확인: 수정/삭제 버튼이 실제로 있는지
                                    buttons_in_section = section.find_elements(By.TAG_NAME, "button")
                                    links_in_section = section.find_elements(By.TAG_NAME, "a")
                                    for btn in buttons_in_section + links_in_section:
                                        try:
                                            btn_text = btn.text or ""
                                            btn_class = btn.get_attribute("class") or ""
                                            if ("수정" in btn_text or "삭제" in btn_text or 
                                                "modify" in btn_class.lower() or "delete" in btn_class.lower()):
                                                print(f"[댓글 확인] 내가 작성한 댓글을 찾았습니다. (버튼 텍스트: {btn_text})")
                                                return True
                                        except:
                                            continue
                            except:
                                continue
                except:
                    pass
                
                # 방법 2: 모든 버튼과 링크에서 수정/삭제 버튼 찾기 (조건 완화)
                try:
                    all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    all_links = self.driver.find_elements(By.TAG_NAME, "a")
                    all_elements = all_buttons + all_links
                    
                    for elem in all_elements:
                        try:
                            if not elem.is_displayed():
                                continue
                            
                            elem_class = elem.get_attribute("class") or ""
                            elem_title = elem.get_attribute("title") or ""
                            elem_text = elem.text or ""
                            elem_aria_label = elem.get_attribute("aria-label") or ""
                            
                            # 수정 관련 키워드 확인 (조건 완화)
                            if ("수정" in elem_text or "modify" in elem_class.lower() or "edit" in elem_class.lower() or 
                                "수정" in elem_title or "수정" in elem_aria_label):
                                # 댓글 영역 근처에 있는지 확인 (parent 찾기 시도)
                                is_in_comment_area = False
                                try:
                                    parent = elem.find_element(By.XPATH, "./ancestor::div[contains(@class, 'u_cbox') or contains(@id, 'comment') or contains(@class, 'comment')]")
                                    is_in_comment_area = True
                                except:
                                    # parent 찾기 실패 시, 댓글 영역 근처인지 다른 방법으로 확인
                                    try:
                                        # 현재 요소의 위치를 확인하여 댓글 영역 근처인지 판단
                                        location = elem.location
                                        size = elem.size
                                        
                                        # 댓글 영역 요소들과의 거리 확인
                                        comment_areas = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="u_cbox"], div[id*="comment"], div[class*="comment"]')
                                        for comment_area_elem in comment_areas[:5]:  # 처음 5개만 확인
                                            try:
                                                comment_location = comment_area_elem.location
                                                comment_size = comment_area_elem.size
                                                
                                                # 요소가 댓글 영역과 겹치거나 근처에 있는지 확인
                                                if (abs(location['y'] - comment_location['y']) < 1000 or  # 1000px 이내
                                                    "u_cbox" in elem_class or "comment" in elem_class.lower()):
                                                    is_in_comment_area = True
                                                    break
                                            except:
                                                continue
                                    except:
                                        pass
                                
                                if is_in_comment_area or "u_cbox" in elem_class or "comment" in elem_class.lower():
                                    print(f"[댓글 확인] 내가 작성한 댓글의 수정 버튼을 찾았습니다. (텍스트: {elem_text}, 클래스: {elem_class[:50]})")
                                    return True
                            
                            # 삭제 관련 키워드 확인 (조건 완화)
                            if ("삭제" in elem_text or "delete" in elem_class.lower() or "del" in elem_class.lower() or 
                                "삭제" in elem_title or "삭제" in elem_aria_label):
                                # 댓글 영역 근처에 있는지 확인
                                is_in_comment_area = False
                                try:
                                    parent = elem.find_element(By.XPATH, "./ancestor::div[contains(@class, 'u_cbox') or contains(@id, 'comment') or contains(@class, 'comment')]")
                                    is_in_comment_area = True
                                except:
                                    # parent 찾기 실패 시, 댓글 영역 근처인지 다른 방법으로 확인
                                    try:
                                        location = elem.location
                                        comment_areas = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="u_cbox"], div[id*="comment"], div[class*="comment"]')
                                        for comment_area_elem in comment_areas[:5]:
                                            try:
                                                comment_location = comment_area_elem.location
                                                if abs(location['y'] - comment_location['y']) < 1000:
                                                    is_in_comment_area = True
                                                    break
                                            except:
                                                continue
                                    except:
                                        pass
                                
                                if is_in_comment_area or "u_cbox" in elem_class or "comment" in elem_class.lower():
                                    print(f"[댓글 확인] 내가 작성한 댓글의 삭제 버튼을 찾았습니다. (텍스트: {elem_text}, 클래스: {elem_class[:50]})")
                                    return True
                        except:
                            continue
                except Exception as e:
                    print(f"[댓글 확인] 버튼 찾기 중 오류: {str(e)}")
                    pass
                
                # 댓글 목록에서 "내 댓글" 표시 확인
                try:
                    page_source = self.driver.page_source
                    # 내 댓글 관련 텍스트나 클래스 확인
                    if "내 댓글" in page_source or "my_comment" in page_source.lower():
                        # 더 정확하게 확인하기 위해 댓글 영역 내에서 확인
                        comment_list_selectors = [
                            'div[class*="u_cbox_comment"]',
                            'li[class*="u_cbox_comment"]',
                            'div[class*="u_cbox_list"]',
                        ]
                        
                        for selector in comment_list_selectors:
                            try:
                                comment_items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                for item in comment_items:
                                    if not item.is_displayed():
                                        continue
                                    
                                    item_html = item.get_attribute("outerHTML") or ""
                                    item_text = item.text or ""
                                    
                                    # 내 댓글 표시나 수정/삭제 관련 텍스트가 있는지 확인
                                    if ("내 댓글" in item_text or 
                                        "수정" in item_text or 
                                        "삭제" in item_text or
                                        "my_comment" in item_html.lower() or
                                        "modify" in item_html.lower() or
                                        "delete" in item_html.lower()):
                                        print("[댓글 확인] 내가 작성한 댓글이 댓글 목록에 있습니다.")
                                        return True
                            except:
                                continue
                except:
                    pass
            except:
                pass
            
            # 3. 댓글 등록 버튼이 비활성화되어 있는지 확인
            submit_button = self.find_comment_submit_button()
            if submit_button:
                try:
                    # 버튼이 비활성화되어 있거나 disabled 속성이 있는지 확인
                    is_disabled = submit_button.get_attribute("disabled")
                    is_enabled = submit_button.is_enabled()
                    
                    if is_disabled or not is_enabled:
                        print("[댓글 확인] 댓글 등록 버튼이 비활성화되어 있습니다. (이미 작성된 것으로 간주)")
                        return True
                    
                    # 버튼의 클래스에서 disabled 관련 클래스 확인
                    button_class = submit_button.get_attribute("class") or ""
                    if "disabled" in button_class.lower() or "off" in button_class.lower():
                        print("[댓글 확인] 댓글 등록 버튼이 비활성화 상태입니다.")
                        return True
                except:
                    pass
            
            # 4. 댓글 입력 영역이 readonly이거나 비활성화되어 있는지 확인
            if comment_area:
                try:
                    readonly = comment_area.get_attribute("readonly")
                    contenteditable = comment_area.get_attribute("contenteditable")
                    
                    if readonly or contenteditable == "false":
                        print("[댓글 확인] 댓글 입력 영역이 비활성화되어 있습니다.")
                        return True
                except:
                    pass
            
            print("[댓글 확인] 이미 작성한 댓글을 찾지 못했습니다. 댓글 작성 가능 상태로 판단합니다.")
            return False
        
        except Exception as e:
            print(f"[댓글 확인] 댓글 작성 여부 확인 실패: {str(e)}")
            import traceback
            traceback.print_exc()
            return False  # 확인 실패 시 작성 가능한 것으로 간주
    
    def find_comment_submit_button(self):
        """
        댓글 등록 버튼 찾기
        <button type="button" class="u_cbox_btn_upload __uis_naverComment_writeButton" data-action="write#request" data-area-code="RPC.write" data-ui-selector="writeButton">
        
        Returns:
            댓글 등록 버튼 요소 또는 None
        """
        try:
            # 댓글 등록 버튼 선택자들
            submit_selectors = [
                'button.u_cbox_btn_upload.__uis_naverComment_writeButton[data-action="write#request"]',
                'button[class*="u_cbox_btn_upload"][data-action="write#request"]',
                'button[data-area-code="RPC.write"][data-ui-selector="writeButton"]',
                'button[data-action="write#request"]',
                'button[class*="u_cbox_btn_upload"]',
            ]
            
            for selector in submit_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        try:
                            if button.is_displayed():
                                text = button.text or ""
                                data_action = button.get_attribute("data-action") or ""
                                
                                # "등록" 텍스트가 있거나 data-action이 "write#request"인 경우
                                if "등록" in text or "write#request" in data_action:
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                                    time.sleep(0.3)
                                    return button
                        except:
                            continue
                except:
                    continue
            
            # 텍스트로 찾기
            try:
                all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for button in all_buttons:
                    try:
                        if not button.is_displayed():
                            continue
                        
                        text = button.text or ""
                        class_attr = button.get_attribute("class") or ""
                        data_action = button.get_attribute("data-action") or ""
                        
                        if ("등록" in text and "u_cbox" in class_attr) or "write#request" in data_action:
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                            time.sleep(0.3)
                            return button
                    except:
                        continue
            except:
                pass
            
            return None
        
        except Exception as e:
            print(f"댓글 등록 버튼 찾기 실패: {str(e)}")
            return None
    
    def write_comment(self, comment_text, comment_list, current_index):
        """
        댓글 작성 (단계별 처리)
        1. 이미 댓글을 작성했는지 확인
        2. 댓글 버튼 클릭
        3. placeholder 클릭
        4. 댓글 입력 영역에 텍스트 입력
        5. 등록 버튼 클릭
        
        Args:
            comment_text: 작성할 댓글 텍스트
            comment_list: 전체 댓글 목록
            current_index: 현재 사용할 댓글 인덱스
        
        Returns:
            bool or str: 댓글 작성 성공 여부 또는 "already_commented" (이미 작성함)
        """
        try:
            # 페이지를 스크롤하여 댓글 영역이 보이도록 함
            try:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
            except:
                pass
            
            # 0단계: 이미 댓글을 작성했는지 확인
            if self.check_already_commented():
                print("[댓글] 이미 작성한 댓글이 있습니다. 다음으로 넘어갑니다.")
                return "already_commented"
            
            # 1단계: 댓글 버튼 찾기 및 클릭 (댓글 영역이 아직 열려있지 않은 경우)
            # check_already_commented에서 이미 댓글 영역을 열었을 수 있으므로 먼저 확인
            comment_area = self.find_comment_area()
            if not comment_area:
                # 댓글 영역이 없으면 댓글 버튼 클릭
                comment_button = self.find_comment_button()
                if not comment_button:
                    print("댓글 버튼을 찾을 수 없습니다.")
                    return False
                
                try:
                    comment_button.click()
                    time.sleep(2)  # 댓글 영역이 열릴 때까지 대기
                except:
                    # JavaScript로 클릭 시도
                    try:
                        self.driver.execute_script("arguments[0].click();", comment_button)
                        time.sleep(2)
                    except:
                        print("댓글 버튼 클릭 실패")
                        return False
            else:
                # 댓글 영역이 이미 열려있으면 대기만
                time.sleep(1)
            
            # 2단계: placeholder 찾기 및 클릭 (입력 영역 활성화)
            placeholder = self.find_comment_placeholder()
            if placeholder:
                try:
                    placeholder.click()
                    time.sleep(1)  # 입력 영역이 활성화될 때까지 대기
                except:
                    # JavaScript로 클릭 시도
                    try:
                        self.driver.execute_script("arguments[0].click();", placeholder)
                        time.sleep(1)
                    except:
                        pass  # placeholder 클릭 실패해도 계속 진행
            
            # 3단계: 댓글 입력 영역 찾기
            comment_area = self.find_comment_area()
            if not comment_area:
                print("댓글 입력 영역을 찾을 수 없습니다.")
                return False
            
            # 댓글 입력 (contenteditable div)
            try:
                # 기존 내용 지우기
                self.driver.execute_script("arguments[0].innerText = '';", comment_area)
                time.sleep(0.3)
                
                # 클릭하여 포커스 주기
                comment_area.click()
                time.sleep(0.5)
                
                # 텍스트 입력 (JavaScript로 직접 입력 - 중복 입력 방지)
                escaped_text = comment_text.replace("'", "\\'").replace("\n", "\\n").replace("\\", "\\\\")
                self.driver.execute_script(f"arguments[0].innerText = '{escaped_text}';", comment_area)
                time.sleep(1)
            except Exception as e:
                print(f"댓글 입력 실패: {str(e)}, send_keys로 재시도")
                # JavaScript 실패 시 send_keys로 시도
                try:
                    comment_area.clear()
                    time.sleep(0.3)
                    comment_area.click()
                    time.sleep(0.5)
                    comment_area.send_keys(comment_text)
                    time.sleep(1)
                except Exception as e2:
                    print(f"send_keys 입력도 실패: {str(e2)}")
                    return False
            
            # 4단계: 등록 버튼 찾기 및 클릭
            submit_button = self.find_comment_submit_button()
            if not submit_button:
                print("댓글 등록 버튼을 찾을 수 없습니다.")
                return False
            
            try:
                submit_button.click()
                time.sleep(3)  # 댓글 등록 대기 (더 긴 대기 시간)
            except:
                # JavaScript로 클릭 시도
                try:
                    self.driver.execute_script("arguments[0].click();", submit_button)
                    time.sleep(3)
                except:
                    print("등록 버튼 클릭 실패")
                    return False
            
            return True
        
        except Exception as e:
            print(f"댓글 작성 실패: {str(e)}")
            return False
    
    def process_blog_post(self, post_element, include_neighbor=False, mutual_only=True, like_enabled=False, comment_enabled=False, comment_list=None, comment_index=0, neighbor_message_list=None, neighbor_message_index=0):
        """
        단일 블로그 포스트에 대한 서로이웃 추가 처리
        
        Args:
            post_element: 블로그 포스트 요소
            include_neighbor: 이웃추가 포함 옵션
            mutual_only: 서로이웃만 옵션
            like_enabled: 공감 활성화 옵션
            comment_enabled: 댓글 작성 활성화 옵션
            comment_list: 댓글 목록 (None이면 기본 댓글 사용)
            comment_index: 현재 사용할 댓글 인덱스
            neighbor_message_list: 서로이웃 메시지 목록 (None이면 메시지 입력 안함)
            neighbor_message_index: 현재 사용할 서로이웃 메시지 인덱스
        
        Returns:
            dict: 처리 결과 {'success': bool, 'type': 'mutual' or 'neighbor' or 'failed' or 'comment'}
        """
        original_handles = self.driver.window_handles.copy()
        
        try:
            # 1. 블로그 포스트 클릭
            if not self.click_blog_post(post_element):
                return {'success': False, 'type': 'failed', 'reason': '포스트 클릭 실패'}
            
            time.sleep(3)  # 페이지 로딩 대기
            
            # 2. 공감 처리 (공감 옵션이 활성화된 경우)
            like_success = False
            if like_enabled:
                try:
                    # 페이지가 완전히 로드될 때까지 추가 대기
                    time.sleep(3)
                    
                    # 페이지를 스크롤하여 공감 버튼이 로드되도록 함
                    try:
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(1)
                        self.driver.execute_script("window.scrollTo(0, 0);")
                        time.sleep(1)
                    except:
                        pass
                    
                    # 공감 버튼을 여러 번 시도해서 찾기
                    for attempt in range(5):  # 3번에서 5번으로 증가
                        result = self.click_like_button()
                        if result:
                            like_success = True
                            print(f"[공감] 처리 성공 (시도 {attempt + 1})")
                            break
                        time.sleep(1.5)  # 재시도 전 대기 시간 증가
                    
                    if not like_success:
                        print("[공감] 버튼을 찾지 못하거나 클릭하지 못했습니다.")
                    
                    time.sleep(2)  # 공감 처리 대기
                except Exception as e:
                    error_msg = f"[공감] 처리 중 오류 발생: {str(e)}"
                    print(error_msg)
            
            # 3. 댓글 처리 (댓글 옵션이 활성화된 경우)
            comment_success = False
            comment_result = None
            if comment_enabled:
                try:
                    # 페이지가 완전히 로드될 때까지 추가 대기
                    time.sleep(2)
                    
                    # 페이지를 스크롤하여 댓글 영역이 로드되도록 함
                    try:
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(1)
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                        time.sleep(1)
                    except:
                        pass
                    
                    # 댓글 목록 준비 (없으면 기본 댓글 사용)
                    if comment_list is None or len(comment_list) == 0:
                        comment_list = ["잘 보고 갑니다!"]
                    
                    # 댓글 인덱스 계산 (순환)
                    actual_index = comment_index % len(comment_list)
                    comment_text = comment_list[actual_index]
                    
                    # 댓글 작성 시도
                    comment_result = self.write_comment(comment_text, comment_list, actual_index)
                    
                    if comment_result == "already_commented":
                        # 이미 작성한 댓글이 있으면 성공으로 처리하고 다음으로 넘어감
                        comment_success = True
                        print("[댓글] 이미 작성한 댓글이 있어 스킵합니다.")
                    elif comment_result:
                        comment_success = True
                        print(f"[댓글] 처리 성공: {comment_text}")
                    else:
                        comment_success = False
                        print("[댓글] 댓글을 달 수 없습니다. (댓글 영역을 찾지 못함)")
                    # 댓글을 달 수 없어도 실패로 처리하지 않고 다음 작업으로 진행
                    time.sleep(2)  # 댓글 처리 대기
                except Exception as e:
                    error_msg = f"[댓글] 처리 중 오류 발생: {str(e)}"
                    print(error_msg)
                    # 오류가 발생해도 다음 작업으로 진행
            
            # 공감만 체크되었거나 댓글만 체크된 경우 (이웃추가가 체크되지 않은 경우)
            if (like_enabled or comment_enabled) and not include_neighbor:
                self.close_current_tab()
                # 공감 성공 여부 확인
                if like_enabled and like_success:
                    return {'success': True, 'type': 'like', 'reason': '공감 처리 완료'}
                elif comment_enabled:
                    # 댓글은 실패해도 다음으로 넘어가므로 성공으로 처리
                    if comment_success:
                        reason = '댓글 처리 완료'
                        if comment_result == "already_commented":
                            reason = '댓글 처리 완료 (이미 작성된 댓글 있어 스킵)'
                        return {'success': True, 'type': 'comment', 'reason': reason}
                    else:
                        return {'success': True, 'type': 'comment', 'reason': '댓글 처리 완료 (댓글 영역을 찾지 못함)'}
                else:
                    return {'success': False, 'type': 'failed', 'reason': '공감/댓글 버튼을 찾지 못함'}
            
            # 이웃추가 버튼 찾기 (서로이웃 버튼은 이웃추가 버튼 클릭 후 나타날 수 있음)
            neighbor_button = self.find_neighbor_add_button()
            if not neighbor_button:
                self.close_current_tab()
                # 공감/댓글만 성공했어도 결과 반환
                if like_enabled and like_success:
                    return {'success': True, 'type': 'like', 'reason': '공감 처리 완료 (이웃추가 버튼 없음)'}
                elif comment_enabled:
                    return {'success': True, 'type': 'comment', 'reason': '댓글 처리 완료 (이웃추가 버튼 없음)'}
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
                    
                    # 서로이웃 메시지 입력 (파일이 있는 경우)
                    if neighbor_message_list and len(neighbor_message_list) > 0:
                        try:
                            # 메시지 인덱스 계산 (순환)
                            actual_message_index = neighbor_message_index % len(neighbor_message_list)
                            message_text = neighbor_message_list[actual_message_index]
                            
                            # 메시지 입력
                            if self.write_neighbor_message(message_text):
                                print(f"[서로이웃 메시지] 입력 성공: {message_text}")
                                time.sleep(1)
                            else:
                                print("[서로이웃 메시지] 입력 실패 (확인 버튼은 계속 진행)")
                        except Exception as e:
                            print(f"[서로이웃 메시지] 입력 중 오류: {str(e)} (확인 버튼은 계속 진행)")
                    
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
                    
                    # 서로이웃 메시지 입력 (파일이 있는 경우)
                    if neighbor_message_list and len(neighbor_message_list) > 0:
                        try:
                            # 메시지 인덱스 계산 (순환)
                            actual_message_index = neighbor_message_index % len(neighbor_message_list)
                            message_text = neighbor_message_list[actual_message_index]
                            
                            # 메시지 입력
                            if self.write_neighbor_message(message_text):
                                print(f"[서로이웃 메시지] 입력 성공: {message_text}")
                                time.sleep(1)
                            else:
                                print("[서로이웃 메시지] 입력 실패 (확인 버튼은 계속 진행)")
                        except Exception as e:
                            print(f"[서로이웃 메시지] 입력 중 오류: {str(e)} (확인 버튼은 계속 진행)")
                    
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
    
    def start_neighbor_add_work(self, include_neighbor=False, mutual_only=True, max_posts=10, delay=30, progress_callback=None, work_control=None, like_enabled=False, comment_enabled=False, comment_file_path=None, neighbor_file_path=None, log_callback=None):
        """
        서로이웃 추가 작업 시작
        
        Args:
            include_neighbor: 이웃추가 포함 옵션
            mutual_only: 서로이웃만 옵션
            max_posts: 최대 처리할 포스트 수
            delay: 각 작업 사이 딜레이 (초)
            progress_callback: 진행 상황 업데이트 콜백 함수 (success_count, fail_count, current_total, max_total)
            work_control: 작업 제어 딕셔너리 {'stop': bool, 'pause': bool}
            like_enabled: 공감 활성화 옵션
            comment_enabled: 댓글 작성 활성화 옵션
            comment_file_path: 댓글 파일 경로 (None이면 기본 댓글 사용)
            neighbor_file_path: 서로이웃 메시지 파일 경로 (None이면 메시지 입력 안함)
            log_callback: 로그 메시지 콜백 함수 (message)
        
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
            like_count = 0
            comment_count = 0
            total_posts = len(posts)
            
            # 댓글 목록 로드 (댓글 기능이 활성화된 경우)
            comment_list = None
            if comment_enabled:
                comment_list = self.load_comment_list(comment_file_path)
                if log_callback:
                    try:
                        log_callback(f"댓글 목록 로드 완료: {len(comment_list)}개")
                    except:
                        pass
            
            # 서로이웃 메시지 목록 로드 (파일이 있는 경우)
            neighbor_message_list = None
            if neighbor_file_path:
                neighbor_message_list = self.load_neighbor_message_list(neighbor_file_path)
                if neighbor_message_list:
                    if log_callback:
                        try:
                            log_callback(f"서로이웃 메시지 목록 로드 완료: {len(neighbor_message_list)}개")
                        except:
                            pass
                else:
                    if log_callback:
                        try:
                            log_callback("서로이웃 메시지 파일이 비어있거나 읽을 수 없습니다.")
                        except:
                            pass
            
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
                            'neighbor_count': neighbor_count,
                            'like_count': like_count,
                            'comment_count': comment_count
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
                                'neighbor_count': neighbor_count,
                                'like_count': like_count,
                                'comment_count': comment_count
                            }
                    
                    # 검색 결과 페이지로 돌아가기 (첫 번째 포스트가 아니고 새 탭이 열렸다면)
                    if i > 1 and len(self.driver.window_handles) > 1:
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        time.sleep(1)
                    
                    # 포스트 처리 (댓글 인덱스와 서로이웃 메시지 인덱스는 순환하여 사용)
                    if comment_list and len(comment_list) > 0:
                        comment_index = (i - 1) % len(comment_list)
                    else:
                        comment_list = ["잘 보고 갑니다!"]
                        comment_index = 0
                    
                    # 서로이웃 메시지 인덱스 계산 (순환)
                    neighbor_message_index = 0
                    if neighbor_message_list and len(neighbor_message_list) > 0:
                        neighbor_message_index = (i - 1) % len(neighbor_message_list)
                    
                    result = self.process_blog_post(post, include_neighbor, mutual_only, like_enabled, comment_enabled, comment_list, comment_index, neighbor_message_list, neighbor_message_index)
                    
                    if result['success']:
                        success_count += 1
                        if result['type'] == 'mutual':
                            mutual_count += 1
                            print(f"[{i}/{total_posts}] 서로이웃 추가 성공")
                        elif result['type'] == 'neighbor':
                            neighbor_count += 1
                            print(f"[{i}/{total_posts}] 일반 이웃추가 성공")
                        elif result['type'] == 'like':
                            like_count += 1
                            log_msg = f"[{i}/{total_posts}] 공감 처리 성공"
                            print(log_msg)
                            if log_callback:
                                try:
                                    log_callback(log_msg)
                                except:
                                    pass
                        elif result['type'] == 'comment':
                            comment_count += 1
                            # 이미 작성한 댓글이 있는지 확인
                            reason = result.get('reason', '')
                            if '이미 작성' in reason or '스킵' in reason:
                                log_msg = f"[{i}/{total_posts}] 댓글 처리 성공 (이미 작성된 댓글 있어 스킵)"
                            else:
                                log_msg = f"[{i}/{total_posts}] 댓글 처리 성공"
                            print(log_msg)
                            if log_callback:
                                try:
                                    log_callback(log_msg)
                                except:
                                    pass
                    else:
                        fail_count += 1
                        if result.get('type') == 'like':
                            log_msg = f"[{i}/{total_posts}] 공감 처리 실패: {result.get('reason', '알 수 없는 오류')}"
                            print(log_msg)
                            if log_callback:
                                try:
                                    log_callback(log_msg)
                                except:
                                    pass
                        elif result.get('type') == 'comment':
                            # 댓글은 실패해도 다음으로 넘어가므로 로그만 출력
                            reason = result.get('reason', '댓글을 달 수 없음')
                            if '이미 작성' in reason or '스킵' in reason:
                                log_msg = f"[{i}/{total_posts}] 댓글 처리: 이미 작성된 댓글이 있어 스킵"
                            else:
                                log_msg = f"[{i}/{total_posts}] 댓글 처리: {reason}"
                            print(log_msg)
                            if log_callback:
                                try:
                                    log_callback(log_msg)
                                except:
                                    pass
                        else:
                            print(f"[{i}/{total_posts}] 작업 실패: {result.get('reason', '알 수 없는 오류')}")
                    
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
                                    'neighbor_count': neighbor_count,
                                    'like_count': like_count,
                                    'comment_count': comment_count
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
                'neighbor_count': neighbor_count,
                'like_count': like_count,
                'comment_count': comment_count
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'작업 중 오류 발생: {str(e)}',
                'total': 0,
                'success_count': 0,
                'fail_count': 0
            }
