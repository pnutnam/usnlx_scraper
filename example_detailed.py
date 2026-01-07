"""
Example usage of the enhanced job scraper with detail extraction.
"""
import json
from scraper_detailed import scrape_jobs_detailed


def main():
    """Run example detailed job search."""
    
    print("=" * 70)
    print("Enhanced Job Scraper - Graphic/Web Design in Phoenix, AZ")
    print("=" * 70)
    print()
    
    # Use predefined search configuration
    jobs = scrape_jobs_detailed('graphic_web_design_phoenix')
    
    # Display results
    print("\n" + "=" * 70)
    print(f"RESULTS: {len(jobs)} Graphic/Web Design Jobs")
    print("=" * 70)
    
    for i, job in enumerate(jobs, 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job['location']}")
        
        if job.get('matched_keywords'):
            print(f"   Matched: {', '.join(job['matched_keywords'])}")
        
        if job.get('pay_range'):
            print(f"   💰 Pay: {job['pay_range']}")
        
        if job.get('employment_type'):
            print(f"   📋 Type: {job['employment_type']}")
        
        if job.get('remote_status'):
            print(f"   🏠 Remote: {job['remote_status']}")
        
        if job.get('benefits'):
            print(f"   ✨ Benefits: {', '.join(job['benefits'])}")
        
        if job.get('summary'):
            summary = job['summary'][:150] + '...' if len(job['summary']) > 150 else job['summary']
            print(f"   📝 Summary: {summary}")
        
        print(f"   🔗 URL: {job['url']}")
    
    # Save to JSON
    output_file = 'graphic_web_design_phoenix_detailed.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved detailed results to {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
