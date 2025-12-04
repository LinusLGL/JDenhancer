import io
from typing import List, Dict
from job_search import search_job_postings
from openai_analyzer import extract_job_details

def parse_excel_paste(text: str) -> List[Dict[str, str]]:
    """
    Parse Excel data pasted as tab-separated text.
    Expected format:
    Company Name	Job Title	Job Description
    Microsoft	UI UX developer	I do design of website
    Google	Software Engineer	development of app
    """
    lines = text.strip().split('\n')
    if len(lines) < 2:
        return []
    
    # Parse header
    header = lines[0].split('\t')
    if len(header) < 2:
        return []
    
    # Parse data rows
    jobs = []
    for line in lines[1:]:
        if not line.strip():
            continue
        
        columns = line.split('\t')
        # Pad with empty strings if columns are missing
        while len(columns) < len(header):
            columns.append('')
        
        job_data = {
            'company_name': columns[0].strip() if len(columns) > 0 else '',
            'job_title': columns[1].strip() if len(columns) > 1 else '',
            'job_description': columns[2].strip() if len(columns) > 2 else ''
        }
        
        # Only add if company name and job title are present
        if job_data['company_name'] and job_data['job_title']:
            jobs.append(job_data)
    
    return jobs


def process_batch_job(company_name: str, job_title: str, job_description: str = "") -> Dict[str, str]:
    """
    Process a single job in the batch.
    Returns the enhanced description or error message.
    """
    try:
        # Search for job postings
        search_results = search_job_postings(company_name, job_title)
        
        # Generate enhanced description
        enhanced_description = extract_job_details(
            search_results,
            company_name,
            job_title,
            job_description
        )
        
        return {
            'status': 'success',
            'enhanced_description': enhanced_description,
            'sources_found': len(search_results) if search_results else 0
        }
    except Exception as e:
        return {
            'status': 'error',
            'enhanced_description': f"Error: {str(e)}",
            'sources_found': 0
        }


def format_as_excel_paste(jobs_data: List[Dict]) -> str:
    """
    Format the results back as tab-separated text for easy pasting into Excel.
    """
    # Header
    output = "Company Name\tJob Title\tJob Description\tEnhanced Description\tSources Found\n"
    
    # Data rows
    for job in jobs_data:
        company = job.get('company_name', '')
        title = job.get('job_title', '')
        original_desc = job.get('job_description', '')
        enhanced_desc = job.get('enhanced_description', '').replace('\n', ' ').replace('\t', ' ')
        sources = str(job.get('sources_found', 0))
        
        output += f"{company}\t{title}\t{original_desc}\t{enhanced_desc}\t{sources}\n"
    
    return output


def create_downloadable_excel(jobs_data: List[Dict]) -> bytes:
    """
    Create a downloadable file with the results.
    Returns tab-separated text that can be opened in Excel.
    """
    content = format_as_excel_paste(jobs_data)
    return content.encode('utf-8')
