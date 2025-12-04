import io
from typing import List, Dict
from job_search import search_job_postings
from openai_analyzer import extract_job_details
import os
from openai import OpenAI

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


def process_batch_jobs_bulk(jobs_list: List[Dict[str, str]], progress_callback=None) -> List[Dict[str, any]]:
    """
    Process multiple jobs efficiently in chunks to handle unlimited rows.
    First searches for sources for each job, then processes in batches of 20.
    Returns list of results with enhanced descriptions and sources.
    """
    results = []
    CHUNK_SIZE = 20  # Process 20 jobs at a time to avoid token limits
    
    # Step 1: Search for sources for each job
    jobs_with_sources = []
    total_jobs = len(jobs_list)
    
    for idx, job in enumerate(jobs_list):
        if progress_callback:
            progress_callback(f"🔍 Searching sources for job {idx + 1}/{total_jobs}: {job['company_name']}", 
                            (idx + 1) / total_jobs * 0.4)  # 0-40% for searching
        try:
            search_results = search_job_postings(job['company_name'], job['job_title'])
            jobs_with_sources.append({
                'company_name': job['company_name'],
                'job_title': job['job_title'],
                'job_description': job.get('job_description', ''),
                'search_results': search_results,
                'sources_found': len(search_results) if search_results else 0
            })
        except Exception as e:
            jobs_with_sources.append({
                'company_name': job['company_name'],
                'job_title': job['job_title'],
                'job_description': job.get('job_description', ''),
                'search_results': [],
                'sources_found': 0
            })
    
    # Step 2: Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets["openai"]["api_key"]
        except:
            try:
                api_key = st.secrets["OPENAI_API_KEY"]
            except:
                pass
    
    if not api_key:
        return [{
            'status': 'error',
            'enhanced_description': 'Error: OpenAI API key not configured',
            'sources_found': 0
        } for _ in jobs_list]
    
    client = OpenAI(api_key=api_key)
    
    # Step 3: Process jobs in chunks
    all_results = []
    num_chunks = (len(jobs_with_sources) + CHUNK_SIZE - 1) // CHUNK_SIZE
    
    for chunk_idx in range(num_chunks):
        start_idx = chunk_idx * CHUNK_SIZE
        end_idx = min((chunk_idx + 1) * CHUNK_SIZE, len(jobs_with_sources))
        chunk = jobs_with_sources[start_idx:end_idx]
        
        if progress_callback:
            progress_callback(f"🤖 Processing batch {chunk_idx + 1}/{num_chunks} ({len(chunk)} jobs)...", 
                            0.4 + (chunk_idx / num_chunks) * 0.6)  # 40-100% for AI processing
        
        # Build context for this chunk
        context = "Process the following jobs and generate enhanced job descriptions for each:\n\n"
        
        for idx, job_data in enumerate(chunk, start_idx + 1):
            context += f"--- JOB {idx} ---\n"
            context += f"Company: {job_data['company_name']}\n"
            context += f"Job Title: {job_data['job_title']}\n"
            
            if job_data.get('job_description'):
                context += f"Existing Description: {job_data['job_description'][:200]}\n"
            
            if job_data['search_results']:
                context += f"\nFound {len(job_data['search_results'])} job posting(s):\n"
                for src_idx, result in enumerate(job_data['search_results'][:2], 1):  # Limit to 2 sources
                    context += f"  Source {src_idx}: {result['source']}\n"
                    context += f"  Title: {result['title'][:100]}\n"
                    if result.get('content'):
                        content = result['content'][:500]  # Limit content
                        context += f"  Content: {content}\n"
            else:
                context += "\nNo job postings found.\n"
            
            context += "\n"
        
        # Create chunk prompt
        prompt = f"""{context}

For each job above, generate a concise enhanced job description following this format:

For each job, output:
**JOB [number]: [Company Name] - [Job Title]**

**Enhanced Job Description**: Write a single, concise paragraph of exactly 50-60 words that combines both the job overview and key responsibilities. This should be a cohesive summary that describes the role's purpose and main duties in flowing, professional statement format.

---

Important:
- Use the found job postings as reference when available
- If no postings found, use your knowledge of the company and role
- Keep each description to exactly 50-60 words
- Make it professional and accurate
- Separate each job with "---"
"""
        
        try:
            # Call OpenAI API for this chunk
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert HR professional who specializes in creating comprehensive job descriptions. You excel at extracting key information from multiple sources and consolidating them into clear, professional job descriptions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=200 * len(chunk)  # Dynamic token allocation
            )
            
            # Parse the response
            full_response = response.choices[0].message.content
            
            # Split by job separators
            job_descriptions = full_response.split('---')
            
            # Match descriptions to jobs in this chunk
            for local_idx, job_data in enumerate(chunk):
                global_idx = start_idx + local_idx
                # Try to find the corresponding description
                enhanced_desc = ""
                for desc in job_descriptions:
                    if f"JOB {global_idx + 1}:" in desc or job_data['company_name'] in desc:
                        enhanced_desc = desc.strip()
                        break
                
                if not enhanced_desc and local_idx < len(job_descriptions):
                    enhanced_desc = job_descriptions[local_idx].strip()
                
                all_results.append({
                    'status': 'success',
                    'enhanced_description': enhanced_desc if enhanced_desc else f"**Enhanced Job Description**: Unable to generate description for this role.",
                    'sources_found': job_data['sources_found']
                })
            
        except Exception as e:
            # Fallback to individual processing for this chunk
            for job_data in chunk:
                try:
                    enhanced_description = extract_job_details(
                        job_data['search_results'],
                        job_data['company_name'],
                        job_data['job_title'],
                        job_data['job_description']
                    )
                    all_results.append({
                        'status': 'success',
                        'enhanced_description': enhanced_description,
                        'sources_found': job_data['sources_found']
                    })
                except Exception as inner_e:
                    all_results.append({
                        'status': 'error',
                        'enhanced_description': f"Error: {str(inner_e)}",
                        'sources_found': 0
                    })
    
    return all_results


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
