import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time
from urllib.parse import quote_plus, urljoin
import json
import re
import warnings

# Suppress SSL warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def search_careers_gov_sg(company_name: str, job_title: str) -> List[Dict]:
    """
    Search jobs.careers.gov.sg for job postings using multiple methods
    """
    results = []
    
    # Method 1: Try Bing search
    try:
        search_query = f"site:careers.gov.sg {job_title} {company_name}"
        encoded_query = quote_plus(search_query)
        
        url = f"https://www.bing.com/search?q={encoded_query}&count=20"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find Bing search results
            search_results = soup.find_all('li', class_='b_algo')
            
            for result in search_results[:10]:
                try:
                    link_elem = result.find('a')
                    if not link_elem:
                        continue
                    
                    job_url = link_elem.get('href', '')
                    
                    # Check if it's a careers.gov.sg job URL
                    if 'careers.gov.sg' in job_url and '/jobs/' in job_url:
                        title_elem = result.find('h2')
                        title = title_elem.text.strip() if title_elem else job_title
                        
                        snippet_elem = result.find('p')
                        snippet = snippet_elem.text.strip() if snippet_elem else ''
                        
                        results.append({
                            'title': title,
                            'company': company_name,
                            'url': job_url,
                            'source': 'jobs.careers.gov.sg',
                            'content': snippet
                        })
                        print(f"Found careers.gov.sg job: {title}")
                except Exception as e:
                    continue
    
    except Exception as e:
        print(f"Error searching careers.gov.sg via Bing: {str(e)}")
    
    # Method 2: Try DuckDuckGo if Bing didn't work
    if not results:
        try:
            search_query = f"site:careers.gov.sg {job_title} {company_name}"
            encoded_query = quote_plus(search_query)
            
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            }
            
            response = requests.post(url, headers=headers, timeout=15, verify=False)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find DuckDuckGo results
                search_results = soup.find_all('div', class_='result')
                
                for result in search_results[:10]:
                    try:
                        link_elem = result.find('a', class_='result__a')
                        if not link_elem:
                            continue
                        
                        job_url = link_elem.get('href', '')
                        
                        # Check if it's a careers.gov.sg job URL
                        if 'careers.gov.sg' in job_url and '/jobs/' in job_url:
                            title = link_elem.text.strip() if link_elem else job_title
                            
                            snippet_elem = result.find('a', class_='result__snippet')
                            snippet = snippet_elem.text.strip() if snippet_elem else ''
                            
                            results.append({
                                'title': title,
                                'company': company_name,
                                'url': job_url,
                                'source': 'jobs.careers.gov.sg',
                                'content': snippet
                            })
                            print(f"Found careers.gov.sg job via DDG: {title}")
                    except Exception as e:
                        continue
        
        except Exception as e:
            print(f"Error searching careers.gov.sg via DuckDuckGo: {str(e)}")
    
    return results


def search_mycareersfuture(company_name: str, job_title: str) -> List[Dict]:
    """
    Search mycareersfuture.gov.sg for job postings
    """
    results = []
    try:
        # Try the API approach first
        search_query = f"{job_title} {company_name}"
        
        api_url = "https://api.mycareersfuture.gov.sg/v2/search"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        params = {
            'search': search_query,
            'limit': 20,
            'sortBy': 'relevancy'
        }
        
        response = requests.get(api_url, headers=headers, params=params, timeout=15, verify=False)
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                if 'results' in data:
                    for job in data['results'][:10]:  # Check top 10 results
                        job_company = job.get('company', {}).get('name', '') if isinstance(job.get('company'), dict) else ''
                        job_title_text = job.get('title', '')
                        
                        # More flexible matching
                        company_match = company_name.lower().replace('of', '').replace('the', '').strip()
                        job_company_clean = job_company.lower().replace('of', '').replace('the', '').strip()
                        
                        # Check if companies match (even partially)
                        if any(word in job_company_clean for word in company_match.split() if len(word) > 3):
                            results.append({
                                'title': job_title_text,
                                'company': job_company,
                                'url': f"https://www.mycareersfuture.gov.sg/job/view/{job.get('uuid', '')}",
                                'source': 'mycareersfuture.gov.sg',
                                'content': job.get('description', '') or job.get('summary', '')
                            })
            except json.JSONDecodeError:
                print("Error parsing MyCareersFuture JSON response")
    
    except Exception as e:
        print(f"Error searching mycareersfuture: {str(e)}")
    
    return results


def search_linkedin(company_name: str, job_title: str) -> List[Dict]:
    """
    Search LinkedIn for job postings - tries multiple approaches
    """
    results = []
    
    # Try direct LinkedIn search first
    try:
        search_query = f"{job_title} {company_name}"
        encoded_query = quote_plus(search_query)
        
        # LinkedIn Jobs API-like search
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={encoded_query}&location=Singapore&start=0"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.linkedin.com/jobs/search'
        }
        
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job cards
            job_cards = soup.find_all('li')
            
            for card in job_cards[:10]:
                try:
                    # Find the base card link
                    link_elem = card.find('a', class_='base-card__full-link')
                    if not link_elem:
                        continue
                    
                    job_url = link_elem.get('href', '')
                    if not job_url or 'linkedin.com/jobs/view' not in job_url:
                        continue
                    
                    # Extract job ID and construct clean URL
                    job_id_match = re.search(r'/view/(\d+)', job_url)
                    if job_id_match:
                        job_id = job_id_match.group(1)
                        # Extract company slug from URL if available
                        company_slug_match = re.search(r'at-([^/\?]+)', job_url)
                        if company_slug_match:
                            company_slug = company_slug_match.group(1)
                            clean_url = f"https://www.linkedin.com/jobs/view/{job_id}/?originalSubdomain=sg"
                        else:
                            clean_url = f"https://www.linkedin.com/jobs/view/{job_id}/?originalSubdomain=sg"
                    else:
                        clean_url = job_url
                    
                    # Get title
                    title_elem = card.find('h3', class_='base-search-card__title')
                    if not title_elem:
                        title_elem = card.find('span', class_='sr-only')
                    title = title_elem.text.strip() if title_elem else job_title
                    
                    # Get company
                    company_elem = card.find('h4', class_='base-search-card__subtitle')
                    if not company_elem:
                        company_elem = card.find('a', class_='hidden-nested-link')
                    company = company_elem.text.strip() if company_elem else company_name
                    
                    # Get location and snippet
                    location_elem = card.find('span', class_='job-search-card__location')
                    location = location_elem.text.strip() if location_elem else ''
                    
                    snippet_elem = card.find('p', class_='base-search-card__snippet')
                    snippet = snippet_elem.text.strip() if snippet_elem else ''
                    
                    # Check if company matches (flexible matching)
                    company_keywords = [word.lower() for word in company_name.split() if len(word) > 3]
                    company_match = any(keyword in company.lower() or keyword in title.lower() for keyword in company_keywords)
                    
                    if company_match:
                        results.append({
                            'title': title,
                            'company': company,
                            'url': clean_url,
                            'source': 'linkedin.com',
                            'content': f"{snippet}\nLocation: {location}" if location else snippet
                        })
                        print(f"Found LinkedIn job: {title} at {company}")
                
                except Exception as e:
                    print(f"Error parsing LinkedIn card: {str(e)}")
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
