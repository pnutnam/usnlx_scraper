"""
Utility functions for job scraper.
"""
from typing import List, Dict
import re


def normalize_location(location: str) -> str:
    """
    Normalize location string for consistent matching.
    
    Args:
        location: Location string (e.g., "San Francisco, CA" or "San Francisco")
    
    Returns:
        Normalized location string in lowercase
    """
    # Remove extra whitespace
    location = re.sub(r'\s+', ' ', location.strip())
    # Convert to lowercase for comparison
    return location.lower()


def deduplicate_jobs(jobs: List[Dict]) -> List[Dict]:
    """
    Remove duplicate jobs based on title, company, and location.
    
    Args:
        jobs: List of job dictionaries
    
    Returns:
        Deduplicated list of jobs
    """
    seen = set()
    unique_jobs = []
    
    for job in jobs:
        # Create a unique key from title, company, and location
        key = (
            job.get('title', '').lower().strip(),
            job.get('company', '').lower().strip(),
            normalize_location(job.get('location', ''))
        )
        
        if key not in seen and all(key):  # Ensure all parts exist
            seen.add(key)
            unique_jobs.append(job)
    
    return unique_jobs


def format_location_for_api(city: str, state: str = None) -> str:
    """
    Format city and optional state for CareerOneStop API.
    
    Args:
        city: City name
        state: Optional state abbreviation or name
    
    Returns:
        Formatted location string (e.g., "San Francisco, CA" or "San Francisco")
    """
    if state:
        return f"{city}, {state}"
    return city
