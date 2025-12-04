# 💼 Job Description Enhancer

A Streamlit application that searches multiple job portals and uses OpenAI to create enhanced, comprehensive job descriptions.

## Features

- 🔍 **Multi-Portal Search**: Searches across multiple job platforms:
  - jobs.careers.gov.sg
  - mycareersfuture.gov.sg
  - linkedin.com

- 🤖 **AI-Powered Analysis**: Uses OpenAI to extract and consolidate key information including:
  - Job overview and responsibilities
  - Required and preferred qualifications
  - Key competencies
  - Work environment details

- 📥 **Export Functionality**: Download enhanced job descriptions as text files

- 💡 **User-Friendly Interface**: Clean, intuitive Streamlit interface

## Prerequisites

- Python 3.8 or higher
- OpenAI API key

## Installation

1. **Clone or download this repository**

2. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your OpenAI API key**:
   - Copy `.env.example` to `.env`:
     ```bash
     copy .env.example .env
     ```
   - Edit `.env` and add your OpenAI API key:
     ```
     OPENAI_API_KEY=sk-your-actual-api-key-here
     ```

## Usage

1. **Start the application**:
   ```bash
   streamlit run app.py
   ```

2. **Fill in the form**:
   - **Company Name** (required): e.g., "Monetary Authority of Singapore"
   - **Job Title** (required): e.g., "Deputy/ Assistant Director, Payments Department (Contract)"
   - **Job Description** (optional): Add any existing description you have

3. **Click "Search & Enhance"**:
   - The app will search multiple job portals
   - Display found job postings with source URLs
   - Generate an AI-enhanced comprehensive job description

4. **Download the results**:
   - Use the download button to save the enhanced description

## Example

### Input:
```
Company Name: Monetary Authority of Singapore
Job Title: Deputy/ Assistant Director, Payments Department (Contract)
Job Description: (optional)
```

### Output:
The application will:
1. Find relevant job postings from multiple sources
2. Display source URLs (e.g., https://jobs.careers.gov.sg/jobs/hrp/16586910/...)
3. Generate a comprehensive enhanced job description with:
   - Job Overview
   - Key Responsibilities
   - Required Qualifications
   - Preferred Qualifications
   - Key Competencies
   - Work Environment & Benefits

## Project Structure

```
JD-Enhancer/
├── app.py                  # Main Streamlit application
├── job_search.py          # Web scraping and search functions
├── openai_analyzer.py     # OpenAI integration for content analysis
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore file
└── README.md             # This file
```

## Important Notes

### Web Scraping Limitations

- **jobs.careers.gov.sg**: May require specific parsing logic based on site structure
- **mycareersfuture.gov.sg**: Has an API that can be used (implemented in code)
- **linkedin.com**: Has strict anti-scraping measures; consider using their official API

The current implementation provides a foundation that may need to be adapted based on:
- Changes to website structures
- Rate limiting policies
- Authentication requirements

### API Costs

- The application uses OpenAI's API (default: gpt-4o-mini)
- Each search and enhancement operation will consume API credits
- Monitor your OpenAI usage at https://platform.openai.com/usage

### Rate Limiting

The application includes basic rate limiting (1-second delays between requests) to be respectful to job portal servers. Adjust if needed.

## Troubleshooting

### "OpenAI API Key not found"
- Ensure you've created a `.env` file (not `.env.example`)
- Verify your API key is correctly set in the `.env` file
- Make sure the `.env` file is in the same directory as `app.py`

### "No job postings found"
- Try different search terms
- Some portals may have changed their structure
- Check the console output for specific error messages

### Web scraping errors
- Websites may block automated requests
- Consider implementing proxies or using official APIs where available
- Some sites may require authentication

## Future Enhancements

- [ ] Add support for more job portals
- [ ] Implement caching to avoid repeated searches
- [ ] Add job matching/scoring functionality
- [ ] Support for bulk job description processing
- [ ] Integration with official APIs where available
- [ ] Advanced filtering and search options

## License

This project is provided as-is for educational and personal use.

## Disclaimer

This tool is for research and personal use. Always respect the terms of service of the job portals you're accessing. Consider using official APIs where available and ensure compliance with each platform's policies regarding data scraping and automated access.
