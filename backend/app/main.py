import os
import tempfile
from typing import List, Optional
from app.scoring.score_engine import calculate_scores
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from app.utils.pdf_parser import extract_text_from_pdf
from app.nlp.decision_engine import analyze_resume


# ==================================================
# FASTAPI APP
# ==================================================

app = FastAPI(
    title="AI Resume Intelligence & Job Matcher",
    description=(
        "Analyze a resume against a job description using "
        "NLP, skill matching, semantic evidence, experience "
        "analysis, and education analysis."
    ),
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# ROOT
# ==================================================

@app.get("/")
def root():
    return {
        "message": "AI Resume Intelligence & Job Matcher API",
        "status": "running"
    }


# ==================================================
# RESPONSE MODELS
# ==================================================


# --------------------------------------------------
# Skill Analysis
# --------------------------------------------------

class SkillAnalysis(BaseModel):
    matched: List[str]
    missing: List[str]


# --------------------------------------------------
# Skill Requirement Group
# --------------------------------------------------

class SkillRequirementGroup(BaseModel):
    group_id: str
    operator: str
    skills: List[str]
    importance: str
    requirement_text: str
    matched: List[str]
    missing: List[str]
    satisfied: bool


# --------------------------------------------------
# Experience Date Range
# --------------------------------------------------

class ExperienceDateRange(BaseModel):
    start: Optional[str] = None
    end: Optional[str] = None
    years: Optional[float] = None


# --------------------------------------------------
# Experience Analysis
# --------------------------------------------------

class ExperienceAnalysis(BaseModel):
    candidate_years: float
    explicit_years: float
    calculated_years: float
    source: str
    date_ranges: List[ExperienceDateRange]
    required_years: float
    satisfied: bool


# --------------------------------------------------
# Education Dates
# --------------------------------------------------

class EducationDates(BaseModel):
    start: Optional[str] = None
    end: Optional[str] = None


# --------------------------------------------------
# Education Requirement Group
# --------------------------------------------------

class EducationRequirementGroup(BaseModel):
    group_id: str
    operator: str
    fields: List[str]
    requirement_text: str
    matched: List[str]
    satisfied: bool


# --------------------------------------------------
# Education Analysis
# --------------------------------------------------

class EducationAnalysis(BaseModel):
    candidate_levels: List[str]
    candidate_fields: List[str]

    institution: Optional[str] = None

    dates: EducationDates

    required_levels: List[str]
    required_fields: List[str]

    required_education_groups: List[
        EducationRequirementGroup
    ]

    satisfied: bool


# --------------------------------------------------
# Requirement Evidence
# --------------------------------------------------

class RequirementEvidence(BaseModel):
    skill: str

    importance: str

    requirement_context: str

    exact_match: bool

    evidence_status: str

    semantic_query: Optional[str] = None

    semantic_score: float

    evidence_strength: str

    evidence: Optional[str] = None

    # OR / AND group information
    group_id: Optional[str] = None

    group_operator: Optional[str] = None

    group_skills: List[str] = Field(
        default_factory=list
    )


# --------------------------------------------------
# Complete Resume Analysis Response
# --------------------------------------------------

class ResumeAnalysisResponse(BaseModel):

    # Resume information
    sections_detected: List[str]

    resume_skills: List[str]

    # Skill analysis
    required_skills: SkillAnalysis

    preferred_skills: SkillAnalysis

    # Requirement groups
    required_skill_groups: List[
        SkillRequirementGroup
    ]

    preferred_skill_groups: List[
        SkillRequirementGroup
    ]

    # Coverage
    required_skill_coverage: float

    # Evidence
    requirement_evidence: List[
        RequirementEvidence
    ]

    # Experience
    experience: ExperienceAnalysis

    # Education
    education: EducationAnalysis

    # Final decision
    eligibility: bool

   
    # Scores
    skill_score: float
    experience_score: float
    education_score: float
    semantic_score: float
    overall_match_score: float


# ==================================================
# ANALYZE ENDPOINT
# ==================================================

@app.post(
    "/analyze",
    response_model=ResumeAnalysisResponse
)
async def analyze(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...)
):

    # ==================================================
    # 1. VALIDATE FILE
    # ==================================================

    if resume_file.content_type != "application/pdf":

        raise HTTPException(
            status_code=400,
            detail="Resume must be a PDF file."
        )

    # ==================================================
    # 2. VALIDATE JOB DESCRIPTION
    # ==================================================

    if not job_description.strip():

        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty."
        )

    # ==================================================
    # 3. READ FILE
    # ==================================================

    file_content = await resume_file.read()

    if not file_content:

        raise HTTPException(
            status_code=400,
            detail="Uploaded resume file is empty."
        )

    # ==================================================
    # 4. CREATE TEMPORARY PDF
    # ==================================================

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            temp_file.write(file_content)

            temp_path = temp_file.name

        # ==================================================
        # 5. EXTRACT RESUME TEXT
        # ==================================================

        resume_text = extract_text_from_pdf(
            temp_path
        )

        if not resume_text.strip():

            raise HTTPException(
                status_code=400,
                detail=(
                    "Could not extract text from the "
                    "uploaded PDF."
                )
            )

        # ==================================================
        # 6. RUN NLP DECISION ENGINE
        # ==================================================

        result = analyze_resume(
            resume_text,
            job_description
        )

        scores = calculate_scores(
            result
        )

        result.update(scores)

        # ==================================================
        # 7. RETURN RESULT
        # ==================================================

        return result

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

    finally:

        # ==================================================
        # 8. CLEAN TEMPORARY FILE
        # ==================================================

        if temp_path and os.path.exists(temp_path):

            os.remove(temp_path)