#!/usr/bin/env python3
"""
Job Search Bot - Main Entry Point
A LinkedIn job search bot that prompts for user credentials and search preferences.
"""

import os
import sys
from job_searcher import LinkedInJobSearcher
from data_manager import DataManager
from utils import get_user_input, validate_credentials, setup_logging
import logging

def main():
    """Main function to run the job search bot"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("=" * 60)
    print("           LINKEDIN JOB SEARCH BOT")
    print("=" * 60)
    print()
    
    try:
        # Get user credentials
        print("Please enter your LinkedIn credentials:")
        email = get_user_input("Email: ")
        password = get_user_input("Password: ", is_password=True)
        
        # Validate credentials format
        if not validate_credentials(email, password):
            print("Invalid credentials format. Please check your email and password.")
            return
        
        # Get search keywords
        print("\nEnter job search keywords (separated by commas):")
        keywords_input = get_user_input("Keywords: ")
        keywords = [keyword.strip() for keyword in keywords_input.split(',') if keyword.strip()]
        
        if not keywords:
            print("No valid keywords provided. Exiting.")
            return
        
        # Get location preferences
        print("\nEnter job location preferences (separated by commas):")
        locations_input = get_user_input("Locations: ")
        locations = [location.strip() for location in locations_input.split(',') if location.strip()]
        
        if not locations:
            print("No valid locations provided. Exiting.")
            return
        
        # Confirm search parameters
        print("\n" + "=" * 40)
        print("SEARCH PARAMETERS:")
        print(f"Keywords: {', '.join(keywords)}")
        print(f"Locations: {', '.join(locations)}")
        print("=" * 40)
        
        confirm = get_user_input("\nProceed with search? (y/n): ").lower()
        if confirm not in ['y', 'yes']:
            print("Search cancelled.")
            return
        
        # Initialize data manager
        data_manager = DataManager()
        
        # Initialize job searcher
        job_searcher = LinkedInJobSearcher(email, password)
        
        # Perform job search
        print("\nStarting job search...")
        print("This may take several minutes. Please be patient.")
        
        all_jobs = []
        for keyword in keywords:
            for location in locations:
                print(f"\nSearching for '{keyword}' in '{location}'...")
                jobs = job_searcher.search_jobs(keyword, location)
                all_jobs.extend(jobs)
                print(f"Found {len(jobs)} jobs for this search.")
        
        if not all_jobs:
            print("\nNo jobs found matching your criteria.")
            return
        
        # Categorize and save jobs
        print(f"\nCategorizing {len(all_jobs)} jobs...")
        
        internships = []
        entry_level_jobs = []
        
        for job in all_jobs:
            if job_searcher.is_internship(job):
                internships.append(job)
            else:
                entry_level_jobs.append(job)
        
        # Save to separate files
        if internships:
            data_manager.save_internships(internships)
            print(f"Saved {len(internships)} internships to internships.csv")
        
        if entry_level_jobs:
            data_manager.save_entry_level_jobs(entry_level_jobs)
            print(f"Saved {len(entry_level_jobs)} entry-level jobs to entry_level_jobs.csv")
        
        print("\nJob search completed successfully!")
        print(f"Total jobs found: {len(all_jobs)}")
        print(f"Internships: {len(internships)}")
        print(f"Entry-level jobs: {len(entry_level_jobs)}")
        
    except KeyboardInterrupt:
        print("\n\nSearch interrupted by user.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        print(f"\nAn error occurred: {e}")
        print("Please check your internet connection and try again.")

if __name__ == "__main__":
    main() 