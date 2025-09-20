from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, create_engine, select
from pathlib import Path
import shutil
import os
from typing import List, Optional
import json

# ... existing code ...

from app.models import SQLModel, Job, Candidate, Resume, Evaluation
from app.parsers import (
    extract_text_pdf, extract_text_docx, normalize_text, 
    parse_resume_structured, parse_job_description
)
from app.scoring import (
    comprehensive_scoring, generate_comprehensive_feedback, 
    verdict_from_score, semantic_score, compute_final_score
)

BASE = Path(__file__).resolve().parent
UPLOAD_DIR = BASE / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Use in-memory database for Vercel or fallback to file-based
if os.getenv('VERCEL'):
    DATABASE_URL = "sqlite:///:memory:"
else:
    DATABASE_URL = f"sqlite:///{BASE / 'data.db'}"
    
engine = create_engine(DATABASE_URL, echo=False)
SQLModel.metadata.create_all(engine)

app = FastAPI(title="Resume Relevance Check System", description="AI-powered resume evaluation platform")

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    """Serve the main dashboard interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_redirect(request: Request):
    """Dashboard redirect"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api")
def api_root():
    """Root endpoint with system information"""
    return {
        "message": "Resume Relevance Check System API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "jobs": "/api/jobs",
            "resumes": "/api/resumes", 
            "evaluate": "/api/evaluate",
            "bulk_evaluate": "/api/bulk-evaluate"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "resume-relevance-api"}

@app.post("/api/jobs")
def add_job(title: str = Form(...), jd_text: str = Form(...), must_have: str = Form(""), nice_to_have: str = Form("")):
    """Create a new job posting with enhanced parsing"""
    # Parse job description for structured information
    jd_parsed = parse_job_description(jd_text)
    
    # Override with manual inputs if provided
    if must_have.strip():
        jd_parsed['must_have_skills'] = [x.strip() for x in must_have.split(",") if x.strip()]
    if nice_to_have.strip():
        jd_parsed['nice_to_have_skills'] = [x.strip() for x in nice_to_have.split(",") if x.strip()]
    
    job = Job(
        title=jd_parsed.get('title', title),
        jd_text=jd_text,
        must_have=jd_parsed['must_have_skills'],
        nice_to_have=jd_parsed['nice_to_have_skills'],
        location=jd_parsed.get('location'),
        min_experience=1 if 'year' in str(jd_parsed.get('required_experience', '')).lower() else None
    )
    
    with Session(engine) as session:
        session.add(job)
        session.commit()
        session.refresh(job)
    
    return {
        "job_id": job.id,
        "parsed_info": jd_parsed,
        "message": "Job created successfully with AI-enhanced parsing"
    }

@app.post("/api/resumes")
def upload_resume(name: str = Form(...), email: str = Form(...), file: UploadFile = File(...)):
    """Upload and parse resume with enhanced extraction"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
            
        suffix = Path(file.filename).suffix.lower()
        if suffix not in [".pdf", ".docx", ".txt"]:
            raise HTTPException(status_code=400, detail="Only PDF/DOCX/TXT allowed")
            
        dest = UPLOAD_DIR / f"{int(os.times()[4]*1000)}_{file.filename}"
        with open(dest, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Extract and parse resume text
        if suffix == ".pdf":
            text = extract_text_pdf(str(dest))
        elif suffix == ".docx":
            text = extract_text_docx(str(dest))
        else:  # .txt file
            try:
                with open(dest, 'r', encoding='utf-8') as f:
                    text = f.read()
            except UnicodeDecodeError:
                # Try with different encodings
                for encoding in ['utf-8-sig', 'latin-1', 'cp1252']:
                    try:
                        with open(dest, 'r', encoding=encoding) as f:
                            text = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    text = "Could not decode file"
        
        text = normalize_text(text)
        
        # Parse resume into structured format
        parsed_data = parse_resume_structured(text)
        
        with Session(engine) as session:
            cand = Candidate(name=name, email=email)
            session.add(cand)
            session.commit()
            session.refresh(cand)
            
            resume = Resume(
                candidate_id=cand.id,
                file_path=str(dest),
                parsed_text=text,
                parsed_json=parsed_data
            )
            session.add(resume)
            session.commit()
            session.refresh(resume)
            
            return {
                "resume_id": resume.id,
                "candidate_id": cand.id,
                "parsed_info": {
                    "skills_found": len(parsed_data['skills']),
                    "education_entries": len(parsed_data['education']),
                    "experience_entries": len(parsed_data['experience']),
                    "projects_found": len(parsed_data['projects']),
                    "certifications_found": len(parsed_data['certifications'])
                },
                "message": "Resume uploaded and parsed successfully"
            }
    except Exception as e:
        print(f"Error in upload_resume: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/api/evaluate")
def evaluate(resume_id: int = Form(...), job_id: int = Form(...)):
    """Evaluate resume against job with comprehensive scoring"""
    with Session(engine) as session:
        resume = session.get(Resume, resume_id)
        job = session.get(Job, job_id)
        
        if not resume or not job:
            raise HTTPException(status_code=404, detail="Resume or job not found")
        
        # Get parsed resume data or parse if not available
        if resume.parsed_json:
            resume_data = resume.parsed_json
        else:
            # Parse resume if not already parsed
            text = resume.parsed_text
            if not text:
                path = resume.file_path
                text = extract_text_pdf(path) if path.endswith(".pdf") else extract_text_docx(path)
                text = normalize_text(text)
            resume_data = parse_resume_structured(text)
            
            # Update resume with parsed data
            resume.parsed_text = text
            resume.parsed_json = resume_data
            session.add(resume)
            session.commit()
        
        # Parse job description if needed
        job_data = {
            'must_have_skills': job.must_have or [],
            'nice_to_have_skills': job.nice_to_have or [],
            'required_education': [],
            'required_experience': ''
        }
        
        # Use comprehensive scoring
        scoring_results = comprehensive_scoring(resume_data, job_data)
        
        # Generate comprehensive feedback
        feedback = generate_comprehensive_feedback(scoring_results, resume_data, job_data)
        
        # Create evaluation record
        ev = Evaluation(
            resume_id=resume_id,
            job_id=job_id,
            final_score=scoring_results['final_score'],
            hard_score=scoring_results['must_have_score'],
            semantic_score=semantic_score(job.jd_text, resume_data.get('raw_text', '')),
            verdict=scoring_results['verdict'],
            missing_skills=scoring_results['missing_must_have'],
            matching_skills=scoring_results['matched_must_have'],
            feedback=feedback
        )
        
        session.add(ev)
        session.commit()
        session.refresh(ev)
    
    return {
        "evaluation_id": ev.id,
        "final_score": scoring_results['final_score'],
        "verdict": scoring_results['verdict'],
        "detailed_scores": {
            "must_have_skills": scoring_results['must_have_score'],
            "nice_to_have_skills": scoring_results['nice_to_have_score'],
            "education": scoring_results['education_score'],
            "experience": scoring_results['experience_score'],
            "projects": scoring_results['project_score']
        },
        "feedback": feedback,
        "missing_skills": scoring_results['missing_must_have'],
        "matched_skills": scoring_results['matched_must_have']
    }

@app.get("/api/jobs")
def list_jobs(skip: int = Query(0), limit: int = Query(10)):
    """List all jobs with pagination"""
    with Session(engine) as session:
        jobs = session.exec(select(Job).offset(skip).limit(limit)).all()
        return [{"id": job.id, "title": job.title, "location": job.location, "must_have": job.must_have} for job in jobs]

@app.get("/api/resumes")
def list_resumes(skip: int = Query(0), limit: int = Query(10)):
    """List all resumes with pagination"""
    with Session(engine) as session:
        resumes = session.exec(select(Resume).offset(skip).limit(limit)).all()
        candidates = {}
        for resume in resumes:
            if resume.candidate_id and resume.candidate_id not in candidates:
                candidate = session.get(Candidate, resume.candidate_id)
                candidates[resume.candidate_id] = candidate
        
        return [{
            "id": resume.id,
            "candidate_name": candidates.get(resume.candidate_id).name if resume.candidate_id and candidates.get(resume.candidate_id) else "Unknown",
            "candidate_email": candidates.get(resume.candidate_id).email if resume.candidate_id and candidates.get(resume.candidate_id) else "Unknown",
            "uploaded_at": resume.uploaded_at
        } for resume in resumes]

@app.get("/api/evaluations")
def list_evaluations(job_id: Optional[int] = Query(None), verdict: Optional[str] = Query(None), skip: int = Query(0), limit: int = Query(20)):
    """List evaluations with filtering options"""
    with Session(engine) as session:
        query = select(Evaluation)
        
        if job_id:
            query = query.where(Evaluation.job_id == job_id)
        if verdict:
            query = query.where(Evaluation.verdict == verdict)
            
        evaluations = session.exec(query.offset(skip).limit(limit)).all()
        
        # Get related data
        result = []
        for ev in evaluations:
            resume = session.get(Resume, ev.resume_id)
            job = session.get(Job, ev.job_id)
            candidate = session.get(Candidate, resume.candidate_id) if resume and resume.candidate_id else None
            
            result.append({
                "id": ev.id,
                "final_score": ev.final_score,
                "verdict": ev.verdict,
                "candidate_name": candidate.name if candidate else "Unknown",
                "job_title": job.title if job else "Unknown",
                "eval_time": ev.eval_time,
                "missing_skills": ev.missing_skills
            })
            
        return result

@app.post("/api/bulk-evaluate")
def bulk_evaluate(job_id: int = Form(...)):
    """Evaluate all resumes against a specific job"""
    with Session(engine) as session:
        job = session.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get all resumes that haven't been evaluated for this job
        evaluated_resume_ids = session.exec(
            select(Evaluation.resume_id).where(Evaluation.job_id == job_id)
        ).all()
        
        resumes = session.exec(
            select(Resume).where(~Resume.id.in_(evaluated_resume_ids) if evaluated_resume_ids else True)
        ).all()
        
        results = []
        for resume in resumes[:50]:  # Limit to 50 resumes per batch
            try:
                # Evaluate each resume
                eval_result = evaluate(resume_id=resume.id, job_id=job_id)
                results.append({
                    "resume_id": resume.id,
                    "evaluation_id": eval_result["evaluation_id"],
                    "score": eval_result["final_score"],
                    "verdict": eval_result["verdict"]
                })
            except Exception as e:
                results.append({
                    "resume_id": resume.id,
                    "error": str(e)
                })
        
        return {
            "job_id": job_id,
            "processed_count": len(results),
            "results": results
        }
