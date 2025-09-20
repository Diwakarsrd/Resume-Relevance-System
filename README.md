# Resume Relevance Check System 🎯

**AI-Powered Resume Evaluation Platform for Innomatics Research Labs**

A comprehensive automated system that evaluates resumes against job requirements at scale, providing consistent scoring, detailed feedback, and actionable insights for both recruiters and candidates.

## 🌟 Key Features

### For Placement Teams
- **Automated Evaluation**: Process thousands of resumes quickly and consistently
- **Intelligent Scoring**: 0-100 relevance scores with detailed breakdowns
- **Bulk Processing**: Evaluate all resumes for a job posting in one click
- **Advanced Dashboard**: Filter, search, and export evaluation results
- **Analytics**: Comprehensive insights and trend analysis

### For Candidates
- **Detailed Feedback**: Specific improvement suggestions
- **Gap Analysis**: Missing skills, certifications, and experience areas
- **Action Plans**: Prioritized roadmap for profile enhancement
- **Skill Matching**: Fuzzy matching with synonym recognition

### AI-Powered Capabilities
- **Smart Parsing**: Extract structured data from resumes and job descriptions
- **Semantic Analysis**: Context-aware evaluation using embeddings
- **Comprehensive Scoring**: Multi-criteria evaluation (skills, education, experience, projects)
- **Intelligent Feedback**: Personalized improvement recommendations

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │    FastAPI      │    │   SQLite DB     │
│   Dashboard     │◄──►│    Backend      │◄──►│   Storage       │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   File Upload   │    │   AI Processing │    │   Results &     │
│   & Display     │    │   (Gemini AI)   │    │   Analytics     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd resume-relevance-mvp
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file with your Gemini API key
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

4. **Start the backend server**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Launch the dashboard** (in a new terminal)
   ```bash
   streamlit run app/streamlit_app.py
   ```

6. **Run the test suite**
   ```bash
   python test_system.py
   ```

### Access Points
- **API Documentation**: http://localhost:8000/docs
- **Streamlit Dashboard**: http://localhost:8501
- **Backend API**: http://localhost:8000

## 📊 Usage Guide

### 1. Job Management
- **Create Jobs**: Upload job descriptions with AI-powered parsing
- **Auto-Extraction**: System automatically identifies required skills, education, experience
- **Manual Override**: Refine extracted information as needed

### 2. Resume Processing
- **Upload**: Support for PDF and DOCX formats
- **Smart Parsing**: Extract skills, education, experience, projects, certifications
- **Structured Storage**: All data stored in searchable format

### 3. Evaluation Process
- **Individual**: Evaluate single resume against specific job
- **Bulk**: Process all resumes for a job posting
- **Comprehensive Scoring**: Multiple criteria with weighted algorithms

### 4. Dashboard Features
- **Overview**: Real-time statistics and recent activity
- **Filtering**: By job, verdict, score range, date
- **Export**: CSV download for external analysis
- **Analytics**: Score distributions, trending skills, insights

## 🧮 Scoring Algorithm

### Multi-Criteria Evaluation (Weighted)

| Criteria | Weight | Description |
|----------|--------|-------------|
| **Must-Have Skills** | 35% | Critical technical skills matching |
| **Education** | 20% | Degree level and field alignment |
| **Experience** | 20% | Years and relevance of work history |
| **Nice-to-Have Skills** | 15% | Additional valuable skills |
| **Projects** | 10% | Relevant project portfolio |
| **Certifications** | Bonus | Up to +20 points for relevant certs |

### Advanced Matching
- **Fuzzy Matching**: Handles variations and typos (70% threshold)
- **Synonym Recognition**: Related skills (JS/JavaScript, ML/Machine Learning)
- **Semantic Analysis**: Context-aware evaluation using AI embeddings

### Verdict Classification
- **High (80-100%)**: Excellent match, strong candidate
- **Medium (60-79%)**: Good match, some gaps to address
- **Low (0-59%)**: Significant skill gaps, major development needed

## 🛠️ Technical Implementation

### Backend (FastAPI)
```python
# Core modules
app/
├── main.py          # API endpoints and routing
├── models.py        # Database models (SQLModel)
├── parsers.py       # Document parsing and AI extraction
├── scoring.py       # Evaluation algorithms and feedback
└── streamlit_app.py # Dashboard interface
```

### Key API Endpoints
```
POST /api/jobs              # Create job with AI parsing
POST /api/resumes           # Upload and parse resume
POST /api/evaluate          # Single evaluation
POST /api/bulk-evaluate     # Bulk processing
GET  /api/jobs              # List jobs with pagination
GET  /api/resumes           # List resumes with pagination
GET  /api/evaluations       # List evaluations with filtering
```

### Database Schema
```sql
-- Core entities
Jobs: id, title, jd_text, must_have[], nice_to_have[], location
Candidates: id, name, email, university, location
Resumes: id, candidate_id, file_path, parsed_text, parsed_json{}
Evaluations: id, resume_id, job_id, scores, verdict, feedback
```

## 📈 Analytics & Insights

### Available Metrics
- **Score Distributions**: By job, time period, candidate demographics
- **Skill Gap Analysis**: Most frequently missing skills across evaluations
- **Trend Analysis**: Evaluation patterns over time
- **Performance Metrics**: Average scores, verdict distributions

### Export Capabilities
- **CSV Reports**: Detailed evaluation results with all metrics
- **Filtered Data**: Export based on custom criteria
- **Bulk Analysis**: Process large datasets for insights

## 🔧 Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your_google_gemini_api_key
DATABASE_URL=sqlite:///data.db  # Optional: custom database
UPLOAD_DIR=uploads/             # Optional: custom upload directory
```

### Customization Options
- **Scoring Weights**: Adjust criteria importance in `scoring.py`
- **Skill Synonyms**: Extend synonym mapping for better matching
- **Verdict Thresholds**: Modify High/Medium/Low boundaries
- **UI Themes**: Customize dashboard colors and layout

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_system.py
```

This will:
1. Create sample job posting
2. Upload test resume
3. Run evaluation process
4. Test bulk processing
5. Verify all API endpoints

## 📦 Deployment

### Production Setup
1. **Database**: Migrate to PostgreSQL for production scale
2. **Authentication**: Add user management and access control
3. **Caching**: Implement Redis for improved performance
4. **Monitoring**: Add logging and health checks
5. **Scaling**: Use Docker containers and load balancers

### Docker Deployment (Future)
```dockerfile
# Example Dockerfile structure
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ ./app/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

## 🔒 Security Considerations

- **File Upload**: Validate file types and scan for malware
- **API Access**: Implement rate limiting and authentication
- **Data Privacy**: Ensure GDPR compliance for candidate data
- **Environment**: Secure API keys and database credentials

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/enhancement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/enhancement`)
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the [API documentation](http://localhost:8000/docs)
2. Run the test suite for debugging
3. Review logs for error details
4. Open GitHub issue with detailed description

## 🚧 Roadmap

### Phase 1 (Current)
- ✅ Core evaluation engine
- ✅ AI-powered parsing
- ✅ Streamlit dashboard
- ✅ Bulk processing

### Phase 2 (Planned)
- 🔄 Advanced analytics dashboard
- 🔄 Email notifications
- 🔄 Interview scheduling integration
- 🔄 Candidate self-service portal

### Phase 3 (Future)
- ⏳ Mobile application
- ⏳ Advanced AI models
- ⏳ Multi-language support
- ⏳ Integration with job boards

---

**Built with ❤️ for Innomatics Research Labs**

*Transforming resume evaluation from manual guesswork to data-driven insights*