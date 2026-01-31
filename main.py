"""
FastAPI Main Application
Provides REST API endpoints for CV-LinkedIn comparison.
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import logging

from backend.cv_parser import parse_cv_from_bytes
from backend.comparator import CVLinkedInComparator, parse_linkedin_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CV-LinkedIn Comparator API",
    description="Compare CV documents with LinkedIn profiles",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize comparator (loaded once at startup)
comparator: Optional[CVLinkedInComparator] = None


@app.on_event("startup")
async def startup_event():
    """Load the model on startup."""
    global comparator
    logger.info("Loading sentence transformer model...")
    comparator = CVLinkedInComparator()
    logger.info("Model loaded successfully!")


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "message": "CV-LinkedIn Comparator API",
        "status": "online",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": comparator is not None
    }


class CompareResponse(BaseModel):
    """Response model for comparison endpoint."""
    success: bool
    overall_score: float
    section_scores: dict
    discrepancies: list
    skills_comparison: dict
    recommendations: list
    weights: dict


@app.post("/compare", response_model=CompareResponse)
async def compare_cv_linkedin(
    cv_file: UploadFile = File(..., description="CV file (PDF or DOCX)"),
    linkedin_text: str = Form(..., description="LinkedIn profile text")
):
    """
    Compare CV with LinkedIn profile.
    
    Args:
        cv_file: Uploaded CV file (PDF or DOCX)
        linkedin_text: LinkedIn profile text
        
    Returns:
        Comparison results with scores and recommendations
    """
    try:
        # Validate file type
        if not cv_file.filename.lower().endswith(('.pdf', '.docx')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Please upload PDF or DOCX file."
            )
        
        # Validate LinkedIn text
        if not linkedin_text or len(linkedin_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="LinkedIn profile text is too short or empty."
            )
        
        logger.info(f"Processing CV file: {cv_file.filename}")
        
        # Read CV file
        cv_bytes = await cv_file.read()
        
        # Parse CV
        logger.info("Parsing CV...")
        cv_data = parse_cv_from_bytes(cv_bytes, cv_file.filename)
        
        # Parse LinkedIn text
        logger.info("Parsing LinkedIn profile...")
        linkedin_data = parse_linkedin_text(linkedin_text)
        
        # Compare
        logger.info("Comparing CV and LinkedIn profile...")
        comparison_result = comparator.calculate_score(cv_data, linkedin_data)
        
        # Generate recommendations
        recommendations = comparator.get_recommendations(comparison_result)
        
        logger.info(f"Comparison complete. Overall score: {comparison_result['overall_score']}%")
        
        return CompareResponse(
            success=True,
            overall_score=comparison_result['overall_score'],
            section_scores=comparison_result['section_scores'],
            discrepancies=comparison_result['discrepancies'],
            skills_comparison=comparison_result['skills_comparison'],
            recommendations=recommendations,
            weights=comparison_result['weights']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during comparison: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing comparison: {str(e)}"
        )


@app.post("/parse-cv")
async def parse_cv_only(
    cv_file: UploadFile = File(..., description="CV file (PDF or DOCX)")
):
    """
    Parse CV file only (for testing).
    
    Args:
        cv_file: Uploaded CV file
        
    Returns:
        Parsed CV data
    """
    try:
        # Validate file type
        if not cv_file.filename.lower().endswith(('.pdf', '.docx')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Please upload PDF or DOCX file."
            )
        
        # Read and parse CV
        cv_bytes = await cv_file.read()
        cv_data = parse_cv_from_bytes(cv_bytes, cv_file.filename)
        
        return {
            "success": True,
            "filename": cv_file.filename,
            "sections": {
                "experience": cv_data['experience'][:200] + "..." if len(cv_data['experience']) > 200 else cv_data['experience'],
                "skills": cv_data['skills'][:200] + "..." if len(cv_data['skills']) > 200 else cv_data['skills'],
                "education": cv_data['education'][:200] + "..." if len(cv_data['education']) > 200 else cv_data['education'],
            },
            "extracted_skills": cv_data['extracted_skills']
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error parsing CV: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing CV: {str(e)}"
        )


@app.post("/parse-linkedin")
async def parse_linkedin_only(
    linkedin_text: str = Form(..., description="LinkedIn profile text")
):
    """
    Parse LinkedIn text only (for testing).
    
    Args:
        linkedin_text: LinkedIn profile text
        
    Returns:
        Parsed LinkedIn data
    """
    try:
        if not linkedin_text or len(linkedin_text.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="LinkedIn profile text is too short or empty."
            )
        
        linkedin_data = parse_linkedin_text(linkedin_text)
        
        return {
            "success": True,
            "sections": {
                "experience": linkedin_data['experience'][:200] + "..." if len(linkedin_data['experience']) > 200 else linkedin_data['experience'],
                "skills": linkedin_data['skills'][:200] + "..." if len(linkedin_data['skills']) > 200 else linkedin_data['skills'],
                "education": linkedin_data['education'][:200] + "..." if len(linkedin_data['education']) > 200 else linkedin_data['education'],
            },
            "extracted_skills": linkedin_data['extracted_skills']
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error parsing LinkedIn: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing LinkedIn: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
