"""
Job Scraper - Pull job listings from CareerOneStop and USNLX.

This package provides a unified interface to search for jobs across
multiple sources using a simple function call.
"""

from scraper import scrape_jobs

__version__ = "1.0.0"
__all__ = ['scrape_jobs']
