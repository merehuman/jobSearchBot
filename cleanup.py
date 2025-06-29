#!/usr/bin/env python3
"""
Cleanup script for Job Search Bot
Helps manage old files and organize the project
"""

import os
import shutil
from datetime import datetime, timedelta

def cleanup_old_results():
    """Clean up old job search results"""
    print("Cleaning up old job search results...")
    
    # Old results directory
    old_dir = "job_search_results"
    new_dir = "job_results"
    
    if os.path.exists(old_dir):
        # Move old files to new directory
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        
        # Move CSV files
        for file in os.listdir(old_dir):
            if file.endswith('.csv'):
                old_path = os.path.join(old_dir, file)
                new_path = os.path.join(new_dir, f"old_{file}")
                shutil.move(old_path, new_path)
                print(f"Moved: {file}")
        
        # Remove old directory if empty
        if not os.listdir(old_dir):
            os.rmdir(old_dir)
            print("Removed empty old results directory")
    
    print("Cleanup completed!")

def create_sample_files():
    """Create sample CSV files with proper structure"""
    print("Creating sample CSV files...")
    
    import pandas as pd
    
    # Sample data
    sample_internships = [
        {
            'job_title': 'Software Engineering Intern',
            'company': 'Tech Corp',
            'location': 'San Francisco, CA',
            'job_description': 'Join our team as a software engineering intern...',
            'qualifications': 'Currently pursuing MS in Computer Science...',
            'salary': 'Salary not specified',
            'job_url': 'https://linkedin.com/jobs/view/123',
            'date_posted': '2024-01-15',
            'search_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    ]
    
    sample_entry_level = [
        {
            'job_title': 'Junior Software Engineer',
            'company': 'Startup Inc',
            'location': 'Remote',
            'job_description': 'We are looking for a junior software engineer...',
            'qualifications': 'BS/MS in Computer Science, 0-2 years experience...',
            'salary': '$60,000 - $80,000 per year',
            'job_url': 'https://linkedin.com/jobs/view/456',
            'date_posted': '2024-01-14',
            'search_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    ]
    
    # Create directories
    os.makedirs("job_results", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Create sample files
    pd.DataFrame(sample_internships).to_csv("job_results/internships.csv", index=False)
    pd.DataFrame(sample_entry_level).to_csv("job_results/entry_level_jobs.csv", index=False)
    
    print("Sample files created!")

def main():
    """Main cleanup function"""
    print("=" * 50)
    print("JOB SEARCH BOT - CLEANUP UTILITY")
    print("=" * 50)
    
    print("\n1. Clean up old results")
    print("2. Create sample files")
    print("3. Both")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        cleanup_old_results()
    elif choice == "2":
        create_sample_files()
    elif choice == "3":
        cleanup_old_results()
        create_sample_files()
    elif choice == "4":
        print("Exiting...")
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main() 