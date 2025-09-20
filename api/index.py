from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import re
from typing import List

# Lightweight FastAPI app for Vercel
app = FastAPI(
    title="Resume Relevance API - Vercel",
    description="Lightweight serverless API for resume evaluation",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Resume Relevance API - Serverless",
        "version": "1.0.0",
        "status": "running",
        "platform": "Vercel",
        "docs": "/docs",
        "note": "Lightweight version optimized for serverless deployment"
    }

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy", "platform": "vercel"}

@app.post("/evaluate")
def evaluate_resume(
    job_title: str = Form(...),
    job_description: str = Form(...),
    resume_text: str = Form(...),
    required_skills: str = Form("")
):
    """Lightweight resume evaluation endpoint"""
    try:
        # Parse required skills
        skills_list = [s.strip().lower() for s in required_skills.split(",") if s.strip()] if required_skills else []
        
        # Extract skills from resume text
        resume_skills = extract_skills_from_text(resume_text)
        
        # Calculate score
        score = calculate_match_score(skills_list, resume_skills)
        verdict = get_verdict(score)
        
        # Find matches and gaps
        matched_skills = list(set(skills_list) & set(resume_skills))
        missing_skills = list(set(skills_list) - set(resume_skills))
        
        # Generate feedback
        feedback = generate_feedback(score, verdict, matched_skills, missing_skills)
        
        return {
            "job_title": job_title,
            "final_score": score,
            "verdict": verdict,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "feedback": feedback,
            "evaluation_summary": {
                "total_required_skills": len(skills_list),
                "matched_skills_count": len(matched_skills),
                "missing_skills_count": len(missing_skills),
                "match_percentage": round(len(matched_skills) / len(skills_list) * 100, 1) if skills_list else 100
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@app.post("/skills-extraction")
def extract_skills_only(resume_text: str = Form(...)):
    """Extract skills from resume text"""
    try:
        skills = extract_skills_from_text(resume_text)
        return {
            "skills_found": skills,
            "skills_count": len(skills),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill extraction failed: {str(e)}")

def extract_skills_from_text(text: str) -> List[str]:
    """Extract skills from text using keyword matching"""
    # Common technical skills database
    skill_keywords = [
        'python', 'javascript', 'java', 'react', 'node.js', 'nodejs', 'sql', 'mongodb', 
        'postgresql', 'mysql', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 
        'machine learning', 'ml', 'data science', 'tensorflow', 'pytorch', 
        'pandas', 'numpy', 'scikit-learn', 'sklearn', 'flask', 'django', 'fastapi',
        'html', 'css', 'angular', 'vue', 'typescript', 'git', 'github', 'linux',
        'windows', 'excel', 'powerbi', 'tableau', 'spark', 'hadoop', 'kafka',
        'redis', 'elasticsearch', 'api', 'rest', 'graphql', 'microservices',
        'devops', 'ci/cd', 'jenkins', 'terraform', 'ansible', 'spring', 'boot'
    ]
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in skill_keywords:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(skill.replace(' ', r'\s+')) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    
    return found_skills

def calculate_match_score(required_skills: List[str], candidate_skills: List[str]) -> int:
    """Calculate match score between required and candidate skills"""
    if not required_skills:
        return 85  # Default score when no specific requirements
    
    # Direct matches
    direct_matches = len(set(required_skills) & set(candidate_skills))
    
    # Fuzzy matching for similar skills
    fuzzy_matches = 0
    for req_skill in required_skills:
        if req_skill not in candidate_skills:
            for cand_skill in candidate_skills:
                if are_skills_similar(req_skill, cand_skill):
                    fuzzy_matches += 0.5  # Half credit for fuzzy matches
                    break
    
    total_matches = direct_matches + fuzzy_matches
    score = min(int((total_matches / len(required_skills)) * 100), 100)
    
    return max(score, 0)

def are_skills_similar(skill1: str, skill2: str) -> bool:
    """Check if two skills are similar"""
    # Simple similarity mapping
    synonyms = {
        'javascript': ['js', 'node.js', 'nodejs'],
        'python': ['py'],
        'machine learning': ['ml', 'ai', 'artificial intelligence'],
        'postgresql': ['postgres'],
        'mongodb': ['mongo'],
        'kubernetes': ['k8s'],
        'docker': ['containerization'],
        'aws': ['amazon web services'],
        'gcp': ['google cloud'],
        'azure': ['microsoft azure']
    }
    
    for main_skill, variations in synonyms.items():
        if (skill1 == main_skill and skill2 in variations) or \
           (skill2 == main_skill and skill1 in variations):
            return True
    
    return False

def get_verdict(score: int) -> str:
    """Get verdict based on score"""
    if score >= 80:
        return "High"
    elif score >= 60:
        return "Medium"
    else:
        return "Low"

def generate_feedback(score: int, verdict: str, matched_skills: List[str], missing_skills: List[str]) -> str:
    """Generate feedback based on evaluation results"""
    feedback_parts = []
    
    # Overall assessment
    if verdict == "High":
        feedback_parts.append(f"🎉 Excellent match! Your profile scores {score}/100 with {verdict} suitability.")
    elif verdict == "Medium":
        feedback_parts.append(f"✅ Good match! Your profile scores {score}/100 with {verdict} suitability.")
    else:
        feedback_parts.append(f"📈 Areas for improvement. Your profile scores {score}/100 with {verdict} suitability.")
    
    # Matched skills
    if matched_skills:
        feedback_parts.append(f"\n🟢 Strong Skills Match: {', '.join(matched_skills[:5])}")
    
    # Missing skills
    if missing_skills:
        feedback_parts.append(f"\n🔴 Skills to Develop: {', '.join(missing_skills[:5])}")
        feedback_parts.append("Consider focusing on these skills to improve your match.")
    
    # Recommendations
    if score < 70:
        feedback_parts.append("\n💡 Recommendations:")
        feedback_parts.append("- Build projects showcasing the missing skills")
        feedback_parts.append("- Consider relevant certifications")
        feedback_parts.append("- Update your resume to highlight relevant experience")
    
    return " ".join(feedback_parts)

# Vercel handler
handler = Mangum(app)