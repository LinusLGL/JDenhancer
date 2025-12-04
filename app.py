import streamlit as st
import os
from dotenv import load_dotenv
from job_search import search_job_postings
from openai_analyzer import extract_job_details
from batch_analyzer import parse_excel_paste, process_batch_job, process_batch_jobs_bulk, format_as_excel_paste, create_downloadable_excel

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="JD Enhancer | AI-Powered Job Descriptions",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern, futuristic design
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    /* Content wrapper */
    .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
        background: rgba(255, 255, 255, 0.98);
        border-radius: 24px;
        margin: 2rem auto;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
    }
    
    /* Header styling */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3rem !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.02em;
    }
    
    /* Subtitle */
    .subtitle {
        color: #64748b;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f8fafc;
        padding: 8px;
        border-radius: 16px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 500;
        border: none;
        background: transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 12px 16px;
        font-size: 0.95rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 12px;
        padding: 12px 32px;
        font-weight: 600;
        font-size: 1rem;
        border: none;
        transition: all 0.3s ease;
        letter-spacing: 0.02em;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }
    
    /* Cards/Expanders */
    .streamlit-expanderHeader {
        border-radius: 12px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: #f1f5f9;
        border-color: #cbd5e1;
    }
    
    /* Success/Info/Warning boxes */
    .stAlert {
        border-radius: 12px;
        border: none;
        padding: 16px 20px;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 8px;
    }
    
    /* Download button */
    .stDownloadButton > button {
        border-radius: 12px;
        background: #10b981;
        color: white;
        font-weight: 600;
        border: none;
        padding: 12px 24px;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        background: #059669;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1rem;
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Form styling */
    .stForm {
        background: #f8fafc;
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Smooth animations */
    * {
        transition: background-color 0.3s ease, border-color 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# Hero section
st.markdown("""
<div style="text-align: center; margin-bottom: 3rem;">
    <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem;">🚀 JD Enhancer</h1>
    <p class="subtitle">Transform job descriptions with AI-powered intelligence</p>
</div>
""", unsafe_allow_html=True)

# Create tabs for single and batch analysis
tab1, tab2 = st.tabs(["✨ Single Analysis", "⚡ Batch Analysis"])

# ============= TAB 1: SINGLE ANALYSIS =============
with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    # Create input form
    with st.form("job_search_form"):
        st.markdown("### 📋 Enter Job Details")
        st.markdown("<p style='color: #64748b; margin-bottom: 1.5rem;'>Fill in the details below to search and enhance job descriptions</p>", unsafe_allow_html=True)
        
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
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🔍 Search & Enhance", type="primary", use_container_width=True)

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
                    with st.expander(f"Result {idx}: {result['title']}", expanded=False):
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
            st.markdown("---")
            st.markdown("### 🤖 AI-Enhanced Job Description")
            with st.spinner("🧠 Analyzing and generating job description with AI..."):
                enhanced_description = extract_job_details(
                    search_results,
                    company_name,
                    job_title,
                    job_description
                )
                
                if enhanced_description:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%); 
                                padding: 2rem; 
                                border-radius: 16px; 
                                border-left: 4px solid #667eea;
                                margin: 1.5rem 0;">
                    """, unsafe_allow_html=True)
                    st.markdown(enhanced_description)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
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
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### ⚡ Batch Job Description Analysis")
    st.markdown("""
    <div style="background: #f8fafc; padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; border-left: 4px solid #667eea;">
        <p style="color: #64748b; margin-bottom: 1rem;"><strong>Process multiple jobs at once by pasting data from Excel.</strong></p>
        <p style="color: #64748b; margin: 0;">📌 <strong>Instructions:</strong></p>
        <ol style="color: #64748b; margin: 0.5rem 0 0 1.2rem;">
            <li>In Excel, select your data with headers: <code>Company Name</code>, <code>Job Title</code>, <code>Job Description</code></li>
            <li>Copy the selected cells (Ctrl+C)</li>
            <li>Paste into the text box below (Ctrl+V)</li>
            <li>Click "Process Batch"</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
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
                
                # Define progress callback
                def update_progress(message, progress):
                    status_text.text(message)
                    progress_bar.progress(progress)
                
                # Process all jobs in bulk with progress updates
                results = process_batch_jobs_bulk(jobs, progress_callback=update_progress)
                
                # Step 3: Store results
                for idx, (job, result) in enumerate(zip(jobs, results)):
                    job_result = {
                        'company_name': job['company_name'],
                        'job_title': job['job_title'],
                        'job_description': job['job_description'],
                        'enhanced_description': result['enhanced_description'],
                        'sources_found': result['sources_found']
                    }
                    st.session_state.batch_results.append(job_result)
                
                progress_bar.progress(1.0)
                status_text.text(f"✅ Completed processing {len(jobs)} job(s)!")
                
                # Display results summary
                st.markdown("---")
                st.subheader("📊 Results Summary")
                
                # Show results in expandable sections
                for idx, result in enumerate(st.session_state.batch_results, 1):
                    with st.expander(f"{idx}. {result['company_name']} - {result['job_title']}", expanded=False):
                        st.markdown(f"**Original Description:** {result['job_description'] or 'N/A'}")
                        st.markdown(f"**Sources Found:** {result['sources_found']}")
                        st.markdown("---")
                        st.markdown("### 🤖 AI-Enhanced Job Description")
                        st.markdown("""
                        <div style="background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%); 
                                    padding: 2rem; 
                                    border-radius: 16px; 
                                    border-left: 4px solid #667eea;
                                    margin: 1.5rem 0;">
                        """, unsafe_allow_html=True)
                        st.markdown(result['enhanced_description'])
                        st.markdown("</div>", unsafe_allow_html=True)
                
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
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 💡 About")
    st.markdown("""
    This application helps you enhance job descriptions by:
    
    **🔍 Searching** multiple job portals:
    - jobs.careers.gov.sg
    - mycareersfuture.gov.sg
    - linkedin.com
    
    **🤖 Extracting** key information using AI
    
    **✨ Generating** comprehensive job descriptions
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Setup")
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
        st.markdown("<div style='background: rgba(16, 185, 129, 0.2); padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0;'>✅ API Key Configured</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='background: rgba(239, 68, 68, 0.2); padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0;'>❌ API Key Not Found</div>", unsafe_allow_html=True)
        st.markdown("Set your `OPENAI_API_KEY` in Streamlit secrets or `.env` file")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📝 Example")
    st.markdown("""
    **Company:** Monetary Authority of Singapore
    
    **Job Title:** Deputy/ Assistant Director, Payments Department (Contract)
    """)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; opacity: 0.6; font-size: 0.85rem;'>Made with 💜 by JD Enhancer</div>", unsafe_allow_html=True)
