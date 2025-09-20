# Streamlit Cloud Deployment Guide

## Quick Deploy for Streamlit Cloud

### Deploy Settings:
1. **Repository:** `YOUR_USERNAME/Resume-Relevance-System`
2. **Branch:** `main`
3. **Main file path:** `streamlit_app.py`
4. **Requirements:** Will use `requirements.txt` automatically

### Features Available:
- Dashboard with metrics and analytics
- Job management with skill requirements
- Resume upload (text paste or file upload)
- Individual and bulk evaluation
- Detailed scoring and feedback
- Analytics and reporting
- Data export functionality

### No Setup Required:
- Uses in-memory storage (session state)
- No database configuration needed
- No API keys required
- Minimal dependencies (just streamlit and pandas)

### Usage Instructions:
1. Create jobs with required skills
2. Upload resumes (text format recommended)
3. Evaluate individual resumes or bulk process
4. View detailed analytics and export reports

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