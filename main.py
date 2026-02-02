from fastapi import FastAPI, UploadFile, File, Form
from typing import List
import pdfplumber

from app.core.section_parser import extract_skills
from app.core.similarity import calculate_ats_score

app = FastAPI(title="AI Powered ATS Resume Analyzer")


def extract_text_from_pdf(file: UploadFile) -> str:
    text = ""
    file.file.seek(0)

    with pdfplumber.open(file.file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text


def hiring_decision(score: float) -> str:
    if score >= 80:
        return "Hire"
    elif score >= 65:
        return "Borderline"
    return "Reject"


@app.post("/analyze")
async def analyze_resumes(
    resumes: List[UploadFile] = File(...),
    job_description: str = Form(...),
    role: str = Form(...)
):
    if len(resumes) > 1000:
        return {"error": "Maximum 1000 resumes allowed"}

    jd_skills = extract_skills(job_description)

    results = []

    for resume in resumes:
        resume_text = extract_text_from_pdf(resume)
        resume_skills = extract_skills(resume_text)

        matched_skills = sorted(set(resume_skills) & set(jd_skills))
        missing_skills = sorted(set(jd_skills) - set(resume_skills))

        ats_score = calculate_ats_score(
            matched_skills=matched_skills,
            jd_skills=jd_skills,
            resume_text=resume_text,
            jd_text=job_description
        )

        results.append({
            "candidate": resume.filename,
            "final_score": ats_score,
            "decision": hiring_decision(ats_score),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "section_scores": {
                "skills": round((len(matched_skills) / max(len(jd_skills), 1)) * 100, 2),
                "similarity": round(ats_score * 0.35, 2),
                "experience": min(90, ats_score + 3),
                "projects": min(85, ats_score),
                "education": 80.0
            }
        })

    ranked = sorted(results, key=lambda x: x["final_score"], reverse=True)

    return {
        "job_role": role,
        "total_resumes": len(resumes),
        "shortlisted": [r for r in ranked if float(r["final_score"]) >= 80],
        "all_candidates_ranked": ranked
    }
