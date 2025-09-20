from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, List
from datetime import datetime
from sqlalchemy import JSON as SA_JSON

class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    jd_text: str
    must_have: List[str] = Field(default_factory=list, sa_column=Column(SA_JSON))
    nice_to_have: List[str] = Field(default_factory=list, sa_column=Column(SA_JSON))
    min_experience: Optional[int] = None
    location: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Candidate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = None
    email: Optional[str] = None
    university: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Resume(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    candidate_id: Optional[int] = None
    file_path: str
    parsed_text: Optional[str] = None
    parsed_json: Optional[dict] = Field(default=None, sa_column=Column(SA_JSON))
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class Evaluation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    resume_id: int
    job_id: int
    final_score: int
    hard_score: int
    semantic_score: int
    verdict: str
    missing_skills: List[str] = Field(default_factory=list, sa_column=Column(SA_JSON))
    missing_certifications: List[str] = Field(default_factory=list, sa_column=Column(SA_JSON))
    matching_skills: List[str] = Field(default_factory=list, sa_column=Column(SA_JSON))
    feedback: Optional[str] = None
    eval_time: datetime = Field(default_factory=datetime.utcnow)
