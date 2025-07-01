#!/usr/bin/env python3
"""
Job Search Bot - Main Entry Point
A bot that searches company career websites for job openings matching user keywords.
"""

import os
import sys
import csv
import logging
from generic_career_parser import GenericCareerParser
from urllib.parse import urlparse
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def get_user_input(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        return ''

def guess_careers_url(company_name):
    """
    Try to guess the careers page URL for a company using common patterns.
    Returns a list of possible URLs (most likely first).
    """
    base = company_name.lower().replace(' ', '')
    patterns = [
        f"https://www.{base}.com/careers",
        f"https://careers.{base}.com/",
        f"https://www.{base}.com/jobs",
        f"https://jobs.{base}.com/",
        f"https://www.{base}.com/about/careers",
        f"https://www.{base}.com/about/jobs"
    ]
    return patterns

def find_working_careers_url(company_name):
    """
    Try each guessed URL and return the first one that loads successfully.
    """
    for url in guess_careers_url(company_name):
        try:
            resp = requests.get(url, timeout=8)
            if resp.status_code == 200 and 'html' in resp.headers.get('Content-Type', ''):
                return url
        except Exception:
            continue
    return None

def save_jobs_to_csv(jobs, filename='results.csv'):
    if not jobs:
        print("No jobs found to save.")
        return
    fieldnames = ['company', 'title', 'location', 'description', 'url']
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for job in jobs:
            writer.writerow(job)
    print(f"Saved {len(jobs)} jobs to {filename}")

def main():
    print("=" * 60)
    print("      COMPANY CAREERS JOB SEARCH BOT")
    print("=" * 60)
    print()
    
    companies_input = get_user_input("Enter company names (comma-separated): ")
    companies = [c.strip() for c in companies_input.split(',') if c.strip()]
    if not companies:
        print("No companies provided. Exiting.")
        return
    
    keywords_input = get_user_input("Enter job search keywords (comma-separated): ")
    keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
    if not keywords:
        print("No keywords provided. Exiting.")
        return
    
    print("\nSearching for jobs at:")
    for c in companies:
        print(f"- {c}")
    print(f"With keywords: {', '.join(keywords)}")
    print()
    
    all_jobs = []
    for company in companies:
        print(f"\nLooking for careers page for {company}...")
        
        careers_url = find_working_careers_url(company)
        if not careers_url:
            print(f"Could not find a working careers page for {company}.")
            continue
            
        print(f"Found careers page: {careers_url}")
        parser = GenericCareerParser(careers_url)
        jobs = parser.parse_jobs(keywords=keywords)
        for job in jobs:
            job['company'] = company
        print(f"Found {len(jobs)} matching jobs at {company}.")
        all_jobs.extend(jobs)
    
    save_jobs_to_csv(all_jobs)
    print("\nDone.")

if __name__ == "__main__":
    main() 