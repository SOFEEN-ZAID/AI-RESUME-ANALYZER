from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from resume_analyzer import analyze_match, extract_text_from_file


app = FastAPI(title="AI Resume and Job Match Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeTextRequest(BaseModel):
    resume_text: str
    job_description: str


@app.get("/")
def health_check():
    return {"status": "ok", "message": "AI Resume Analyzer API is running"}


@app.post("/analyze-text")
def analyze_text(payload: AnalyzeTextRequest):
    return analyze_match(payload.resume_text, payload.job_description)


@app.post("/analyze-file")
async def analyze_file(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
):
    resume_text = await extract_text_from_file(resume)
    return analyze_match(resume_text, job_description)
