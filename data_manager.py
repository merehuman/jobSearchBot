#!/usr/bin/env python3
"""
Data Manager for Job Search Bot
Handles saving and managing job data in CSV format
"""

import pandas as pd
import os
import logging
from datetime import datetime
from typing import List, Dict, Any
from utils import clean_text, extract_salary_range, extract_qualifications

class DataManager:
    """Manages job data storage and retrieval"""
    
    def __init__(self):
        """Initialize the data manager"""
        self.logger = logging.getLogger(__name__)
        
        # Create output directory if it doesn't exist
        self.output_dir = "job_results"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Define CSV file paths
        self.internships_file = os.path.join(self.output_dir, "internships.csv")
        self.entry_level_file = os.path.join(self.output_dir, "entry_level_jobs.csv")
        
        # Define CSV columns
        self.columns = [
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
    
    def save_internships(self, internships: List[Dict[str, Any]]):
        """
        Save internship jobs to CSV file
        
        Args:
            internships: List of internship job dictionaries
        """
        try:
            if not internships:
                self.logger.info("No internships to save")
                return
            
            # Process and clean the data
            processed_internships = []
            for job in internships:
                processed_job = self._process_job_data(job)
                processed_internships.append(processed_job)
            
            # Create DataFrame
            df = pd.DataFrame(processed_internships, columns=self.columns)
            
            # Save to CSV
            df.to_csv(self.internships_file, index=False, encoding='utf-8')
            
            self.logger.info(f"Saved {len(internships)} internships to {self.internships_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving internships: {e}")
            raise
    
    def save_entry_level_jobs(self, entry_level_jobs: List[Dict[str, Any]]):
        """
        Save entry-level jobs to CSV file
        
        Args:
            entry_level_jobs: List of entry-level job dictionaries
        """
        try:
            if not entry_level_jobs:
                self.logger.info("No entry-level jobs to save")
                return
            
            # Process and clean the data
            processed_jobs = []
            for job in entry_level_jobs:
                processed_job = self._process_job_data(job)
                processed_jobs.append(processed_job)
            
            # Create DataFrame
            df = pd.DataFrame(processed_jobs, columns=self.columns)
            
            # Save to CSV
            df.to_csv(self.entry_level_file, index=False, encoding='utf-8')
            
            self.logger.info(f"Saved {len(entry_level_jobs)} entry-level jobs to {self.entry_level_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving entry-level jobs: {e}")
            raise
    
    def _process_job_data(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and clean job data for CSV storage
        
        Args:
            job: Raw job data dictionary
        
        Returns:
            Processed job data dictionary
        """
        # Extract and clean basic information
        title = clean_text(job.get('title', ''))
        company = clean_text(job.get('company', ''))
        location = clean_text(job.get('location', ''))
        description = clean_text(job.get('description', ''))
        url = job.get('url', '')
        date_posted = job.get('date_posted', 'No date')
        
        # Extract salary and qualifications from description
        salary = extract_salary_range(description)
        qualifications = extract_qualifications(description)
        
        # Current date for tracking when the job was found
        search_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            'job_title': title,
            'company': company,
            'location': location,
            'job_description': description,
            'qualifications': qualifications,
            'salary': salary,
            'job_url': url,
            'date_posted': date_posted,
            'search_date': search_date
        }
    
    def load_existing_jobs(self, file_path: str) -> pd.DataFrame:
        """
        Load existing jobs from CSV file
        
        Args:
            file_path: Path to the CSV file
        
        Returns:
            DataFrame with existing jobs
        """
        try:
            if os.path.exists(file_path):
                df = pd.read_csv(file_path, encoding='utf-8')
                self.logger.info(f"Loaded {len(df)} existing jobs from {file_path}")
                return df
            else:
                self.logger.info(f"No existing file found at {file_path}")
                return pd.DataFrame(columns=self.columns)
        except Exception as e:
            self.logger.error(f"Error loading existing jobs from {file_path}: {e}")
            return pd.DataFrame(columns=self.columns)
    
    def get_job_summary(self) -> Dict[str, int]:
        """
        Get summary of saved jobs
        
        Returns:
            Dictionary with counts of internships and entry-level jobs
        """
        summary = {
            'internships': 0,
            'entry_level_jobs': 0
        }
        
        try:
            # Count internships
            if os.path.exists(self.internships_file):
                internships_df = pd.read_csv(self.internships_file)
                summary['internships'] = len(internships_df)
            
            # Count entry-level jobs
            if os.path.exists(self.entry_level_file):
                entry_level_df = pd.read_csv(self.entry_level_file)
                summary['entry_level_jobs'] = len(entry_level_df)
                
        except Exception as e:
            self.logger.error(f"Error getting job summary: {e}")
        
        return summary
    
    def clear_old_results(self, days_old: int = 30):
        """
        Clear job results older than specified days
        
        Args:
            days_old: Number of days after which to clear old results
        """
        try:
            cutoff_date = datetime.now() - pd.Timedelta(days=days_old)
            
            # Clear old internships
            if os.path.exists(self.internships_file):
                df = pd.read_csv(self.internships_file)
                df['search_date'] = pd.to_datetime(df['search_date'])
                df = df[df['search_date'] > cutoff_date]
                df.to_csv(self.internships_file, index=False, encoding='utf-8')
                self.logger.info(f"Cleared old internships, kept {len(df)} recent ones")
            
            # Clear old entry-level jobs
            if os.path.exists(self.entry_level_file):
                df = pd.read_csv(self.entry_level_file)
                df['search_date'] = pd.to_datetime(df['search_date'])
                df = df[df['search_date'] > cutoff_date]
                df.to_csv(self.entry_level_file, index=False, encoding='utf-8')
                self.logger.info(f"Cleared old entry-level jobs, kept {len(df)} recent ones")
                
        except Exception as e:
            self.logger.error(f"Error clearing old results: {e}") 