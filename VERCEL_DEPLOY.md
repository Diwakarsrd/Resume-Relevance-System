# Vercel Deployment Guide - Complete System

## 🚀 Deploy Full Resume Relevance System to Vercel

### Single Command Deployment

```bash
vercel --prod
```

### Complete Setup Steps

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Navigate to project directory**:
   ```bash
   cd resume-relevance-mvp
   ```

4. **Deploy the complete system**:
   ```bash
   vercel --prod
   ```

5. **Set environment variables**:
   ```bash
   vercel env add GEMINI_API_KEY production
   vercel env add VERCEL production
   ```
   Enter your Gemini API key and "true" for VERCEL variable

### Alternative: GitHub Integration

1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Import from GitHub: `https://github.com/Diwakarsrd/Resume-Relevance-System`
4. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: ./
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)
   - **Install Command**: pip install -r requirements.txt
5. **Environment Variables**:
   - `GEMINI_API_KEY`: Your Gemini API key
   - `VERCEL`: true
6. Click **Deploy**

### Deployed Endpoints

#### API Endpoints (Full FastAPI Backend)
- **Root**: `https://your-project.vercel.app/api/`
- **API Docs**: `https://your-project.vercel.app/api/docs`
- **Health Check**: `https://your-project.vercel.app/api/health`
- **Create Job**: `POST /api/jobs`
- **Upload Resume**: `POST /api/resumes` 
- **Evaluate**: `POST /api/evaluate`
- **Bulk Evaluate**: `POST /api/bulk-evaluate`
- **List Jobs**: `GET /api/jobs`
- **List Resumes**: `GET /api/resumes`
- **List Evaluations**: `GET /api/evaluations`

#### Dashboard
- **Streamlit Dashboard**: `https://your-project.vercel.app/`
- **Dashboard Direct**: `https://your-project.vercel.app/dashboard/`

### Features Included

✅ **Complete FastAPI Backend**
- All original endpoints preserved
- AI-powered resume parsing
- Comprehensive scoring system
- Job description parsing
- Bulk evaluation capabilities

✅ **Full Streamlit Dashboard**
- Job Management with AI parsing
- Resume Upload & Analysis
- Bulk Evaluation interface
- Analytics & Insights
- Export functionality

✅ **Database**
- Automatic SQLite setup
- In-memory database for serverless
- All models and relationships preserved

✅ **File Uploads**
- PDF/DOCX/TXT support
- Temporary file handling
- Structured parsing

### Testing the Deployment

1. **Test API Health**:
   ```bash
   curl https://your-project.vercel.app/api/health
   ```

2. **Test Job Creation**:
   ```bash
   curl -X POST https://your-project.vercel.app/api/jobs \
     -F "title=Python Developer" \
     -F "jd_text=Looking for Python developer with FastAPI experience" \
     -F "must_have=python,fastapi"
   ```

3. **Access Dashboard**:
   Open `https://your-project.vercel.app/` in your browser

### Important Notes

1. **Database**: Uses in-memory SQLite on Vercel (data doesn't persist between deployments)
2. **File Storage**: Temporary files are cleaned up after each request
3. **Cold Starts**: First request may take longer due to serverless nature
4. **Timeouts**: Functions have 60-second timeout limit

### For Production Use

Consider these upgrades:
- **Database**: Use Vercel KV, PlanetScale, or Supabase for persistent storage
- **File Storage**: Use AWS S3, Cloudinary, or Vercel Blob for file uploads
- **Caching**: Add Redis for better performance

### Troubleshooting

- Check Vercel function logs in the dashboard
- Ensure all dependencies are in requirements.txt
- Verify environment variables are set correctly
- Check function timeout limits for large file uploads