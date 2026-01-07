"""
Enhanced job scraper with detail extraction and filtering.
"""
from typing import List, Dict
from datetime import datetime
from usnlx_scraper import USNLXScraper
from search_config import SEARCH_QUERIES


def scrape_jobs_detailed(
    search_name: str = None,
    role: str = None,
    city: str = None,
    radius_miles: int = None,
    include_keywords: List[str] = None,
    exclude_keywords: List[str] = None
) -> List[Dict]:
    """
    Search for jobs with detailed information extraction.
    
    Can be used in two ways:
    1. With a search_name from search_config.py
    2. With direct parameters (role, city, radius, keywords)
    
    Args:
        search_name: Name of predefined search in search_config.py
        role: Job role/title (if not using search_name)
        city: City name (if not using search_name)
        radius_miles: Search radius in miles (e.g., 25, 50, 100)
        include_keywords: Keywords to filter for (if not using search_name)
        exclude_keywords: Keywords to filter out (if not using search_name)
    
    Returns:
        List of detailed job dictionaries
    
    Examples:
        # Using predefined search
        >>> jobs = scrape_jobs_detailed('graphic_web_design_phoenix')
        
        # Using direct parameters
        >>> jobs = scrape_jobs_detailed(
        ...     role='Designer',
        ...     city='Phoenix, AZ',
        ...     radius_miles=100,
        ...     include_keywords=['graphic', 'web'],
        ...     exclude_keywords=['cad', 'electrical']
        ... )
    """
    # Get search parameters
    if search_name:
        if search_name not in SEARCH_QUERIES:
            raise ValueError(f"Search '{search_name}' not found in search_config.py")
        
        config = SEARCH_QUERIES[search_name]
        role = config['role']
        city = config['city']
        radius_miles = config.get('radius_miles', radius_miles)
        include_keywords = config.get('include_keywords')
        exclude_keywords = config.get('exclude_keywords')
    elif not role or not city:
        raise ValueError("Must provide either search_name or both role and city")
    
    print(f"Searching for: {role} in {city}")
    if radius_miles:
        print(f"Radius: within {radius_miles} miles")
    if include_keywords:
        print(f"Including keywords: {', '.join(include_keywords)}")
    if exclude_keywords:
        print(f"Excluding keywords: {', '.join(exclude_keywords)}")
    print()
    
    # Run scraper with detail extraction
    scraper = USNLXScraper()
    jobs = scraper.search_jobs(
        role=role,
        city=city,
        radius_miles=radius_miles,
        extract_details=True,
        include_keywords=include_keywords,
        exclude_keywords=exclude_keywords
    )
    
    # Add timestamp to each job
    timestamp = datetime.now().isoformat()
    for job in jobs:
        job['scraped_at'] = timestamp
    
    print(f"\n✓ Found {len(jobs)} matching jobs with detailed information")
    
    return jobs
