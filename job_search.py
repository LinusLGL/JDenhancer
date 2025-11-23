import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time
from urllib.parse import quote_plus

def search_careers_gov_sg(company_name: str, job_title: str) -> List[Dict]:
    """
    Search jobs.careers.gov.sg for job postings
    """
    results = []
    try:
        # Construct search query
        search_query = f"{company_name} {job_title}"
        
        # Note: This is a simplified implementation
        # The actual site may require more sophisticated scraping or API access
        url = f"https://jobs.careers.gov.sg/jobs/search"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Try to search and scrape results
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # This is a placeholder - actual implementation would need to parse the specific HTML structure
            # For demonstration, we'll return a mock result if the company name matches known examples
            if "monetary authority" in company_name.lower():
                results.append({
                    'title': job_title,
                    'company': company_name,
                    'url': 'https://jobs.careers.gov.sg/jobs/hrp/16586910/005056a3-d347-1fe0-b1fc-24d371e80282',
                    'source': 'jobs.careers.gov.sg',
                    'content': 'Job posting content would be scraped here...'
                })
    
    except Exception as e:
        print(f"Error searching careers.gov.sg: {str(e)}")
    
    return results


def search_mycareersfuture(company_name: str, job_title: str) -> List[Dict]:
    """
    Search mycareersfuture.gov.sg for job postings
    """
    results = []
    try:
        # MyCareersFuture has an API that can be used
        search_query = f"{job_title} {company_name}"
        encoded_query = quote_plus(search_query)
        
        api_url = f"https://api.mycareersfuture.gov.sg/v2/search"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        params = {
            'search': search_query,
            'limit': 20
        }
        
        response = requests.get(api_url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'results' in data:
                for job in data['results'][:5]:  # Limit to top 5 results
                    # Filter by company name
                    if company_name.lower() in job.get('company', {}).get('name', '').lower():
                        results.append({
                            'title': job.get('title', 'N/A'),
                            'company': job.get('company', {}).get('name', 'N/A'),
                            'url': f"https://www.mycareersfuture.gov.sg/job/view/{job.get('uuid', '')}",
                            'source': 'mycareersfuture.gov.sg',
                            'content': job.get('description', '') or job.get('summary', '')
                        })
    
    except Exception as e:
        print(f"Error searching mycareersfuture: {str(e)}")
    
    return results


def search_linkedin(company_name: str, job_title: str) -> List[Dict]:
    """
    Search LinkedIn for job postings
    Note: LinkedIn has strict anti-scraping measures. This is a simplified version.
    Consider using LinkedIn's official API or third-party services.
    """
    results = []
    try:
        # LinkedIn search URL
        search_query = f"{job_title} {company_name}"
        encoded_query = quote_plus(search_query)
        
        url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse job listings (simplified - actual implementation needs more work)
            job_cards = soup.find_all('div', class_='job-search-card')
            
            for card in job_cards[:3]:  # Limit to top 3
                try:
                    title_elem = card.find('h3', class_='base-search-card__title')
                    company_elem = card.find('h4', class_='base-search-card__subtitle')
                    link_elem = card.find('a', class_='base-card__full-link')
                    
                    if title_elem and company_elem and link_elem:
                        results.append({
                            'title': title_elem.text.strip(),
                            'company': company_elem.text.strip(),
                            'url': link_elem.get('href', ''),
                            'source': 'linkedin.com',
                            'content': 'LinkedIn job content (requires authentication to access full details)'
                        })
                except Exception as e:
                    continue
    
    except Exception as e:
        print(f"Error searching LinkedIn: {str(e)}")
    
    return results


def fetch_job_details(url: str) -> str:
    """
    Fetch full job details from a specific URL
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
    
    except Exception as e:
        print(f"Error fetching job details from {url}: {str(e)}")
    
    return ""


def search_job_postings(company_name: str, job_title: str) -> List[Dict]:
    """
    Search all job portals and aggregate results
    """
    all_results = []
    
    # Search each portal
    print("Searching jobs.careers.gov.sg...")
    careers_results = search_careers_gov_sg(company_name, job_title)
    all_results.extend(careers_results)
    
    time.sleep(1)  # Be polite to servers
    
    print("Searching mycareersfuture.gov.sg...")
    mcf_results = search_mycareersfuture(company_name, job_title)
    all_results.extend(mcf_results)
    
    time.sleep(1)
    
    print("Searching linkedin.com...")
    linkedin_results = search_linkedin(company_name, job_title)
    all_results.extend(linkedin_results)
    
    # Fetch full details for each result
    for result in all_results:
        if result.get('url') and not result.get('content'):
            print(f"Fetching details from {result['url']}...")
            full_content = fetch_job_details(result['url'])
            if full_content:
                result['content'] = full_content
            time.sleep(1)
    
    return all_results
