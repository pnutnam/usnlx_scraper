"""
USNLX web scraper for job search.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from bs4 import BeautifulSoup
from typing import List, Dict
import time
import config
from concurrent.futures import ThreadPoolExecutor, as_completed


class USNLXScraper:
    """Web scraper for USNLX job listings."""
    
    def __init__(self, headless: bool = None, browser_type: str = None):
        """
        Initialize the USNLX scraper.
        
        Args:
            headless: Run browser in headless mode (default from config)
            browser_type: Browser to use - "chrome" or "firefox" (default from config)
        """
        self.headless = headless if headless is not None else config.HEADLESS_BROWSER
        self.browser_type = browser_type or config.BROWSER_TYPE
        self.driver = None
        
    def _init_driver(self):
        """Initialize the Selenium WebDriver."""
        if self.driver:
            return
        
        if self.browser_type.lower() == "chrome":
            options = ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        else:
            options = FirefoxOptions()
            if self.headless:
                options.add_argument('--headless')
            
            service = FirefoxService(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=options)
        
        self.driver.implicitly_wait(config.IMPLICIT_WAIT)
    
    def _close_driver(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def _build_search_url(self, role: str, city: str, radius_miles: int = None) -> str:
        """
        Build the USNLX search URL.
        
        Args:
            role: Job role/title
            city: City name
            radius_miles: Search radius in miles (optional)
        
        Returns:
            Search URL
        """
        from urllib.parse import urlencode
        params = {
            'q': role,
            'location': city
        }
        # Add radius parameter if specified
        if radius_miles:
            params['r'] = radius_miles
        return f"{config.USNLX_BASE_URL}?{urlencode(params)}"
    
    def _click_more_button(self) -> bool:
        """
        Click the "More" button to load additional job listings.
        
        Returns:
            True if button was clicked, False if not found or not clickable
        """
        try:
            # Wait for the "More" button to be present and clickable
            # Using aria-label as the most reliable selector
            more_button = WebDriverWait(self.driver, config.USNLX_TIMEOUT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Load more jobs"]'))
            )
            
            # Scroll to button
            self.driver.execute_script("arguments[0].scrollIntoView(true);", more_button)
            time.sleep(0.5)
            
            # Click the button
            more_button.click()
            
            # Wait a moment for new jobs to load
            time.sleep(1.5)
            
            return True
        except (TimeoutException, NoSuchElementException):
            return False
    
    def _parse_job_listings(self, html: str) -> List[Dict]:
        """
        Parse job listings from HTML.
        
        Args:
            html: Page HTML content
        
        Returns:
            List of job dictionaries
        """
        soup = BeautifulSoup(html, 'lxml')
        jobs = []
        
        # Find all job listing links
        job_links = soup.find_all('a', class_='flex px-2 py-4')
        
        for link in job_links:
            try:
                # Extract job title
                title_elem = link.find('h2')
                title = title_elem.get_text(strip=True) if title_elem else ''
                
                # Extract company and location from the paragraph
                info_elem = link.find('p')
                company = ''
                location = ''
                
                if info_elem:
                    # Company is in a span
                    company_elem = info_elem.find('span')
                    if company_elem:
                        company = company_elem.get_text(strip=True)
                    
                    # Location is the text after the company span
                    full_text = info_elem.get_text(strip=True)
                    if company:
                        location = full_text.replace(company, '').strip()
                
                # Extract job URL
                job_url = link.get('href', '')
                if job_url and not job_url.startswith('http'):
                    job_url = f"https://usnlx.com{job_url}"
                
                # Extract job ID from URL
                job_id = ''
                if job_url:
                    parts = job_url.rstrip('/').split('/')
                    if len(parts) >= 2:
                        job_id = parts[-2]  # ID is typically second-to-last part
                
                job = {
                    'job_id': job_id,
                    'title': title,
                    'company': company,
                    'location': location,
                    'url': job_url,
                    'source': 'usnlx'
                }
                
                jobs.append(job)
                
            except Exception as e:
                print(f"Error parsing job listing: {e}")
                continue
        
        return jobs
    
    def _extract_job_details(self, job_url: str) -> Dict:
        """
        Extract detailed information from a job detail page.
        
        Args:
            job_url: URL of the job detail page
        
        Returns:
            Dictionary with detailed job information
        """
        details = {
            'summary': None,
            'pay_range': None,
            'employment_type': None,
            'remote_status': None,
            'benefits': None,
            'description': None,
            'posted_date': None
        }
        
        try:
            # Navigate to job detail page
            self.driver.get(job_url)
            
            # Wait for page to load
            time.sleep(2)
            
            # Get page HTML
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            
            # Extract job description (usually in a div with class 'job-description' or similar)
            desc_elem = soup.find('div', class_='job-description')
            if not desc_elem:
                # Try alternative selectors
                desc_elem = soup.find('div', {'id': 'job-description'})
            if not desc_elem:
                # Try to find any div containing substantial text
                all_divs = soup.find_all('div')
                for div in all_divs:
                    text = div.get_text(strip=True)
                    if len(text) > 200:  # Likely the description
                        desc_elem = div
                        break
            
            if desc_elem:
                details['description'] = desc_elem.get_text(separator='\n', strip=True)
                
                # Try to extract specific fields from description
                desc_text = details['description'].lower()
                
                # Extract employment type
                if 'full-time' in desc_text or 'full time' in desc_text:
                    details['employment_type'] = 'Full-time'
                elif 'part-time' in desc_text or 'part time' in desc_text:
                    details['employment_type'] = 'Part-time'
                elif 'contract' in desc_text:
                    details['employment_type'] = 'Contract'
                
                # Extract remote status
                if 'remote' in desc_text and 'not remote' not in desc_text:
                    if 'hybrid' in desc_text:
                        details['remote_status'] = 'Hybrid'
                    else:
                        details['remote_status'] = 'Remote'
                elif 'on-site' in desc_text or 'onsite' in desc_text or 'in-office' in desc_text:
                    details['remote_status'] = 'On-site'
                
                # Try to extract pay range (common patterns)
                import re
                pay_patterns = [
                    r'\$[\d,]+\s*-\s*\$[\d,]+\s*(?:per|/)\s*(?:year|hour|yr|hr)',
                    r'\$[\d,]+k?\s*-\s*\$[\d,]+k?',
                    r'salary:?\s*\$[\d,]+\s*-\s*\$[\d,]+',
                ]
                for pattern in pay_patterns:
                    match = re.search(pattern, desc_text, re.IGNORECASE)
                    if match:
                        details['pay_range'] = match.group(0)
                        break
                
                # Extract benefits (look for common benefit keywords)
                benefit_keywords = ['health insurance', '401k', 'pto', 'paid time off', 
                                   'dental', 'vision', 'retirement', 'bonus']
                found_benefits = []
                for keyword in benefit_keywords:
                    if keyword in desc_text:
                        found_benefits.append(keyword.title())
                if found_benefits:
                    details['benefits'] = list(set(found_benefits))  # Remove duplicates
            
            # Try to extract summary (often in a specific element)
            summary_elem = soup.find('p', class_='job-summary')
            if not summary_elem:
                summary_elem = soup.find('div', class_='summary')
            if summary_elem:
                details['summary'] = summary_elem.get_text(strip=True)
            elif details['description']:
                # Use first paragraph of description as summary
                paragraphs = details['description'].split('\n')
                for para in paragraphs:
                    if len(para) > 50:
                        details['summary'] = para[:300] + '...' if len(para) > 300 else para
                        break
            
            # Extract posted date from JSON-LD structured data
            try:
                import json as json_module
                import re
                json_ld_scripts = soup.find_all('script', type='application/ld+json')
                for script in json_ld_scripts:
                    try:
                        data = json_module.loads(script.string)
                        if isinstance(data, dict) and 'datePosted' in data:
                            details['posted_date'] = data['datePosted']
                            break
                    except:
                        continue
            except Exception as e:
                pass  # posted_date will remain None
            
        except Exception as e:
            print(f"Error extracting job details from {job_url}: {e}")
        
        return details
    
    def _extract_job_details_with_index(self, index: int, job: Dict, total: int) -> Dict:
        """
        Extract job details with progress reporting (for parallel execution).
        
        Args:
            index: Job index (1-based)
            job: Job dictionary containing URL
            total: Total number of jobs
        
        Returns:
            Dictionary with detailed job information
        """
        print(f"  [{index}/{total}] {job['title'][:50]}...")
        return self._extract_job_details(job['url'])
    
    def _set_distance_filter(self, radius_miles: int) -> bool:
        """
        Set the distance filter dropdown on USNLX.
        
        Args:
            radius_miles: Distance in miles (e.g., 25, 50, 100)
        
        Returns:
            True if filter was set successfully, False otherwise
        """
        try:
            # Wait for page to load
            time.sleep(2)
            
            # Look for distance/radius dropdown or filter
            # Common selectors for distance filters
            selectors = [
                "//select[contains(@name, 'radius')]",
                "//select[contains(@name, 'distance')]",
                "//select[contains(@id, 'radius')]",
                "//select[contains(@id, 'distance')]",
                "//select[contains(@class, 'radius')]",
                "//select[contains(@class, 'distance')]"
            ]
            
            distance_select = None
            for selector in selectors:
                try:
                    distance_select = self.driver.find_element(By.XPATH, selector)
                    if distance_select:
                        break
                except NoSuchElementException:
                    continue
            
            if not distance_select:
                print(f"Warning: Could not find distance filter dropdown")
                return False
            
            # Try to select the radius value
            from selenium.webdriver.support.ui import Select
            select = Select(distance_select)
            
            # Try to find option with the radius value
            radius_str = str(radius_miles)
            for option in select.options:
                option_text = option.text.lower()
                option_value = option.get_attribute('value')
                
                # Check if this option matches our radius
                if radius_str in option_text or radius_str in str(option_value):
                    select.select_by_visible_text(option.text)
                    print(f"✓ Set distance filter to: {option.text}")
                    time.sleep(1)  # Wait for filter to apply
                    return True
            
            # If exact match not found, try to find closest match
            print(f"Warning: Could not find exact {radius_miles} mile option, using default")
            return False
            
        except Exception as e:
            print(f"Error setting distance filter: {e}")
            return False
    
    def search_jobs(
        self, 
        role: str, 
        city: str,
        radius_miles: int = None,
        extract_details: bool = False,
        include_keywords: List[str] = None,
        exclude_keywords: List[str] = None
    ) -> List[Dict]:
        """
        Search for jobs on USNLX.
        
        Args:
            role: Job role/title
            city: City name
            radius_miles: Search radius in miles (e.g., 25, 50, 100)
            extract_details: If True, click into each job to extract detailed info
            include_keywords: Only include jobs with titles containing these keywords
            exclude_keywords: Exclude jobs with titles containing these keywords
        
        Returns:
            List of job dictionaries with standardized fields
        """
        try:
            # Initialize driver
            self._init_driver()
            
            # Build and navigate to search URL (includes radius if specified)
            url = self._build_search_url(role, city, radius_miles)
            self.driver.get(url)
            
            # Wait for initial job listings to load
            try:
                WebDriverWait(self.driver, config.USNLX_TIMEOUT).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'li'))
                )
            except TimeoutException:
                print("Timeout waiting for job listings to load")
                return []
            
            # Click "More" button repeatedly to load ALL jobs
            clicks = 0
            print("Loading all job listings...")
            while clicks < config.USNLX_MAX_MORE_CLICKS:
                if not self._click_more_button():
                    # No more button found or not clickable - we've loaded all jobs
                    break
                clicks += 1
                if clicks % 5 == 0:
                    print(f"  Loaded {clicks * 15}+ jobs...")
            
            # Get the final page HTML
            html = self.driver.page_source
            
            # Parse job listings
            jobs = self._parse_job_listings(html)
            
            print(f"Retrieved {len(jobs)} total jobs from USNLX")
            
            # Filter by keywords if specified
            if include_keywords or exclude_keywords:
                jobs = self._filter_by_keywords(jobs, include_keywords, exclude_keywords)
                print(f"Filtered to {len(jobs)} matching jobs")
            
            # Extract details if requested
            if extract_details:
                print(f"Extracting details for {len(jobs)} jobs in parallel (10 at a time)...")
                detailed_jobs = []
                
                # Use ThreadPoolExecutor for parallel scraping
                with ThreadPoolExecutor(max_workers=10) as executor:
                    # Submit all jobs for detail extraction
                    future_to_job = {
                        executor.submit(self._extract_job_details_with_index, i, job, len(jobs)): job 
                        for i, job in enumerate(jobs, 1)
                    }
                    
                    # Collect results as they complete
                    for future in as_completed(future_to_job):
                        job = future_to_job[future]
                        try:
                            details = future.result()
                            # Merge details into job
                            job.update(details)
                            detailed_jobs.append(job)
                        except Exception as e:
                            print(f"  Error extracting details for {job['title']}: {e}")
                            detailed_jobs.append(job)  # Add job without details
                
                jobs = detailed_jobs
                print(f"✓ Completed detail extraction for {len(jobs)} jobs")
            
            return jobs
            
        except Exception as e:
            print(f"Error scraping USNLX: {e}")
            return []
        
        finally:
            # Clean up
            self._close_driver()
    
    def _filter_by_keywords(
        self, 
        jobs: List[Dict], 
        include_keywords: List[str] = None,
        exclude_keywords: List[str] = None
    ) -> List[Dict]:
        """
        Filter jobs by title keywords.
        
        Args:
            jobs: List of job dictionaries
            include_keywords: Only include jobs with titles containing these keywords
            exclude_keywords: Exclude jobs with titles containing these keywords
        
        Returns:
            Filtered list of jobs
        """
        filtered_jobs = []
        
        for job in jobs:
            title_lower = job['title'].lower()
            
            # Check exclude keywords first
            if exclude_keywords:
                if any(keyword.lower() in title_lower for keyword in exclude_keywords):
                    continue
            
            # Check include keywords
            if include_keywords:
                if any(keyword.lower() in title_lower for keyword in include_keywords):
                    job['matched_keywords'] = [
                        kw for kw in include_keywords 
                        if kw.lower() in title_lower
                    ]
                    filtered_jobs.append(job)
            else:
                filtered_jobs.append(job)
        
        return filtered_jobs
    
    def __enter__(self):
        """Context manager entry."""
        self._init_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self._close_driver()
