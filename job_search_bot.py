import os
import pandas as pd
from datetime import datetime
from typing import List, Dict
import multion
import agentql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class JobSearchBot:
    def __init__(self):
        self.qualifications = "Master's of Science in Computer Science"
        self.job_type = "real-time software engineering"
        self.internships_file = "internships.csv"
        self.entry_level_file = "entry_level_jobs.csv"
        self.columns = ['title', 'location', 'description', 'qualifications', 'salary']
        
        # Initialize multion for complex job search tasks
        multion.login()
        
        # Initialize empty DataFrames for storing results
        self.internships_df = pd.DataFrame(columns=self.columns)
        self.entry_level_df = pd.DataFrame(columns=self.columns)

    def search_jobs(self):
        """
        Main method to search for jobs using various job platforms
        """
        # List of job boards to search
        job_boards = [
            "linkedin.com/jobs",
            "indeed.com",
            "glassdoor.com"
        ]

        for board in job_boards:
            # Use multion to perform intelligent job searching
            search_results = multion.browse({
                "url": f"https://www.{board}",
                "goals": [
                    f"Search for {self.job_type} positions",
                    "Filter for entry-level and internship positions",
                    f"Look for positions matching qualifications: {self.qualifications}",
                    "Collect job details including title, location, description, qualifications, and salary"
                ]
            })
            
            self._process_results(search_results)

    def _process_results(self, results: List[Dict]):
        """
        Process and categorize job search results
        """
        for job in results:
            job_data = {
                'title': job.get('title', ''),
                'location': job.get('location', ''),
                'description': job.get('description', ''),
                'qualifications': job.get('qualifications', ''),
                'salary': job.get('salary', '')
            }
            
            # Categorize as internship or entry-level based on title and description
            if any(keyword in job_data['title'].lower() for keyword in ['intern', 'internship']):
                self.internships_df = pd.concat([self.internships_df, pd.DataFrame([job_data])], ignore_index=True)
            else:
                self.entry_level_df = pd.concat([self.entry_level_df, pd.DataFrame([job_data])], ignore_index=True)

    def save_results(self):
        """
        Save results to CSV files
        """
        # Add timestamp to avoid overwriting previous results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save internships
        internships_filename = f"{timestamp}_{self.internships_file}"
        self.internships_df.to_csv(internships_filename, index=False)
        print(f"Saved internships to {internships_filename}")
        
        # Save entry-level positions
        entry_level_filename = f"{timestamp}_{self.entry_level_file}"
        self.entry_level_df.to_csv(entry_level_filename, index=False)
        print(f"Saved entry-level positions to {entry_level_filename}")

def main():
    try:
        # Create and run the job search bot
        bot = JobSearchBot()
        print("Starting job search...")
        bot.search_jobs()
        bot.save_results()
        print("Job search completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 