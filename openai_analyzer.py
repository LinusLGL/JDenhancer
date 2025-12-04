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
    # Try to get API key from environment (works for both local .env and Streamlit secrets)
    api_key = os.getenv("OPENAI_API_KEY")
    
    # If not in environment, try Streamlit secrets directly
    if not api_key:
        try:
            import streamlit as st
            # Try new structure: [openai] api_key
            api_key = st.secrets["openai"]["api_key"]
        except:
            try:
                # Try flat structure: OPENAI_API_KEY
                api_key = st.secrets["OPENAI_API_KEY"]
            except:
                pass
    
    if not api_key:
        return "Error: OpenAI API key not configured. Please set OPENAI_API_KEY in your Streamlit secrets or .env file."
    
    client = OpenAI(api_key=api_key)
    
    # Prepare context from search results
    context = f"Company: {company_name}\nJob Title: {job_title}\n\n"
    
    if existing_description:
        context += f"Existing Job Description:\n{existing_description}\n\n"
    
    # Check if we have search results
    if search_results and len(search_results) > 0:
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
        
        # Create prompt for OpenAI with search results
        prompt = f"""You are an expert HR professional and job description writer. Based on the job postings found, create a comprehensive and enhanced job description.

{context}

Please analyze the above job postings and create an enhanced job description:

**Enhanced Job Description**: Write a single, concise paragraph of exactly 50-60 words that combines both the job overview and key responsibilities. This should be a cohesive summary that describes the role's purpose and main duties in flowing, professional statement format. Extract the most important information from the sources and present it as a unified narrative.

Focus on extracting accurate information from the sources rather than making assumptions. If multiple sources conflict, prioritize information from official government job portals (careers.gov.sg, mycareersfuture.gov.sg) over other sources.
"""
    else:
        # No search results found - use AI to generate based on company analysis
        prompt = f"""You are an expert HR professional and job description writer. Based on your knowledge of the company and typical job roles, generate an accurate and professional job description.

{context}

Using your understanding of:
- The company "{company_name}" (its industry, mission, and typical organizational structure)
- The job title "{job_title}" (typical responsibilities and requirements for this role)
- Any additional context provided

Please generate a concise, accurate job description:

**Enhanced Job Description**: Write a single, concise paragraph of exactly 50-60 words that combines both the job overview and key responsibilities. This should be a cohesive summary that describes the role's purpose and main duties in flowing, professional statement format. Base this on:
   - Industry standards for this job title
   - Typical functions within organizations like {company_name}
   - The level of seniority implied by the job title
   - Common expectations for this type of position

Keep it professional, realistic, and focused on the most critical aspects of the role. Be specific and actionable in describing responsibilities.
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
    
    # If not in environment, try Streamlit secrets
    if not api_key:
        try:
            import streamlit as st
            # Try new structure: [openai] api_key
            api_key = st.secrets["openai"]["api_key"]
        except:
            try:
                # Try flat structure: OPENAI_API_KEY
                api_key = st.secrets["OPENAI_API_KEY"]
            except:
                pass
    
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
