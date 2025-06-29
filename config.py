#!/usr/bin/env python3
"""
Configuration settings for the Job Search Bot
"""

import os
from typing import List

class Config:
    """Configuration class for the job search bot"""
    
    # LinkedIn settings
    LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"
    LINKEDIN_JOBS_URL = "https://www.linkedin.com/jobs"
    LINKEDIN_FEED_URL = "https://www.linkedin.com/feed"
    
    # Search settings
    DEFAULT_MAX_JOBS_PER_SEARCH = 20
    DEFAULT_SEARCH_DELAY = (2, 4)  # Random delay range in seconds
    DEFAULT_JOB_PROCESSING_DELAY = (1, 2)  # Delay between processing jobs
    
    # Time settings
    LOGIN_WAIT_TIME = 5  # Seconds to wait after login
    PAGE_LOAD_WAIT_TIME = 3  # Seconds to wait for page loads
    SCROLL_WAIT_TIME = 2  # Seconds to wait between scrolls
    
    # WebDriver settings
    CHROME_OPTIONS = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled",
        "--disable-extensions",
        "--disable-plugins",
        "--disable-images",
        "--disable-javascript",  # Disable JS for faster loading
    ]
    
    # Job categorization keywords
    INTERNSHIP_KEYWORDS = [
        'intern', 'internship', 'co-op', 'coop', 'student', 'graduate',
        'entry level', 'entry-level', 'junior', 'trainee', 'apprentice'
    ]
    
    # Salary extraction patterns
    SALARY_PATTERNS = [
        r'\$[\d,]+(?:-\$[\d,]+)?\s*(?:per\s+)?(?:year|month|hour|week)',
        r'\$[\d,]+(?:k|K)\s*(?:per\s+)?(?:year|month)',
        r'[\d,]+(?:k|K)\s*-\s*[\d,]+(?:k|K)\s*(?:per\s+)?(?:year|month)',
        r'salary[:\s]*\$?[\d,]+(?:-\$?[\d,]+)?',
        r'compensation[:\s]*\$?[\d,]+(?:-\$?[\d,]+)?'
    ]
    
    # Qualification keywords
    QUALIFICATION_KEYWORDS = [
        'requirements', 'qualifications', 'skills', 'experience', 
        'education', 'degree', 'certification', 'preferred', 'must have'
    ]
    
    # File paths
    OUTPUT_DIR = "job_results"
    LOGS_DIR = "logs"
    INTERNSHIPS_FILE = os.path.join(OUTPUT_DIR, "internships.csv")
    ENTRY_LEVEL_FILE = os.path.join(OUTPUT_DIR, "entry_level_jobs.csv")
    
    # CSV columns
    CSV_COLUMNS = [
        'job_title',
        'company',
        'location', 
        'job_description',
        'qualifications',
        'salary',
        'job_url',
        'date_posted',
        'search_date'
    ]
    
    # User agent strings
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    ]
    
    # Request headers
    DEFAULT_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }
    
    # Logging settings
    LOG_LEVEL = "INFO"
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Data retention
    DEFAULT_RETENTION_DAYS = 30  # Days to keep old job results
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.LOGS_DIR, exist_ok=True)
    
    @classmethod
    def get_user_agent(cls) -> str:
        """Get a random user agent string"""
        import random
        return random.choice(cls.USER_AGENTS) 