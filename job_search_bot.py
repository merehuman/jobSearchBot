import os
import time
import random
import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import logging
import signal
import sys
from urllib.parse import urlencode

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LinkedInJobSearchBot:
    def __init__(self):
        # Job search parameters
        self.job_types = [
            "software engineer",
            "software developer",
            "engine",
            "software",
            "C++"
        ]
        self.locations = ["Berkeley", "Oakland", "San Francisco", "Remote"]
        
        # Setup requests session with more browser-like headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
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
        })
        
        # Create output directory
        self.output_dir = "job_search_results"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load previous results
        self.jobs_df = self._load_previous_results()
        
        # Track seen jobs using multiple fields
        self.seen_jobs = self._initialize_seen_jobs()
        
        # Flag for graceful shutdown
        self.should_stop = False
        
        # Setup signal handler for Ctrl+C
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        logger.info("\nStopping job search gracefully... Please wait...")
        self.should_stop = True

    def _create_job_identifier(self, title: str, company: str, location: str) -> str:
        """Create a unique identifier for a job based on multiple fields"""
        # Clean and normalize the strings
        title = title.lower().strip()
        company = company.lower().strip()
        location = location.lower().strip()
        return f"{title}|{company}|{location}"

    def _search_linkedin(self, job_type: str, location: str) -> list:
        """Perform a single job search"""
        jobs = []
        
        try:
            # Add a longer delay between searches
            time.sleep(random.uniform(3, 5))
            
            # Format the search URL with additional parameters
            params = {
                'keywords': job_type,
                'location': location,
                'refresh': 'true',
                'position': '1',
                'pageNum': '0',
                'f_TPR': 'r604800',  # Last week (7 days = 604800 seconds)
                'sortBy': 'DD'  # Sort by date posted
            }
            search_url = f"https://www.linkedin.com/jobs/search?{urlencode(params)}"
            
            # Visit the main jobs page first
            self.session.get("https://www.linkedin.com/jobs")
            time.sleep(random.uniform(1, 2))
            
            # Now perform the search
            response = self.session.get(search_url, 
                headers={'Referer': 'https://www.linkedin.com/jobs'})
            
            if response.status_code != 200:
                logger.error(f"Failed to get search results: {response.status_code}")
                if response.status_code == 999:
                    logger.info("LinkedIn rate limit detected. Waiting longer between requests...")
                    time.sleep(random.uniform(10, 15))
                return jobs
            
            soup = BeautifulSoup(response.text, 'html.parser')
            job_cards = soup.find_all('div', {'class': ['base-card', 'base-search-card', 'job-search-card']})
            
            for card in job_cards[:10]:  # Limit to first 10 results per search
                if self.should_stop:
                    break
                    
                try:
                    # Extract job details with multiple fallback selectors
                    title = self._extract_text(card, [
                        'h3.base-search-card__title',
                        'h3.job-search-card__title',
                        'a.base-card__full-link'
                    ])
                    
                    company = self._extract_text(card, [
                        'h4.base-search-card__subtitle',
                        'a.job-search-card__subtitle-link',
                        'a[data-tracking-control-name="public_jobs_company_name"]'
                    ])
                    
                    job_location = self._extract_text(card, [
                        'span.job-search-card__location',
                        'div.base-search-card__metadata span'
                    ])
                    
                    # Get URL with fallbacks
                    url = self._extract_url(card, [
                        'a.base-card__full-link',
                        'a.job-search-card__title-link'
                    ])
                    
                    # Skip if we couldn't get essential information
                    if not title or not url:
                        logger.debug(f"Skipping job - missing essential info. Title: {title}, URL: {url}")
                        continue
                        
                    # Use provided location if we couldn't extract it
                    if not job_location:
                        job_location = location
                        
                    # Use "Company not specified" if we couldn't extract company
                    if not company:
                        company = "Company not specified"
                    
                    # Create unique identifier for this job
                    job_id = self._create_job_identifier(title, company, job_location)
                    
                    # Skip if we've seen this job before
                    if job_id in self.seen_jobs or url in self.seen_jobs:
                        continue
                        
                    # Mark as seen using both identifiers
                    self.seen_jobs.add(job_id)
                    if url:
                        self.seen_jobs.add(url)
                    
                    # Get job details
                    description = self._get_job_description(url) if url else 'No description'
                    
                    job = {
                        'title': title,
                        'company': company,
                        'location': job_location,
                        'description': description,
                        'url': url,
                        'date_posted': self._extract_date(card),
                        'salary': self._extract_salary(card)
                    }
                    
                    jobs.append(job)
                    logger.info(f"New job found: {title} at {company} in {job_location}")
                    
                    if not self.should_stop:
                        # Add small delay between processing jobs
                        time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    logger.error(f"Error processing job card: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error in LinkedIn search: {e}")
        
        return jobs

    def _extract_text(self, element, selectors):
        """Extract text using multiple possible selectors"""
        for selector in selectors:
            try:
                found = element.select_one(selector)
                if found:
                    text = found.get_text(strip=True)
                    # Check for various invalid text patterns
                    if text and not text.startswith('*') and not text.startswith('...'):
                        # Clean up the text
                        text = text.replace('*', '').replace('...', '').strip()
                        if text and len(text) > 1:  # Ensure we have meaningful text
                            return text
            except Exception:
                continue
        return None

    def _extract_url(self, element, selectors):
        """Extract URL using multiple possible selectors"""
        for selector in selectors:
            try:
                found = element.select_one(selector)
                if found and 'href' in found.attrs:
                    return found['href']
            except Exception:
                continue
        return None

    def _extract_date(self, card):
        """Extract posting date with fallbacks"""
        try:
            date_elem = card.find('time', {'class': ['job-search-card__listdate', 'job-posted-date']})
            if date_elem:
                return date_elem.get('datetime', 'No date')
        except Exception:
            pass
        return 'No date'

    def _extract_salary(self, card):
        """Extract salary information with fallbacks"""
        try:
            salary_elem = card.find('span', {'class': ['job-search-card__salary-info', 'base-search-card__metadata']})
            if salary_elem:
                return salary_elem.get_text(strip=True)
        except Exception:
            pass
        return 'Salary not specified'

    def _get_job_description(self, url: str) -> str:
        """Get the full job description"""
        try:
            if not url:
                return "No description available"
                
            response = self.session.get(url)
            if response.status_code != 200:
                return "Failed to load description"
                
            soup = BeautifulSoup(response.text, 'html.parser')
            desc_elem = soup.find('div', class_='show-more-less-html__markup')
            return desc_elem.get_text(strip=True) if desc_elem else "No description available"
            
        except Exception as e:
            logger.error(f"Error getting job description: {e}")
            return "Error loading description"

    def _save_jobs(self, jobs: list):
        """Add jobs to the DataFrame, ensuring no duplicates"""
        if not jobs:
            return
            
        # Convert new jobs to DataFrame
        new_df = pd.DataFrame(jobs)
        
        # Remove any duplicates based on URL or title+company+location combination
        if not self.jobs_df.empty:
            # Remove duplicates based on URL
            new_df = new_df[~new_df['url'].isin(self.jobs_df['url'])]
            
            # Remove duplicates based on title+company+location
            existing_identifiers = set(
                self.jobs_df.apply(
                    lambda x: self._create_job_identifier(x['title'], x['company'], x['location']), 
                    axis=1
                )
            )
            new_df = new_df[
                ~new_df.apply(
                    lambda x: self._create_job_identifier(x['title'], x['company'], x['location']) in existing_identifiers,
                    axis=1
                )
            ]
        
        # Add new jobs to main DataFrame
        self.jobs_df = pd.concat([self.jobs_df, new_df], ignore_index=True)

    def search_jobs(self):
        """Search for jobs on LinkedIn"""
        logger.info("Starting job search... Press Ctrl+C to stop")
        initial_job_count = len(self.jobs_df)
        
        try:
            for job_type in self.job_types:
                if self.should_stop:
                    break
                    
                for location in self.locations:
                    if self.should_stop:
                        break
                        
                    try:
                        logger.info(f"Searching for {job_type} in {location}")
                        new_jobs = self._search_linkedin(job_type, location)
                        if new_jobs:
                            self._save_jobs(new_jobs)
                            
                        if not self.should_stop:
                            # Add random delay between searches
                            time.sleep(random.uniform(2, 4))
                            
                    except Exception as e:
                        logger.error(f"Error searching for {job_type} in {location}: {e}")
            
        finally:
            final_job_count = len(self.jobs_df)
            new_jobs_found = final_job_count - initial_job_count
            
            if new_jobs_found > 0:
                self._save_to_csv()
                logger.info(f"Found {new_jobs_found} new unique jobs")
            else:
                logger.info("No new jobs found")

    def _load_previous_results(self) -> pd.DataFrame:
        """Load all previous results from CSV files"""
        try:
            # Get all CSV files in the output directory
            csv_files = [f for f in os.listdir(self.output_dir) if f.endswith('.csv')]
            
            if not csv_files:
                logger.info("No previous results found")
                return pd.DataFrame(columns=[
                    'title', 'company', 'location', 'description', 
                    'salary', 'url', 'date_posted'
                ])
            
            # Read and combine all CSV files
            all_jobs = []
            for csv_file in csv_files:
                try:
                    df = pd.read_csv(os.path.join(self.output_dir, csv_file))
                    all_jobs.append(df)
                except Exception as e:
                    logger.error(f"Error reading {csv_file}: {e}")
            
            if all_jobs:
                combined_df = pd.concat(all_jobs, ignore_index=True)
                # Remove duplicates based on URL and title+company+location
                combined_df = combined_df.drop_duplicates(subset=['url'], keep='first')
                combined_df = combined_df.drop_duplicates(
                    subset=['title', 'company', 'location'], 
                    keep='first'
                )
                logger.info(f"Loaded {len(combined_df)} previous job listings")
                return combined_df
            
            return pd.DataFrame(columns=[
                'title', 'company', 'location', 'description', 
                'salary', 'url', 'date_posted'
            ])
            
        except Exception as e:
            logger.error(f"Error loading previous results: {e}")
            return pd.DataFrame(columns=[
                'title', 'company', 'location', 'description', 
                'salary', 'url', 'date_posted'
            ])

    def _initialize_seen_jobs(self) -> set:
        """Initialize set of seen jobs from previous results"""
        seen = set()
        
        # Add URLs to seen set
        if not self.jobs_df.empty:
            seen.update(self.jobs_df['url'].dropna().tolist())
            
            # Add title+company+location combinations
            for _, row in self.jobs_df.iterrows():
                job_id = self._create_job_identifier(
                    row['title'], row['company'], row['location']
                )
                seen.add(job_id)
        
        return seen

    def _save_to_csv(self):
        """Save new results to CSV file"""
        try:
            if self.jobs_df.empty:
                logger.info("No jobs found to save")
                return
            
            # Get the latest jobs (ones not in previous files)
            previous_urls = set()
            csv_files = [f for f in os.listdir(self.output_dir) if f.endswith('.csv')]
            for csv_file in csv_files:
                try:
                    df = pd.read_csv(os.path.join(self.output_dir, csv_file))
                    previous_urls.update(df['url'].dropna().tolist())
                except Exception:
                    continue
            
            # Filter for only new jobs
            new_jobs = self.jobs_df[~self.jobs_df['url'].isin(previous_urls)]
            
            if new_jobs.empty:
                logger.info("No new unique jobs to save")
                return
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.output_dir, f"linkedin_jobs_{timestamp}.csv")
            
            new_jobs.to_csv(filename, index=False, encoding='utf-8')
            logger.info(f"Saved {len(new_jobs)} new unique jobs to {filename}")
                
        except Exception as e:
            logger.error(f"Error saving results: {e}")

def main():
    try:
        # Create and run the job search bot
        bot = LinkedInJobSearchBot()
        bot.search_jobs()
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 