"""
Job scraper for USNLX.
"""
from typing import List, Dict
from usnlx_scraper import USNLXScraper


def scrape_jobs(role: str, city: str) -> List[Dict]:
    """
    Search for jobs on USNLX.
    
    Args:
        role: Job role/title to search for
        city: City name or "City, State" format
    
    Returns:
        List of job dictionaries with standardized fields:
        - job_id: Unique identifier
        - title: Job title
        - company: Company name
        - location: Job location
        - url: Link to job posting
        - source: Source of the job ('usnlx')
    
    Example:
        >>> jobs = scrape_jobs("Software Engineer", "San Francisco")
        >>> print(f"Found {len(jobs)} jobs")
        >>> for job in jobs[:5]:
        ...     print(f"{job['title']} at {job['company']}")
    """
    try:
        scraper = USNLXScraper()
        jobs = scraper.search_jobs(role=role, city=city)
        print(f"Retrieved {len(jobs)} jobs from USNLX")
        return jobs
    except Exception as e:
        print(f"Error scraping USNLX: {e}")
        return []
