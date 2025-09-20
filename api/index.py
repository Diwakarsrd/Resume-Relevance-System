from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.main import app as main_app

# Create FastAPI app for Vercel
app = FastAPI(
    title="Resume Relevance API",
    description="Complete resume evaluation system API",
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

# Mount the main app
app.mount("/api", main_app)

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Resume Relevance Check System",
        "version": "1.0.0",
        "status": "running",
        "api_docs": "/docs",
        "main_api": "/api"
    }

# Vercel handler
handler = Mangum(app)