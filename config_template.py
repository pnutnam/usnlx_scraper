"""
Configuration settings for USNLX job scraper.
"""

# Browser settings
BROWSER_TYPE = "chrome"  # Options: "chrome" or "firefox"
HEADLESS_BROWSER = True  # Run browser in headless mode

# USNLX scraper settings
USNLX_BASE_URL = "https://usnlx.com/jobs/"
USNLX_TIMEOUT = 10  # Timeout in seconds for page elements
USNLX_MAX_MORE_CLICKS = 50  # Maximum number of times to click "More" button
IMPLICIT_WAIT = 5  # Implicit wait time in seconds
