"""
Search query configuration for job scraper.

This file defines what types of jobs to search for and how to filter them.
"""

# Search queries - these will be used to search USNLX
SEARCH_QUERIES = {
    'graphic_web_design_phoenix': {
        'role': 'Designer',
        'city': 'Phoenix, AZ',
        'radius_miles': 100,  # Search within 100 miles
        'include_keywords': [
            'graphic', 'web', 'ui', 'ux', 'visual', 'digital',
            'brand', 'creative', 'product designer', 'interface'
        ],
        'exclude_keywords': [
            'cad', 'electrical', 'mechanical', 'civil', 'structural',
            'roadway', 'hvac', 'plumbing', 'cabinetry', 'interior',
            'landscape', 'architectural', 'engineering'
        ]
    }
}

# Fields to extract from job detail pages
DETAIL_FIELDS = [
    'title',
    'company',
    'location',
    'summary',
    'pay_range',
    'employment_type',  # Full-time, Part-time, Contract
    'remote_status',     # Remote, Hybrid, On-site
    'benefits',
    'description',
    'posted_date',
    'url'
]
