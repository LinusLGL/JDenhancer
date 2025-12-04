import streamlit as st
import os
from dotenv import load_dotenv
from job_search import search_job_postings
from openai_analyzer import extract_job_details
from batch_analyzer import parse_excel_paste, process_batch_job, format_as_excel_paste, create_downloadable_excel

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

# Create tabs for single and batch analysis
tab1, tab2 = st.tabs(["📝 Single Analysis", "📊 Batch Analysis"])

# ============= TAB 1: SINGLE ANALYSIS =============
with tab1:
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
                try:
                    # Search for job postings
                    search_results = search_job_postings(company_name, job_title)
                    
                    if not search_results:
                        st.info("🤖 No specific job postings found. Generating description using AI analysis...")
                        # Add debug info in an expander
                        with st.expander("🔍 Debug Info - Why no results?"):
                            st.text(f"Company: {company_name}")
                            st.text(f"Job Title: {job_title}")
                            st.text("The search tried multiple sources:")
                            st.text("- jobs.careers.gov.sg (via DuckDuckGo, Google, Bing)")
                            st.text("- mycareersfuture.gov.sg")
                            st.text("- linkedin.com")
                            st.text("\nNo matching results were found. AI will generate based on general knowledge.")
                    else:
                        st.success(f"✅ Found {len(search_results)} relevant job posting(s)!")
                except Exception as e:
                    st.warning(f"⚠️ Search encountered an issue: {str(e)}")
                    st.info("Generating description using AI analysis...")
                    search_results = []
            
            if search_results:
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
            
            # Always generate AI-enhanced description (whether search results found or not)
            st.subheader("🤖 AI-Enhanced Job Description")
            with st.spinner("🧠 Analyzing and generating job description with AI..."):
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

# ============= TAB 2: BATCH ANALYSIS =============
with tab2:
    st.subheader("📊 Batch Job Description Analysis")
    st.markdown("""
    Process multiple jobs at once by pasting data from Excel.
    
    **Instructions:**
    1. In Excel, select your data with headers: `Company Name`, `Job Title`, `Job Description`
    2. Copy the selected cells (Ctrl+C)
    3. Paste into the text box below (Ctrl+V)
    4. Click "Process Batch"
    """)
    
    # Example format
    with st.expander("📋 See Example Format"):
        st.code("""Company Name	Job Title	Job Description
Microsoft	UI UX developer	I do design of website
Google	Software Engineer	development of app
IBM	Director	""")
    
    # Input text area for pasted Excel data
    excel_data = st.text_area(
        "Paste Excel Data Here",
        placeholder="Company Name\tJob Title\tJob Description\nMicrosoft\tUI UX developer\tI do design of website\nGoogle\tSoftware Engineer\tdevelopment of app",
        height=200,
        help="Paste tab-separated data from Excel. No limit on number of rows."
    )
    
    # Process button
    col1, col2 = st.columns([1, 4])
    with col1:
        process_batch = st.button("🚀 Process Batch", type="primary", use_container_width=True)
    
    # Process batch
    if process_batch:
        if not excel_data.strip():
            st.error("⚠️ Please paste Excel data first.")
        else:
            # Parse the pasted data
            jobs = parse_excel_paste(excel_data)
            
            if not jobs:
                st.error("❌ Could not parse the data. Please ensure it's in the correct format with headers.")
            else:
                st.success(f"✅ Found {len(jobs)} job(s) to process")
                
                # Initialize results storage
                if 'batch_results' not in st.session_state:
                    st.session_state.batch_results = []
                
                st.session_state.batch_results = []
                
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Process each job
                for idx, job in enumerate(jobs):
                    status_text.text(f"Processing {idx + 1}/{len(jobs)}: {job['company_name']} - {job['job_title']}")
                    
                    result = process_batch_job(
                        job['company_name'],
                        job['job_title'],
                        job['job_description']
                    )
                    
                    # Store result
                    job_result = {
                        'company_name': job['company_name'],
                        'job_title': job['job_title'],
                        'job_description': job['job_description'],
                        'enhanced_description': result['enhanced_description'],
                        'sources_found': result['sources_found']
                    }
                    st.session_state.batch_results.append(job_result)
                    
                    # Update progress
                    progress_bar.progress((idx + 1) / len(jobs))
                
                status_text.text(f"✅ Completed processing {len(jobs)} job(s)!")
                
                # Display results summary
                st.markdown("---")
                st.subheader("📊 Results Summary")
                
                # Show results in expandable sections
                for idx, result in enumerate(st.session_state.batch_results, 1):
                    with st.expander(f"{idx}. {result['company_name']} - {result['job_title']}", expanded=False):
                        st.markdown(f"**Original Description:** {result['job_description'] or 'N/A'}")
                        st.markdown(f"**Sources Found:** {result['sources_found']}")
                        st.markdown("**Enhanced Description:**")
                        st.markdown(result['enhanced_description'])
                
                # Create downloadable outputs
                st.markdown("---")
                st.subheader("📥 Download Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Copy to clipboard button (shows formatted text)
                    copy_text = format_as_excel_paste(st.session_state.batch_results)
                    st.text_area(
                        "Copy this text to paste into Excel:",
                        value=copy_text,
                        height=200,
                        help="Select all (Ctrl+A) and copy (Ctrl+C), then paste into Excel"
                    )
                
                with col2:
                    # Download as file
                    download_data = create_downloadable_excel(st.session_state.batch_results)
                    st.download_button(
                        label="📥 Download as TSV File",
                        data=download_data,
                        file_name="batch_job_descriptions_enhanced.tsv",
                        mime="text/tab-separated-values",
                        help="Download as tab-separated file that can be opened in Excel"
                    )

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
