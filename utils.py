#!/usr/bin/env python3
"""
Utility functions for the Job Search Bot
"""

import getpass
import re
import logging
import os
from datetime import datetime

def get_user_input(prompt: str, is_password: bool = False) -> str:
    """
    Get user input with optional password masking
    
    Args:
        prompt: The prompt to display to the user
        is_password: Whether to mask the input (for passwords)
    
    Returns:
        User input as string
    """
    if is_password:
        return getpass.getpass(prompt)
    else:
        return input(prompt).strip()

def validate_credentials(email: str, password: str) -> bool:
    """
    Validate email and password format
    
    Args:
        email: User's email address
        password: User's password
    
    Returns:
        True if credentials are valid, False otherwise
    """
    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False
    
    # Password should not be empty and should be at least 6 characters
    if not password or len(password) < 6:
        return False
    
    return True

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/job_search_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler()
        ]
    )

def clean_text(text: str) -> str:
    """
    Clean and normalize text data
    
    Args:
        text: Raw text to clean
    
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might cause CSV issues
    text = text.replace('"', '""')  # Escape quotes for CSV
    
    return text

def extract_salary_range(text: str) -> str:
    """
    Extract salary information from job description
    
    Args:
        text: Job description text
    
    Returns:
        Extracted salary information or "Salary not specified"
    """
    if not text:
        return "Salary not specified"
    
    # Common salary patterns
    salary_patterns = [
        r'\$[\d,]+(?:-\$[\d,]+)?\s*(?:per\s+)?(?:year|month|hour|week)',
        r'\$[\d,]+(?:k|K)\s*(?:per\s+)?(?:year|month)',
        r'[\d,]+(?:k|K)\s*-\s*[\d,]+(?:k|K)\s*(?:per\s+)?(?:year|month)',
        r'salary[:\s]*\$?[\d,]+(?:-\$?[\d,]+)?',
        r'compensation[:\s]*\$?[\d,]+(?:-\$?[\d,]+)?'
    ]
    
    for pattern in salary_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return clean_text(matches[0])
    
    return "Salary not specified"

def extract_qualifications(text: str) -> str:
    """
    Extract qualifications from job description
    
    Args:
        text: Job description text
    
    Returns:
        Extracted qualifications or "Qualifications not specified"
    """
    if not text:
        return "Qualifications not specified"
    
    # Look for qualification sections
    qualification_keywords = [
        'requirements', 'qualifications', 'skills', 'experience', 
        'education', 'degree', 'certification'
    ]
    
    lines = text.split('\n')
    qualifications = []
    
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        
        # Check if this line contains qualification keywords
        if any(keyword in line_lower for keyword in qualification_keywords):
            # Collect the next few lines as qualifications
            for j in range(i, min(i + 10, len(lines))):
                qual_line = lines[j].strip()
                if qual_line and len(qual_line) > 10:  # Meaningful line
                    qualifications.append(qual_line)
    
    if qualifications:
        return clean_text('\n'.join(qualifications[:5]))  # Limit to first 5 lines
    
    return "Qualifications not specified"

def is_internship_job(title: str, description: str) -> bool:
    """
    Determine if a job is an internship based on title and description
    
    Args:
        title: Job title
        description: Job description
    
    Returns:
        True if it's an internship, False otherwise
    """
    internship_keywords = [
        'intern', 'internship', 'co-op', 'coop', 'student', 'graduate',
        'entry level', 'entry-level', 'junior', 'trainee'
    ]
    
    text_to_check = f"{title} {description}".lower()
    
    return any(keyword in text_to_check for keyword in internship_keywords)

def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human readable format
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minutes"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours} hours {minutes} minutes" 