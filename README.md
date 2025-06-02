# Job Search Bot

A Python-based job search bot that automatically searches and collects software engineering job postings based on specified criteria.

## Features
- Searches for real-time software engineering positions
- Separates results into two categories:
  - Internships for recent Master's graduates
  - Entry-level positions
- Stores job data in CSV format with the following information:
  - Job title
  - Location
  - Description
  - Qualifications
  - Salary

## Requirements
- Python 3.8+
- Dependencies listed in requirements.txt

## Setup
1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the main script:
```bash
python job_search_bot.py
```

The script will create two CSV files:
- `internships.csv`: Contains internship positions
- `entry_level_jobs.csv`: Contains entry-level positions

## Configuration
The bot is configured to search based on the following qualifications:
- Master's of Science in Computer Science
- Focus on real-time software engineering positions 