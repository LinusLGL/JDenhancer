# 🚀 Deploying to Streamlit Cloud

Follow these steps to deploy your Job Description Enhancer to Streamlit Cloud:

## Prerequisites

1. Push your code to GitHub (instructions below)
2. Have a Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))
3. Have an OpenAI API key

## Step 1: Push to GitHub

Your code is ready to push! Run these commands:

```bash
git add .
git commit -m "Initial commit: Job Description Enhancer"
git branch -M main
git push -u origin main
```

If you need to authenticate with GitHub, you may need to use a personal access token.

## Step 2: Deploy on Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Sign in** with your GitHub account
3. **Click "New app"**
4. **Configure your app**:
   - Repository: `LinusLGL/JD-Enhancer`
   - Branch: `main`
   - Main file path: `app.py`

5. **Add Secrets** (Important!):
   - Click on "Advanced settings"
   - Go to "Secrets" section
   - Add your OpenAI API key:
   ```toml
   OPENAI_API_KEY = "sk-your-actual-openai-api-key-here"
   ```

6. **Click "Deploy"**

Your app will be live at: `https://your-app-name.streamlit.app`

## Updating Your App

Whenever you push changes to GitHub, Streamlit Cloud will automatically redeploy your app!

## Troubleshooting

### "Module not found" errors
- Check that all dependencies are listed in `requirements.txt`

### "OpenAI API Key not configured"
- Verify you've added `OPENAI_API_KEY` in the Streamlit Cloud secrets section
- Make sure there are no extra quotes or spaces

### App is slow
- The free tier has resource limitations
- Consider optimizing web scraping or caching results

## Local Development

To run locally:
1. Copy `.env.example` to `.env`
2. Add your OpenAI API key to `.env`
3. Run: `streamlit run app.py`

## Security Notes

- **Never commit** your `.env` file or actual API keys
- Use Streamlit Cloud secrets for production
- Keep your OpenAI API key secure
