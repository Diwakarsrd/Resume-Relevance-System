from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import os
import json
from typing import List, Optional
import re

# Simple in-memory storage for demo purposes
jobs_db = []
resumes_db = []
evaluations_db = []
candidates_db = []

app = FastAPI(title="Resume Relevance System - Simple", description="Simplified API for Streamlit Cloud")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/")
def root():
    return {
        "message": "Resume Relevance System - Simple API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/api/jobs")
def create_job(title: str = Form(...), jd_text: str = Form(...), must_have: str = Form(""), nice_to_have: str = Form("")):
    """Create a new job posting"""
    job_id = len(jobs_db) + 1
    
    # Simple skill parsing
    must_have_skills = [s.strip().lower() for s in must_have.split(",") if s.strip()]
    nice_to_have_skills = [s.strip().lower() for s in nice_to_have.split(",") if s.strip()]
    
    job = {
        "id": job_id,
        "title": title,
        "jd_text": jd_text,
        "must_have": must_have_skills,
        "nice_to_have": nice_to_have_skills,
        "location": None
    }
    
    jobs_db.append(job)
    
    return {
        "job_id": job_id,
        "parsed_info": {
            "must_have_skills": must_have_skills,
            "nice_to_have_skills": nice_to_have_skills
        },
        "message": "Job created successfully"
    }

@app.get("/api/jobs")
def get_jobs(limit: int = 50):
    """Get all jobs"""
    return jobs_db[:limit]

@app.post("/api/resumes")
def upload_resume(name: str = Form(...), email: str = Form(...), file: UploadFile = File(...)):
    """Upload a resume"""
    try:
        candidate_id = len(candidates_db) + 1
        resume_id = len(resumes_db) + 1
        
        # Save uploaded file
        file_path = UPLOAD_DIR / f"{resume_id}_{file.filename}"
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Simple text extraction
        text = ""
        if file.filename.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        else:
            text = f"File uploaded: {file.filename}"
        
        # Simple skill extraction
        skills = extract_simple_skills(text)
        
        candidate = {
            "id": candidate_id,
            "name": name,
            "email": email
        }
        candidates_db.append(candidate)
        
        resume = {
            "id": resume_id,
            "candidate_id": candidate_id,
            "candidate_name": name,
            "candidate_email": email,
            "file_path": str(file_path),
            "parsed_text": text,
            "upload_time": "2024-01-01T00:00:00"
        }
        resumes_db.append(resume)
        
        return {
            "resume_id": resume_id,
            "candidate_id": candidate_id,
            "parsed_info": {
                "skills_found": len(skills),
                "experience_entries": 1,
                "education_entries": 1,
                "projects_found": 0,
                "certifications_found": 0
            },
            "message": "Resume uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/resumes")
def get_resumes(limit: int = 50):
    """Get all resumes"""
    return resumes_db[:limit]

@app.post("/api/evaluate")
def evaluate_resume(job_id: int = Form(...), resume_id: int = Form(...)):
    """Evaluate a resume against a job"""
    # Find job and resume
    job = next((j for j in jobs_db if j["id"] == job_id), None)
    resume = next((r for r in resumes_db if r["id"] == resume_id), None)
    
    if not job or not resume:
        raise HTTPException(status_code=404, detail="Job or resume not found")
    
    # Simple evaluation
    resume_skills = extract_simple_skills(resume["parsed_text"])
    job_skills = job["must_have"] + job["nice_to_have"]
    
    matched_skills = list(set(resume_skills) & set(job_skills))
    missing_skills = list(set(job_skills) - set(resume_skills))
    
    # Calculate score
    if job_skills:
        score = int((len(matched_skills) / len(job_skills)) * 100)
    else:
        score = 80
    
    # Determine verdict
    if score >= 80:
        verdict = "High"
    elif score >= 60:
        verdict = "Medium"
    else:
        verdict = "Low"
    
    # Generate feedback
    feedback = f"Score: {score}%. Matched {len(matched_skills)} out of {len(job_skills)} required skills."
    
    evaluation = {
        "id": len(evaluations_db) + 1,
        "job_id": job_id,
        "resume_id": resume_id,
        "job_title": job["title"],
        "candidate_name": resume["candidate_name"],
        "final_score": score,
        "verdict": verdict,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "feedback": feedback,
        "eval_time": "2024-01-01T00:00:00"
    }
    
    evaluations_db.append(evaluation)
    
    return evaluation

@app.get("/api/evaluations")
def get_evaluations(limit: int = 100, job_id: Optional[int] = None):
    """Get evaluations"""
    evals = evaluations_db
    if job_id:
        evals = [e for e in evals if e["job_id"] == job_id]
    return evals[:limit]

@app.post("/api/bulk-evaluate")
def bulk_evaluate(job_id: int = Form(...)):
    """Bulk evaluate all resumes against a job"""
    job = next((j for j in jobs_db if j["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    processed = 0
    for resume in resumes_db:
        # Check if already evaluated
        existing = next((e for e in evaluations_db if e["job_id"] == job_id and e["resume_id"] == resume["id"]), None)
        if not existing:
            # Evaluate
            evaluate_resume(job_id, resume["id"])
            processed += 1
    
    return {"processed_count": processed, "message": "Bulk evaluation completed"}

def extract_simple_skills(text: str) -> List[str]:
    """Extract skills using simple keyword matching"""
    common_skills = [
        'python', 'javascript', 'java', 'react', 'node.js', 'sql', 'mongodb',
        'postgresql', 'docker', 'kubernetes', 'aws', 'azure', 'machine learning',
        'data science', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'flask',
        'django', 'fastapi', 'html', 'css', 'angular', 'vue', 'typescript',
        'git', 'linux', 'excel', 'powerbi', 'tableau'
    ]
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in common_skills:
        if skill in text_lower:
            found_skills.append(skill)
    
    return found_skills

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)