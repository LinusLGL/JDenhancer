import streamlit as st
import os
from dotenv import load_dotenv
from job_search import search_job_postings
from openai_analyzer import extract_job_details

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Job Description Enhancer",
    page_icon="💼",
    layout="wide"
)

# Main title
st.title("💼 Job Description Enhancer")
st.markdown("Find and enhance job descriptions using AI-powered search and analysis")

# Create input form
with st.form("job_search_form"):
    st.subheader("Enter Job Details")
    
    company_name = st.text_input(
        "Company Name *",
        placeholder="e.g., Monetary Authority of Singapore",
        help="Enter the name of the company"
    )
    
    job_title = st.text_input(
        "Job Title *",
        placeholder="e.g., Deputy/ Assistant Director, Payments Department (Contract)",
        help="Enter the job title you're searching for"
    )
    
    job_description = st.text_area(
        "Job Description (Optional)",
        placeholder="Enter any additional job description details you already have...",
        help="Optional: Add any existing job description to refine the search",
        height=150
    )
    
    submitted = st.form_submit_button("🔍 Search & Enhance", type="primary")

# Process form submission
if submitted:
    if not company_name or not job_title:
        st.error("⚠️ Please fill in both Company Name and Job Title fields.")
    else:
        with st.spinner("🔎 Searching for job postings..."):
            # Search for job postings
            search_results = search_job_postings(company_name, job_title)
            
            if not search_results:
                st.warning("❌ No job postings found. Please try different search terms.")
            else:
                st.success(f"✅ Found {len(search_results)} relevant job posting(s)!")
                
                # Display search results
                st.subheader("📋 Found Job Postings")
                for idx, result in enumerate(search_results, 1):
                    with st.expander(f"Result {idx}: {result['title']}", expanded=(idx == 1)):
                        st.markdown(f"**Source:** [{result['source']}]({result['url']})")
                        st.markdown(f"**Company:** {result['company']}")
                        
                        if result.get('content'):
                            st.markdown("**Job Posting Content:**")
                            st.text_area(
                                "Raw Content",
                                value=result['content'][:1000] + ("..." if len(result['content']) > 1000 else ""),
                                height=200,
                                key=f"content_{idx}",
                                disabled=True
                            )
                
                # Analyze with OpenAI
                st.subheader("🤖 AI-Enhanced Job Description")
                with st.spinner("🧠 Analyzing job postings with OpenAI..."):
                    enhanced_description = extract_job_details(
                        search_results,
                        company_name,
                        job_title,
                        job_description
                    )
                    
                    if enhanced_description:
                        st.markdown("---")
                        st.markdown(enhanced_description)
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Enhanced Description",
                            data=enhanced_description,
                            file_name=f"{company_name}_{job_title}_enhanced.txt".replace(" ", "_").replace("/", "-"),
                            mime="text/plain"
                        )
                    else:
                        st.error("❌ Failed to generate enhanced description. Please try again.")

# Sidebar information
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This application helps you enhance job descriptions by:
    
    1. **Searching** multiple job portals:
       - jobs.careers.gov.sg
       - mycareersfuture.gov.sg
       - linkedin.com
    
    2. **Extracting** key information using AI
    
    3. **Generating** comprehensive job descriptions
    """)
    
    st.header("⚙️ Setup")
    # Check for API key in Streamlit secrets first, then environment
    api_key = None
    try:
        # Try new structure: [openai] api_key
        api_key = st.secrets["openai"]["api_key"]
    except:
        try:
            # Try flat structure: OPENAI_API_KEY
            api_key = st.secrets["OPENAI_API_KEY"]
        except:
            pass
    
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        st.success("✅ OpenAI API Key configured")
    else:
        st.error("❌ OpenAI API Key not found")
        st.markdown("Set your `OPENAI_API_KEY` in Streamlit secrets or `.env` file")
    
    st.header("📝 Example")
    st.markdown("""
    **Company:** Monetary Authority of Singapore
    
    **Job Title:** Deputy/ Assistant Director, Payments Department (Contract)
    """)
