#!/usr/bin/env python3
"""
LinkedIn Job Searcher
Handles LinkedIn job searching with authentication and job categorization
"""

import time
import random
import logging
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlencode, urljoin
from typing import List, Dict, Any
from utils import clean_text, is_internship_job

class LinkedInJobSearcher:
    """LinkedIn job search functionality with authentication"""
    
    def __init__(self, email: str, password: str):
        """
        Initialize the LinkedIn job searcher
        
        Args:
            email: LinkedIn email
            password: LinkedIn password
        """
        self.email = email
        self.password = password
        self.logger = logging.getLogger(__name__)
        self.driver = None
        self.session = requests.Session()
        
        # Setup browser-like headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Track seen jobs to avoid duplicates
        self.seen_jobs = set()
    
    def __enter__(self):
        """Context manager entry"""
        self._setup_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self._cleanup()
    
    def _setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Use webdriver-manager to handle driver installation
            self.driver = webdriver.Chrome(
                ChromeDriverManager().install(),
                options=chrome_options
            )
            
            # Hide automation indicators
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("Chrome WebDriver setup completed")
            
        except Exception as e:
            self.logger.error(f"Error setting up WebDriver: {e}")
            raise
    
    def _cleanup(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver closed")
            except Exception as e:
                self.logger.error(f"Error closing WebDriver: {e}")
    
    def login_to_linkedin(self) -> bool:
        """
        Login to LinkedIn using provided credentials
        
        Returns:
            True if login successful, False otherwise
        """
        try:
            self.logger.info("Attempting to login to LinkedIn...")
            
            # Navigate to LinkedIn login page
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(2)
            
            # Wait for login form and enter credentials
            wait = WebDriverWait(self.driver, 10)
            
            # Enter email
            email_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
            email_field.clear()
            email_field.send_keys(self.email)
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url:
                self.logger.info("LinkedIn login successful")
                return True
            else:
                self.logger.error("LinkedIn login failed")
                return False
                
        except TimeoutException:
            self.logger.error("Timeout during LinkedIn login")
            return False
        except Exception as e:
            self.logger.error(f"Error during LinkedIn login: {e}")
            return False
    
    def search_jobs(self, keyword: str, location: str, max_jobs: int = 20) -> List[Dict[str, Any]]:
        """
        Search for jobs on LinkedIn
        
        Args:
            keyword: Job search keyword
            location: Job location
            max_jobs: Maximum number of jobs to retrieve
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        try:
            # Ensure we're logged in
            if not self._is_logged_in():
                if not self.login_to_linkedin():
                    self.logger.error("Failed to login to LinkedIn")
                    return jobs
            
            # Navigate to jobs page
            self.logger.info(f"Searching for '{keyword}' in '{location}'")
            self.driver.get("https://www.linkedin.com/jobs")
            time.sleep(3)
            
            # Build search URL
            search_params = {
                'keywords': keyword,
                'location': location,
                'refresh': 'true',
                'position': '1',
                'pageNum': '0',
                'f_TPR': 'r604800',  # Last week
                'sortBy': 'DD'  # Sort by date posted
            }
            
            search_url = f"https://www.linkedin.com/jobs/search?{urlencode(search_params)}"
            self.driver.get(search_url)
            time.sleep(3)
            
            # Scroll to load more jobs
            self._scroll_to_load_jobs(max_jobs)
            
            # Extract job listings
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, "div.base-card")
            
            for i, card in enumerate(job_cards[:max_jobs]):
                try:
                    job = self._extract_job_from_card(card)
                    if job and self._is_new_job(job):
                        jobs.append(job)
                        self.seen_jobs.add(job['url'])
                        
                    # Add delay between processing jobs
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    self.logger.error(f"Error processing job card {i}: {e}")
                    continue
            
            self.logger.info(f"Found {len(jobs)} new jobs for '{keyword}' in '{location}'")
            
        except Exception as e:
            self.logger.error(f"Error searching jobs: {e}")
        
        return jobs
    
    def _is_logged_in(self) -> bool:
        """Check if currently logged into LinkedIn"""
        try:
            # Check for login indicators
            self.driver.get("https://www.linkedin.com/feed")
            time.sleep(2)
            return "feed" in self.driver.current_url
        except:
            return False
    
    def _scroll_to_load_jobs(self, max_jobs: int):
        """Scroll down to load more job listings"""
        try:
            jobs_loaded = 0
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while jobs_loaded < max_jobs:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Count current jobs
                current_jobs = len(self.driver.find_elements(By.CSS_SELECTOR, "div.base-card"))
                jobs_loaded = current_jobs
                
                # Check if we've reached the bottom
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
        except Exception as e:
            self.logger.error(f"Error scrolling to load jobs: {e}")
    
    def _extract_job_from_card(self, card) -> Dict[str, Any]:
        """Extract job information from a job card element"""
        try:
            # Extract basic information
            title = self._safe_extract_text(card, "h3.base-search-card__title")
            company = self._safe_extract_text(card, "h4.base-search-card__subtitle")
            location = self._safe_extract_text(card, "span.job-search-card__location")
            
            # Get job URL
            url = self._safe_extract_url(card, "a.base-card__full-link")
            
            if not title or not url:
                return None
            
            # Get job description
            description = self._get_job_description(url)
            
            # Extract additional information
            date_posted = self._safe_extract_text(card, "time.job-search-card__listdate")
            if not date_posted:
                date_posted = "No date"
            
            job = {
                'title': clean_text(title),
                'company': clean_text(company) if company else "Company not specified",
                'location': clean_text(location) if location else "Location not specified",
                'description': clean_text(description),
                'url': url,
                'date_posted': clean_text(date_posted)
            }
            
            return job
            
        except Exception as e:
            self.logger.error(f"Error extracting job from card: {e}")
            return None
    
    def _safe_extract_text(self, element, selector: str) -> str:
        """Safely extract text from an element"""
        try:
            found = element.find_element(By.CSS_SELECTOR, selector)
            return found.text.strip()
        except NoSuchElementException:
            return ""
        except Exception:
            return ""
    
    def _safe_extract_url(self, element, selector: str) -> str:
        """Safely extract URL from an element"""
        try:
            found = element.find_element(By.CSS_SELECTOR, selector)
            return found.get_attribute('href')
        except NoSuchElementException:
            return ""
        except Exception:
            return ""
    
    def _get_job_description(self, url: str) -> str:
        """Get full job description from job page"""
        try:
            if not url:
                return "No description available"
            
            # Use requests session for faster description retrieval
            response = self.session.get(url)
            if response.status_code != 200:
                return "Failed to load description"
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try multiple selectors for job description
            desc_selectors = [
                'div.show-more-less-html__markup',
                'div.description__text',
                'div.job-description',
                'div[data-job-description]'
            ]
            
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    return desc_elem.get_text(strip=True)
            
            return "No description available"
            
        except Exception as e:
            self.logger.error(f"Error getting job description: {e}")
            return "Error loading description"
    
    def _is_new_job(self, job: Dict[str, Any]) -> bool:
        """Check if job has been seen before"""
        return job['url'] not in self.seen_jobs
    
    def is_internship(self, job: Dict[str, Any]) -> bool:
        """
        Determine if a job is an internship
        
        Args:
            job: Job dictionary
        
        Returns:
            True if it's an internship, False otherwise
        """
        title = job.get('title', '').lower()
        description = job.get('description', '').lower()
        
        return is_internship_job(title, description) 