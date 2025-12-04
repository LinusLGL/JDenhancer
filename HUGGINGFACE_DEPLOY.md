# Hugging Face Spaces Deployment Guide

## Quick Deploy to Hugging Face

### Method 1: Upload Files Directly

1. Go to your Space: https://huggingface.co/spaces/AlterniteAvacado/JDenhancer/tree/main

2. Click "Files" → "Add file" → "Upload files"

3. Upload these files:
   - `app.py`
   - `job_search.py`
   - `openai_analyzer.py`
   - `batch_analyzer.py`
   - `requirements.txt`
   - `README_HF.md` (rename to `README.md` when uploading)

4. Go to Settings → Variables & Secrets → New secret:
   - Name: `OPENAI_API_KEY`
   - Value: Your OpenAI API key (starts with sk-proj-...)

5. The app will automatically build and deploy!

---

### Method 2: Sync with GitHub (Recommended)

1. Go to your Space settings: https://huggingface.co/spaces/AlterniteAvacado/JDenhancer/settings

2. Scroll to "Repository" section

3. Click "Import from GitHub repository"

4. Enter: `LinusLGL/JD-Enhancer`

5. Click "Import"

6. Add your OpenAI API key in Settings → Variables & Secrets

7. Done! It will auto-sync with your GitHub repo

---

## Configure Secrets

### Required Secret:
- `OPENAI_API_KEY` - Your OpenAI API key

### How to add:
1. Go to https://huggingface.co/spaces/AlterniteAvacado/JDenhancer/settings
2. Scroll to "Variables and secrets"
3. Click "New secret"
4. Name: `OPENAI_API_KEY`
5. Value: `sk-proj-...` (your key)
6. Click "Save"

---

## Update .streamlit/secrets.toml Access

Your app currently accesses secrets via `st.secrets["openai"]["api_key"]`. 
Hugging Face Spaces provides secrets as environment variables.

The current code already handles this with fallback:
```python
api_key = st.secrets["openai"]["api_key"]  # Streamlit Cloud
# Falls back to:
api_key = os.getenv("OPENAI_API_KEY")  # Hugging Face / Local
```

---

## Verify Deployment

1. Go to: https://huggingface.co/spaces/AlterniteAvacado/JDenhancer
2. Wait for build to complete (usually 2-5 minutes)
3. Test with:
   - Company: Science Centre Board
   - Job Title: Senior Associate, Corporate Communications
4. Should show job postings!

---

## Troubleshooting

### App not starting?
- Check "Logs" tab in your Space
- Verify all files are uploaded
- Verify `OPENAI_API_KEY` secret is set

### No job results?
- Rate limiting may occur - wait 30 seconds between searches
- Check logs for error messages

### Need to update?
- **With GitHub sync**: Just push to your GitHub repo
- **Without GitHub sync**: Re-upload changed files in Files tab
