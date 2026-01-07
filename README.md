# USNLX Job Scraper

A Python scraper for pulling job listings from **USNLX.com** (National Labor Exchange).

## Features

- 🔍 Search jobs by role and city
- 🌐 Automated web scraping with Selenium
- 📊 Standardized JSON output format
- 🔄 Loads all available job listings automatically
- 🚀 No API keys or authentication required

## Installation

1. **Clone the repository:**

   ```bash
   cd /home/nate/.gemini/antigravity/scratch/job_scraper
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

You can modify settings in `config.py` such as:

- Browser type (Chrome or Firefox)
- Headless mode (default: True)
- Maximum "More" button clicks (default: 50)
- Timeouts and wait times

## Usage

### Basic Example

```python
from scraper import scrape_jobs

# Search for jobs
jobs = scrape_jobs(
    role="Software Engineer",
    city="San Francisco"
)

print(f"Found {len(jobs)} jobs")
for job in jobs:
    print(f"{job['title']} at {job['company']}")
```

### Run the Example Script

```bash
python example.py
```

This will:

1. Search for "Software Engineer" in San Francisco from both sources
2. Display the first 5 results
3. Save all results to `jobs_output.json`
4. Run additional example searches

## Output Format

Each job listing contains:

```python
{
    "job_id": "54D24CBE5E6A47E88C39DEEB1F98727B",
    "title": "Software Engineer",
    "company": "Tech Company Inc.",
    "location": "San Francisco, CA",
    "url": "https://usnlx.com/...",
    "source": "usnlx"
}
```

## Scraper Details

### How It Works

- Opens a headless browser (Chrome or Firefox)
- Navigates to USNLX search results
- Automatically clicks the "More" button to load all available jobs (up to 50 times)
- Parses job listings from the HTML
- Returns structured JSON data

### Limitations

- **No authentication required** - completely free to use
- **Rate limits:** None specified, but includes respectful delays between actions
- **Results:** Loads all available results (typically 15-100+ jobs per search)

## Project Structure

```text
job_scraper/
├── __init__.py         # Package initialization
├── scraper.py          # Main scraper interface
├── usnlx_scraper.py    # USNLX web scraper
├── config.py           # Configuration
├── utils.py            # Utility functions
├── example.py          # Example usage script
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Dependencies

- **requests** - HTTP requests for API calls
- **selenium** - Web browser automation
- **beautifulsoup4** - HTML parsing
- **webdriver-manager** - Automatic WebDriver management
- **lxml** - Fast XML/HTML parser

## Troubleshooting

### ChromeDriver Issues

If you encounter ChromeDriver errors, the scraper will automatically download the correct driver. Ensure you have Chrome installed, or switch to Firefox in `config.py`:

```python
BROWSER_TYPE = "firefox"
```

### No Results Found

- Check that the role and city are spelled correctly
- Try broader search terms (e.g., "Engineer" instead of "Senior Software Engineer")
- Some locations may have limited job postings
- Try different city name formats (e.g., "San Francisco" vs "San Francisco, CA")

## Best Practices

1. **Be respectful** - Don't make excessive requests in short periods
2. **Use specific search terms** - More specific roles yield better results
3. **Save results to files** - Avoid re-scraping the same data
4. **Run in headless mode** - Faster and uses less resources (default)

## License

This project is for educational and personal use.
