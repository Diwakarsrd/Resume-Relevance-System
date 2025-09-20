# 🚀 Streamlit Cloud Deployment Guide

## 🆘 QUICK FIX for Requirements Error

If you're getting a requirements installation error, try these fixes:

### Option 1: Use Minimal Setup
1. **Rename your main file** in Streamlit Cloud settings:
   - Change from: `streamlit_app.py`
   - To: `streamlit_app_simple.py`

### Option 2: Use Simplified Requirements
1. **In your GitHub repo**, replace `requirements.txt` with:
```txt
streamlit
requests
pandas
plotly
fastapi
uvicorn
python-multipart
```

### Option 3: Restart with Clean Deploy
1. **Delete the app** in Streamlit Cloud
2. **Create new app** with these exact settings:
   - Repository: `YOUR_USERNAME/Resume-Relevance-System`
   - Branch: `main` 
   - Main file: `streamlit_app_simple.py`

---

## Quick Deploy Button
[![Deploy to Streamlit Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy)

## 📋 Prerequisites
1. GitHub account
2. Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))
3. Google Gemini API key (optional for AI features)

## 🔧 Deployment Steps

### 1. Fork or Clone Repository
```bash
git clone https://github.com/Diwakarsrd/Resume-Relevance-System.git
cd Resume-Relevance-System
```

### 2. Push to Your GitHub Repository
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/Resume-Relevance-System.git
git push origin main
```

### 3. Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Click "New app"**
3. **Connect your GitHub repository**
4. **Set the following:**
   - Repository: `YOUR_USERNAME/Resume-Relevance-System`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
   - App URL: `your-app-name` (customize as needed)

### 4. Configure Secrets (Optional)

In your Streamlit Cloud app settings:

1. **Go to "Settings" → "Secrets"**
2. **Add the following:**
```toml
[general]
GEMINI_API_KEY = "your_actual_gemini_api_key"
```

### 5. Deploy!
Click "Deploy" and wait for your app to build and launch.

## 🌐 App URLs
- **Main App:** `https://your-app-name.streamlit.app`
- **API Docs:** Available within the app (backend runs internally)

## 📱 Features Available
✅ **Dashboard Overview** - System metrics and analytics  
✅ **Job Management** - Create and manage job postings  
✅ **Resume Upload** - PDF/DOCX/TXT file processing  
✅ **Bulk Evaluation** - Process multiple resumes  
✅ **Analytics** - Charts and insights  
✅ **AI-Powered Parsing** - Smart skill extraction  

## 🔄 Updates
Any changes pushed to your GitHub repository will automatically redeploy the app.

## 🆘 Troubleshooting

### Common Issues:

**1. App won't start:**
- Check the logs in Streamlit Cloud dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify the main file path is `streamlit_app.py`

**2. Backend API not responding:**
- The app includes an embedded FastAPI server
- Initial startup may take 30-60 seconds
- Check the "System Status" in the sidebar

**3. File upload errors:**
- Streamlit Cloud has file size limits
- Large files may timeout
- Try smaller test files first

**4. AI features not working:**
- Add your `GEMINI_API_KEY` to secrets
- Ensure the API key is valid and has quota

### Performance Tips:
- First load may be slow as dependencies install
- Subsequent loads are much faster
- Use caching for better performance

## 🔗 Additional Resources
- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-cloud)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management)
- [GitHub Integration](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app)

## 📞 Support
If you encounter issues:
1. Check the Streamlit Cloud logs
2. Review this deployment guide
3. Test locally first with `streamlit run streamlit_app.py`