"""
CareerOneStop API client for job search.
"""
import requests
from typing import List, Dict, Optional
from urllib.parse import quote
import config


class CareerOneStopClient:
    """Client for interacting with CareerOneStop Jobs API V2."""
    
    def __init__(self, user_id: str = None, token: str = None):
        """
        Initialize the CareerOneStop API client.
        
        Args:
            user_id: CareerOneStop user ID (defaults to config value)
            token: CareerOneStop API token (defaults to config value)
        """
        self.user_id = user_id or config.CAREERONESTOP_USER_ID
        self.token = token or config.CAREERONESTOP_TOKEN
        self.base_url = config.CAREERONESTOP_BASE_URL
        
    def _build_headers(self) -> Dict[str, str]:
        """Build authentication headers for API requests."""
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def _build_url(
        self,
        keyword: str,
        location: str,
        radius: int,
        sort_column: str,
        sort_order: str,
        start_row: int,
        page_size: int,
        days: int
    ) -> str:
        """
        Build the API URL with parameters.
        
        Args:
            keyword: Job title or role
            location: City, State, or Zip Code
            radius: Search radius in miles
            sort_column: Field to sort by
            sort_order: Sort order (ASC, DESC, or 0 for relevance)
            start_row: Starting record index
            page_size: Number of results per page
            days: Jobs posted within last X days
        
        Returns:
            Complete API URL
        """
        # URL encode the keyword and location
        keyword_encoded = quote(keyword)
        location_encoded = quote(location)
        
        url = (
            f"{self.base_url}/{self.user_id}/{keyword_encoded}/"
            f"{location_encoded}/{radius}/{sort_column}/{sort_order}/"
            f"{start_row}/{page_size}/{days}"
        )
        
        # Add query parameters for enhanced data
        url += "?enableJobDescriptionSnippet=1&enableMetaData=0"
        
        return url
    
    def search_jobs(
        self,
        keyword: str,
        location: str,
        radius: int = None,
        max_results: int = None,
        days: int = None
    ) -> List[Dict]:
        """
        Search for jobs using the CareerOneStop API.
        
        Args:
            keyword: Job title or role (use "0" for all jobs in location)
            location: City, State, or Zip Code (e.g., "San Francisco, CA")
            radius: Search radius in miles (default from config)
            max_results: Maximum number of results to return (default 750)
            days: Jobs posted within last X days (default from config)
        
        Returns:
            List of job dictionaries with standardized fields
        """
        radius = radius or config.DEFAULT_RADIUS
        max_results = max_results or (config.MAX_START_ROW + config.MAX_PAGE_SIZE)
        days = days or config.DEFAULT_DAYS
        
        all_jobs = []
        start_row = 0
        page_size = config.MAX_PAGE_SIZE
        
        while start_row <= config.MAX_START_ROW and len(all_jobs) < max_results:
            # Build URL for this page
            url = self._build_url(
                keyword=keyword,
                location=location,
                radius=radius,
                sort_column=config.DEFAULT_SORT_COLUMN,
                sort_order=config.DEFAULT_SORT_ORDER,
                start_row=start_row,
                page_size=page_size,
                days=days
            )
            
            try:
                # Make API request
                response = requests.get(
                    url,
                    headers=self._build_headers(),
                    timeout=config.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Extract jobs from response
                jobs = data.get('Jobs', [])
                
                if not jobs:
                    # No more jobs available
                    break
                
                # Convert to standardized format
                for job in jobs:
                    standardized_job = {
                        'job_id': job.get('JvId', ''),
                        'title': job.get('JobTitle', ''),
                        'company': job.get('Company', ''),
                        'location': job.get('Location', ''),
                        'description_snippet': job.get('DescriptionSnippet', ''),
                        'url': job.get('URL', ''),
                        'posted_date': job.get('AcquisitionDate', ''),
                        'source': 'careeronestop'
                    }
                    all_jobs.append(standardized_job)
                
                # Check if we've retrieved all available jobs
                total_count = data.get('JobCount', 0)
                if len(all_jobs) >= total_count or len(all_jobs) >= max_results:
                    break
                
                # Move to next page
                start_row += page_size
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching jobs from CareerOneStop: {e}")
                break
        
        return all_jobs[:max_results]
