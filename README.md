# LinkedIn Job Search Bot

A Python-based LinkedIn job search bot that automatically searches and collects job postings based on user-specified criteria. The bot prompts for LinkedIn credentials, search keywords, and location preferences, then categorizes results into internships and entry-level positions.

## Features

- **Interactive User Interface**: Prompts for LinkedIn credentials, search keywords, and locations
- **LinkedIn Authentication**: Secure login using provided credentials
- **Smart Job Categorization**: Automatically separates jobs into:
  - Internships for recent Master's graduates
  - Entry-level positions
- **Comprehensive Data Collection**: Stores job data in CSV format with:
  - Job title
  - Company name
  - Location
  - Full job description
  - Extracted qualifications
  - Salary information (when available)
  - Job URL
  - Date posted
  - Search date
- **Duplicate Prevention**: Avoids collecting the same job multiple times
- **Rate Limiting**: Respects LinkedIn's rate limits with intelligent delays
- **Logging**: Comprehensive logging for debugging and monitoring

## Project Structure

```
jobSearchBot/
├── main.py              # Main entry point with user interface
├── job_searcher.py      # LinkedIn job search functionality
├── data_manager.py      # Data storage and CSV management
├── utils.py             # Utility functions and helpers
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── job_results/        # Output directory for CSV files
│   ├── internships.csv
│   └── entry_level_jobs.csv
└── logs/               # Log files directory
```

## Requirements

- Python 3.8+
- Chrome browser (for Selenium WebDriver)
- LinkedIn account
- Dependencies listed in requirements.txt

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd jobSearchBot
   ```

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

1. Run the main script:
   ```bash
   python main.py
   ```

2. Follow the prompts:
   - Enter your LinkedIn email and password
   - Provide job search keywords (comma-separated)
   - Specify location preferences (comma-separated)
   - Confirm search parameters

3. The bot will:
   - Login to LinkedIn
   - Search for jobs based on your criteria
   - Categorize jobs into internships and entry-level positions
   - Save results to separate CSV files

## Output Files

The bot creates two CSV files in the `job_results/` directory:

- **`internships.csv`**: Contains internship positions suitable for recent Master's graduates
- **`entry_level_jobs.csv`**: Contains entry-level positions

Each CSV file includes the following columns:
- `job_title`: The job title
- `company`: Company name
- `location`: Job location
- `job_description`: Full job description
- `qualifications`: Extracted qualifications and requirements
- `salary`: Salary information (when available)
- `job_url`: Direct link to the job posting
- `date_posted`: When the job was posted
- `search_date`: When the job was found by the bot

## Configuration

The bot is designed for users with:
- Master's of Science in Computer Science
- Focus on real-time software engineering positions
- Interest in both internships and entry-level positions

## Safety and Ethics

- **Rate Limiting**: The bot includes intelligent delays to respect LinkedIn's servers
- **User Consent**: Always requires explicit user confirmation before starting searches
- **Secure Input**: Passwords are masked during input
- **Logging**: All activities are logged for transparency

## Troubleshooting

### Common Issues

1. **Chrome Driver Issues**: The bot uses webdriver-manager to automatically handle Chrome driver installation
2. **Login Failures**: Ensure your LinkedIn credentials are correct and your account is not locked
3. **No Jobs Found**: Try different keywords or locations, or check if LinkedIn's structure has changed

### Logs

Check the `logs/` directory for detailed error messages and debugging information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational purposes. Please respect LinkedIn's terms of service and use responsibly.

## Disclaimer

This bot is designed for personal use and educational purposes. Users are responsible for complying with LinkedIn's terms of service and applicable laws. The developers are not responsible for any misuse of this tool. 