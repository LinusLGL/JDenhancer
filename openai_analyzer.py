import os
from typing import List, Dict
from openai import OpenAI

def extract_job_details(
    search_results: List[Dict],
    company_name: str,
    job_title: str,
    existing_description: str = ""
) -> str:
    """
    Use OpenAI to extract and consolidate key responsibilities and information
    from job search results
    """
    
    # Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Error: OpenAI API key not configured. Please set OPENAI_API_KEY in your .env file."
    
    client = OpenAI(api_key=api_key)
    
    # Prepare context from search results
    context = f"Company: {company_name}\nJob Title: {job_title}\n\n"
    
    if existing_description:
        context += f"Existing Job Description:\n{existing_description}\n\n"
    
    context += "Found Job Postings:\n\n"
    
    for idx, result in enumerate(search_results, 1):
        context += f"--- Source {idx}: {result['source']} ---\n"
        context += f"URL: {result['url']}\n"
        context += f"Title: {result['title']}\n"
        context += f"Company: {result['company']}\n"
        if result.get('content'):
            # Limit content length to avoid token limits
            content = result['content'][:4000]
            context += f"Content:\n{content}\n\n"
    
    # Create prompt for OpenAI
    prompt = f"""You are an expert HR professional and job description writer. Based on the job postings found, create a comprehensive and enhanced job description.

{context}

Please analyze the above job postings and create an enhanced job description that includes:

1. **Job Overview**: A clear summary of the role and its importance to the organization

2. **Key Responsibilities**: Extract and consolidate the main duties and responsibilities from all sources. List them as bullet points, organized by priority or theme.

3. **Required Qualifications**: 
   - Education requirements
   - Years of experience
   - Essential skills and competencies
   - Professional certifications (if any)

4. **Preferred Qualifications**: Additional skills or experience that would be beneficial

5. **Key Competencies**: Important soft skills and attributes for success in this role

6. **Work Environment & Benefits** (if mentioned): Working conditions, team structure, benefits, etc.

Format the output in clear markdown with proper headings and bullet points. Make it professional, comprehensive, and easy to read. Focus on extracting accurate information from the sources rather than making assumptions.

If multiple sources conflict, prioritize information from official government job portals (careers.gov.sg, mycareersfuture.gov.sg) over other sources.
"""
    
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using gpt-4o-mini for cost efficiency; can be changed to gpt-4 for better quality
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
            max_tokens=2000
        )
        
        # Extract the response
        enhanced_description = response.choices[0].message.content
        return enhanced_description
    
    except Exception as e:
        return f"Error generating enhanced description: {str(e)}\n\nPlease check your OpenAI API key and ensure you have sufficient credits."


def analyze_job_match(
    job_content: str,
    user_profile: str,
    job_title: str
) -> Dict[str, any]:
    """
    Optional: Analyze how well a candidate matches the job requirements
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"error": "OpenAI API key not configured"}
    
    client = OpenAI(api_key=api_key)
    
    prompt = f"""Analyze the match between this job posting and candidate profile:

Job Title: {job_title}

Job Requirements:
{job_content}

Candidate Profile:
{user_profile}

Provide a match analysis including:
1. Match Score (0-100%)
2. Matching Qualifications
3. Missing Qualifications
4. Recommendations for the candidate
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert career advisor who helps candidates understand their fit for job positions."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return {
            "analysis": response.choices[0].message.content,
            "success": True
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }
