# Company Careers Job Search Bot

A Python bot that searches the official careers pages of user-specified companies for job openings matching your keyword interests and qualifications.

## Features

- **User-driven:** Enter a list of company names and job search keywords at startup.
- **Automatic careers page discovery:** Attempts to find each company's official careers/jobs page.
- **Flexible scraping:** Modular design allows for custom parsers for specific companies and a generic fallback for standard layouts.
- **Keyword filtering:** Finds jobs whose title or description matches any of your keywords.
- **CSV output:** Saves all matching jobs to a CSV file with company name, job title, location, description, job URL, and more.
- **Ethical scraping:** Always checks robots.txt and respects site terms and request rates.
- **Extensible:** Easy to add support for new companies or custom page formats.

## How It Works

1. **Prompt for input:**
   - Enter company names (comma-separated)
   - Enter job search keywords (comma-separated)
2. **For each company:**
   - Find the official careers/jobs page
   - Scrape or parse job listings
   - Filter jobs by keywords
3. **Save results:**
   - All matching jobs are saved to `results.csv`

## Project Structure

```
company-careers-bot/
├── main.py                # Main entry point and user interface
├── company_finders/       # Parsers for specific companies (modular)
│   ├── __init__.py
│   ├── google.py          # Example: Google careers parser
│   └── ...
├── generic_career_parser.py # Fallback parser for standard layouts
├── data_manager.py        # Handles saving results to CSV
├── utils.py               # Shared helpers (keyword matching, robots.txt, etc.)
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── projectinstructions.txt# Project goals and rules
└── logs/                  # Log files
```

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the bot:
   ```bash
   python main.py
   ```
3. Enter company names and keywords when prompted.
4. View results in `results.csv`.

## Extending the Bot

- To add support for a new company with a unique careers page, add a new module in `company_finders/` and register it in the main script.
- The bot will use the generic parser for companies without a custom module.

## Ethics & Best Practices

- **Do not use this bot on sites that forbid scraping.**
- **Always check robots.txt before scraping a site.**
- **Be respectful with request rates (add delays).**
- **Use only for personal or research purposes unless you have permission.**

## License

This project is for educational and personal use. Please respect each company's terms of service and robots.txt. 