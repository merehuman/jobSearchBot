from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re
# Move Selenium imports to the top so all methods can use them
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    webdriver = Options = Service = By = WebDriverWait = EC = ChromeDriverManager = None

class GenericCareerParser:
    """
    Generic parser for standard company careers pages.
    Uses Selenium to handle JavaScript-rendered content and navigate to job search interfaces.
    """
    def __init__(self, base_url, delay=2, use_selenium=True):
        self.base_url = base_url
        self.delay = delay
        self.use_selenium = use_selenium
        self.session = None
        if not use_selenium:
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            })

    def __enter__(self):
        if self.use_selenium:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        else:
            self.driver = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.use_selenium and hasattr(self, 'driver') and self.driver:
            self.driver.quit()

    def is_scraping_allowed(self):
        """Check robots.txt for scraping permission."""
        parsed = urlparse(self.base_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        try:
            if self.use_selenium:
                import requests
                session = requests.Session()
                session.headers.update({'User-Agent': 'Mozilla/5.0'})
                resp = session.get(robots_url, timeout=5)
            else:
                resp = self.session.get(robots_url, timeout=5)
            if resp.status_code != 200:
                return True  # If robots.txt not found, assume allowed
            robots_txt = resp.text.lower()
            # Look for Disallow rules for /careers or /jobs
            for line in robots_txt.splitlines():
                if line.startswith('disallow:') and ('/careers' in line or '/jobs' in line):
                    return False
            return True
        except Exception:
            return True  # If error, assume allowed

    def parse_jobs(self, keywords=None):
        """
        Parse the careers page and extract job postings.
        Navigates through landing pages to find job search interface.
        Optionally filter by keywords (list of strings).
        Returns a list of job dicts.
        """
        if not self.is_scraping_allowed():
            print(f"Scraping not allowed by robots.txt for {self.base_url}")
            return []
        
        if not self.use_selenium:
            print("Selenium required for navigation. Falling back to basic parsing.")
            return self._basic_parse_jobs(keywords)
        
        try:
            with self:
                return self._selenium_parse_jobs(keywords)
        except Exception as e:
            print(f"Selenium parsing failed: {e}. Falling back to basic parsing.")
            return self._basic_parse_jobs(keywords)

    def _selenium_parse_jobs(self, keywords=None):
        """Use Selenium to navigate and parse jobs."""
        print(f"Loading careers page: {self.base_url}")
        self.driver.get(self.base_url)
        time.sleep(self.delay + 2)
        
        # Step 1: Try to navigate to job search interface
        self._navigate_to_job_search()
        
        # Step 2: If keywords provided, try to use search functionality
        if keywords:
            self._use_search_functionality(keywords)
        
        # Step 3: Extract jobs from current page
        return self._extract_jobs_from_current_page(keywords)

    def _navigate_to_job_search(self, max_depth=5):
        """Iteratively navigate through links/buttons with relevant keywords until a search bar is found or no further navigation is possible."""
        print("Starting iterative navigation to job search interface...")
        navigation_keywords = [
            "explore opportunities", "see open roles", "find jobs", "view jobs", "join us", "search jobs", "search careers",
            "explore", "opportunity", "opportunities", "search", "job", "career", "opening", "position"
        ]
        navigation_keywords = [kw.lower() for kw in navigation_keywords]
        main_keywords = ["career", "job", "opportunit", "explore", "opening", "position"]
        cookie_keywords = [
            'decline', 'reject', 'no thanks', 'do not accept', 'deny', 'refuse'
        ]
        depth = 0
        while depth < max_depth:
            print(f"\n[Navigation Depth {depth}] URL: {self.driver.current_url}")
            # Step 0: Try to dismiss cookie popups
            try:
                buttons = self.driver.find_elements(By.TAG_NAME, 'button')
                for button in buttons:
                    text = button.text.strip().lower()
                    if any(word in text for word in cookie_keywords):
                        print(f"Clicking cookie popup button: '{button.text}'")
                        button.click()
                        time.sleep(2)
                        break
            except Exception as e:
                print(f"Error handling cookie popup: {e}")

            # Step 1: Check for search bar
            search_selectors = [
                "input[type='text']",
                "input[type='search']",
                "input[placeholder*='search']",
                "input[placeholder*='keyword']",
                "input[placeholder*='job']",
                "input[name*='search']",
                "input[name*='keyword']",
                "input[id*='search']",
                "input[id*='keyword']"
            ]
            found_search = False
            for selector in search_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            print(f"Found search input: {element.get_attribute('placeholder') or element.get_attribute('name') or element.get_attribute('id')}")
                            found_search = True
                            break
                    if found_search:
                        break
                except Exception as e:
                    continue
            if found_search:
                print("Search bar found. Stopping navigation.")
                return

            # Step 2: Find navigation elements (a, button, and clickable custom elements)
            clickable_elements = self.driver.find_elements(By.XPATH, "//*[self::a or self::button or @role='button' or @tabindex]")
            nav_links = []
            for elem in clickable_elements:
                try:
                    # Gather all possible text/attributes
                    texts = [elem.text.strip().lower()]
                    for attr in ["aria-label", "title", "alt"]:
                        val = elem.get_attribute(attr)
                        if val:
                            texts.append(val.strip().lower())
                    # Check data-* attributes
                    for attr_name in elem.get_property('attributes'):
                        if attr_name.name.startswith('data-'):
                            val = elem.get_attribute(attr_name.name)
                            if val:
                                texts.append(val.strip().lower())
                    # Combine all text/attributes into one string for regex search
                    combined = " ".join(texts)
                    for kw in navigation_keywords:
                        if re.search(rf"\b{re.escape(kw)}\b", combined, re.IGNORECASE):
                            print(f"Found navigation candidate: '{combined}' (matches '{kw}')")
                            nav_links.append(elem)
                            break
                except Exception as e:
                    continue
            if not nav_links:
                print("No further navigation links found. Stopping navigation.")
                return
            # Step 3: Click the first navigation element
            link = nav_links[0]
            try:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
                time.sleep(1)
                link.click()
                print("Clicked navigation element.")
                time.sleep(3)
            except Exception as e:
                href = link.get_attribute('href')
                print(f"Element not clickable, using driver.get as fallback: {e}")
                if href:
                    self.driver.get(href)
                    time.sleep(3)
            depth += 1
        print("Maximum navigation depth reached. Stopping navigation.")
        return

    def _use_search_functionality(self, keywords):
        """Try to use search bar to enter keywords."""
        print(f"Looking for search functionality to enter keywords: {keywords}")
        
        # Try to find search input fields
        search_selectors = [
            "input[type='text']",
            "input[type='search']", 
            "input[placeholder*='search']",
            "input[placeholder*='keyword']",
            "input[placeholder*='job']",
            "input[name*='search']",
            "input[name*='keyword']",
            "input[id*='search']",
            "input[id*='keyword']"
        ]
        
        search_input = None
        for selector in search_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        search_input = element
                        print(f"Found search input: {element.get_attribute('placeholder') or element.get_attribute('name') or element.get_attribute('id')}")
                        break
                if search_input:
                    break
            except:
                continue
        
        if search_input:
            try:
                # Clear and enter keywords
                search_input.clear()
                keyword_text = ' '.join(keywords)
                search_input.send_keys(keyword_text)
                print(f"Entered keywords: {keyword_text}")
                
                # Try to submit search
                search_input.submit()
                time.sleep(3)
                
                # Also try to find and click search button
                search_button_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button:contains('Search')",
                    "button:contains('Find')",
                    "button:contains('Go')"
                ]
                
                for selector in search_button_selectors:
                    try:
                        buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for button in buttons:
                            if button.is_displayed():
                                button.click()
                                print("Clicked search button")
                                time.sleep(3)
                                break
                    except:
                        continue
                        
            except Exception as e:
                print(f"Error using search functionality: {e}")

    def _extract_jobs_from_current_page(self, keywords=None):
        """Extract jobs from the current page."""
        print("Extracting jobs from current page...")
        
        # Scroll to load any lazy-loaded content
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Get page content
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        
        jobs = []
        
        # Try multiple methods to find job listings
        job_elements = []
        
        # Method 1: Look for job cards with common class names
        job_elements = soup.find_all(['div', 'li', 'article'], class_=re.compile(r'(job|position|opening|listing|card)', re.I))
        
        # Method 2: Look for links with job-like text
        if not job_elements:
            job_elements = soup.find_all('a', href=True, text=re.compile(r'(engineer|developer|designer|manager|analyst|specialist)', re.I))
        
        # Method 3: Look for any elements containing job-related text
        if not job_elements:
            job_text_elements = soup.find_all(text=re.compile(r'(engineer|developer|designer|manager|analyst|specialist)', re.I))
            for text_elem in job_text_elements:
                parent = text_elem.parent
                if parent and parent.name in ['div', 'li', 'article', 'a']:
                    job_elements.append(parent)
        
        print(f"Found {len(job_elements)} potential job elements")
        
        # Extract job information
        for elem in job_elements:
            title = self._extract_title(elem)
            location = self._extract_location(elem)
            url = self._extract_url(elem)
            description = self._extract_description(elem)
            
            if not title:
                continue
                
            job = {
                'title': title,
                'location': location or '',
                'description': description or '',
                'url': urljoin(self.driver.current_url, url) if url else self.driver.current_url
            }
            
            # Filter by keywords if provided
            if not keywords or any(kw.lower() in (title + description).lower() for kw in keywords):
                jobs.append(job)
        
        return jobs

    def _basic_parse_jobs(self, keywords=None):
        """Basic parsing without Selenium navigation."""
        html = None
        try:
            import requests
            resp = requests.get(self.base_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            })
            time.sleep(self.delay)
            html = resp.text
        except Exception as e:
            print(f"Error loading page with requests: {e}")
            return []
        
        soup = BeautifulSoup(html, 'lxml')
        jobs = []
        
        # Try to find job cards, tables, or lists
        job_elements = soup.find_all(['div', 'li', 'tr'], class_=re.compile(r'(job|position|opening)', re.I))
        if not job_elements:
            # Fallback: look for links with job-like text
            job_elements = soup.find_all('a', href=True, text=re.compile(r'(job|opening|position)', re.I))
        
        for elem in job_elements:
            title = self._extract_title(elem)
            location = self._extract_location(elem)
            url = self._extract_url(elem)
            description = self._extract_description(elem)
            if not title:
                continue
            job = {
                'title': title,
                'location': location or '',
                'description': description or '',
                'url': urljoin(self.base_url, url) if url else self.base_url
            }
            if not keywords or any(kw.lower() in (title + description).lower() for kw in keywords):
                jobs.append(job)
        return jobs

    def _extract_title(self, elem):
        # Try to find a title in the element or its children
        for tag in ['h2', 'h3', 'a', 'span', 'div']:
            t = elem.find(tag)
            if t and t.get_text(strip=True):
                return t.get_text(strip=True)
        if elem.get_text(strip=True):
            return elem.get_text(strip=True)[:100]
        return None

    def _extract_location(self, elem):
        # Look for location in text or sub-elements
        text = elem.get_text(" ", strip=True)
        match = re.search(r'(remote|[A-Z][a-z]+,? [A-Z]{2,}|[A-Z][a-z]+,? [A-Z][a-z]+)', text)
        if match:
            return match.group(0)
        return None

    def _extract_url(self, elem):
        # Try to find a link in the element
        a = elem.find('a', href=True)
        if a:
            return a['href']
        return None

    def _extract_description(self, elem):
        # Try to get a short description
        ps = elem.find_all('p')
        if ps:
            return ' '.join(p.get_text(strip=True) for p in ps)
        return elem.get_text(" ", strip=True)[:300] 