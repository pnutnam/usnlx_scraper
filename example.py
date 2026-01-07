"""
Example usage of the USNLX job scraper.
"""
import json
from scraper import scrape_jobs


def main():
    """Run example job searches."""
    
    print("=" * 60)
    print("USNLX Job Scraper Example")
    print("=" * 60)
    
    # Example 1: Search for Software Engineer in San Francisco
    print("\n1. Searching for 'Software Engineer' in 'San Francisco'...")
    jobs = scrape_jobs(
        role="Software Engineer",
        city="San Francisco"
    )
    
    print(f"\nFound {len(jobs)} total jobs")
    
    # Display first 5 jobs
    if jobs:
        print("\nFirst 5 jobs:")
        for i, job in enumerate(jobs[:5], 1):
            print(f"\n{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   URL: {job['url']}")
        
        # Save all jobs to JSON file
        output_file = "jobs_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved all {len(jobs)} jobs to {output_file}")
    
    # Example 2: Search for Nurse in Chicago
    print("\n" + "=" * 60)
    print("\n2. Searching for 'Nurse' in 'Chicago'...")
    jobs_nurses = scrape_jobs(
        role="Nurse",
        city="Chicago"
    )
    
    print(f"\nFound {len(jobs_nurses)} jobs")
    
    # Example 3: Search for Data Scientist in New York
    print("\n" + "=" * 60)
    print("\n3. Searching for 'Data Scientist' in 'New York'...")
    jobs_ds = scrape_jobs(
        role="Data Scientist",
        city="New York"
    )
    
    print(f"\nFound {len(jobs_ds)} jobs")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
