import io
import math
import re
from collections import Counter

from fastapi import HTTPException, UploadFile

try:
    import docx
except ImportError:
    docx = None

try:
    import fitz
except ImportError:
    fitz = None


SKILL_CATEGORIES = {
    "Programming": {
        "python",
        "java",
        "c++",
        "javascript",
        "typescript",
        "sql",
        "r",
    },
    "AI/ML": {
        "machine learning",
        "deep learning",
        "nlp",
        "computer vision",
        "generative ai",
        "llm",
        "rag",
        "transformers",
        "bert",
        "model evaluation",
        "feature engineering",
        "data analysis",
        "data visualization",
        "statistics",
    },
    "Frameworks": {
        "tensorflow",
        "pytorch",
        "scikit-learn",
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "langchain",
        "fastapi",
        "flask",
        "django",
        "react",
        "next.js",
        "node.js",
    },
    "Data & Cloud": {
        "postgresql",
        "mongodb",
        "mysql",
        "faiss",
        "chromadb",
        "vector database",
        "aws",
        "azure",
        "gcp",
        "docker",
        "kubernetes",
        "mlops",
        "git",
        "github",
        "api",
        "model deployment",
        "ci/cd",
    },
}

SKILL_KEYWORDS = set().union(*SKILL_CATEGORIES.values())

ROLE_PROFILES = {
    "Machine Learning Engineer": {
        "python",
        "machine learning",
        "deep learning",
        "pytorch",
        "tensorflow",
        "scikit-learn",
        "model deployment",
        "docker",
        "api",
        "mlops",
    },
    "Data Scientist": {
        "python",
        "sql",
        "statistics",
        "pandas",
        "numpy",
        "data visualization",
        "machine learning",
        "feature engineering",
        "model evaluation",
    },
    "AI/LLM Engineer": {
        "python",
        "llm",
        "rag",
        "langchain",
        "vector database",
        "faiss",
        "chromadb",
        "transformers",
        "fastapi",
        "api",
    },
    "Computer Vision Engineer": {
        "python",
        "computer vision",
        "deep learning",
        "pytorch",
        "tensorflow",
        "numpy",
        "model evaluation",
        "model deployment",
    },
}


ACTION_VERBS = [
    "built",
    "developed",
    "designed",
    "implemented",
    "deployed",
    "optimized",
    "automated",
    "analyzed",
    "trained",
    "evaluated",
]

SECTION_PATTERNS = {
    "contact": r"\b(email|phone|linkedin|github|portfolio)\b|@",
    "summary": r"\b(summary|profile|objective)\b",
    "skills": r"\b(skills|technical skills|technologies)\b",
    "projects": r"\b(projects|academic projects|personal projects)\b",
    "experience": r"\b(experience|internship|work experience|employment)\b",
    "education": r"\b(education|degree|university|college|bachelor|b\.tech|m\.tech)\b",
    "metrics": r"\d+%|\d+\s*(users|records|rows|accuracy|f1|precision|recall|latency|seconds|ms)",
}


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#.\s-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


async def extract_text_from_file(file: UploadFile) -> str:
    content = await file.read()
    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        if fitz is None:
            raise HTTPException(
                status_code=500,
                detail="PDF support is not installed. Run: pip install pymupdf",
            )
        pdf = fitz.open(stream=content, filetype="pdf")
        return "\n".join(page.get_text() for page in pdf)

    if filename.endswith(".docx"):
        if docx is None:
            raise HTTPException(
                status_code=500,
                detail="DOCX support is not installed. Run: pip install python-docx",
            )
        document = docx.Document(io.BytesIO(content))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)

    return content.decode("utf-8", errors="ignore")


def extract_skills(text: str) -> list[str]:
    cleaned = clean_text(text)
    found = []

    for skill in SKILL_KEYWORDS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"
        if re.search(pattern, cleaned):
            found.append(skill)

    return sorted(found)


def calculate_similarity(resume_text: str, job_description: str) -> float:
    resume_tokens = tokenize_for_similarity(resume_text)
    job_tokens = tokenize_for_similarity(job_description)

    if not resume_tokens or not job_tokens:
        return 0

    resume_vector = Counter(resume_tokens)
    job_vector = Counter(job_tokens)
    vocabulary = set(resume_vector) | set(job_vector)

    dot_product = sum(resume_vector[word] * job_vector[word] for word in vocabulary)
    resume_norm = math.sqrt(sum(value * value for value in resume_vector.values()))
    job_norm = math.sqrt(sum(value * value for value in job_vector.values()))

    if resume_norm == 0 or job_norm == 0:
        return 0

    score = dot_product / (resume_norm * job_norm)
    return round(score * 100, 2)


def tokenize_for_similarity(text: str) -> list[str]:
    cleaned = clean_text(text)
    words = [
        word
        for word in cleaned.split()
        if len(word) > 2 and word not in STOP_WORDS
    ]
    bigrams = [f"{words[index]} {words[index + 1]}" for index in range(len(words) - 1)]
    return words + bigrams


def score_keyword_coverage(resume_text: str, job_description: str) -> tuple[float, list[str]]:
    job_keywords = set(extract_top_keywords(job_description, limit=25))
    resume_cleaned = clean_text(resume_text)
    covered = sorted(keyword for keyword in job_keywords if keyword in resume_cleaned)

    if not job_keywords:
        return 0, []

    score = round((len(covered) / len(job_keywords)) * 100, 2)
    missing = sorted(job_keywords - set(covered))[:12]
    return score, missing


def analyze_sections(resume_text: str) -> dict:
    cleaned = clean_text(resume_text)
    return {
        section: bool(re.search(pattern, cleaned))
        for section, pattern in SECTION_PATTERNS.items()
    }


def calculate_ats_score(section_report: dict, resume_text: str) -> float:
    checks = [
        section_report["contact"],
        section_report["skills"],
        section_report["projects"] or section_report["experience"],
        section_report["education"],
        section_report["metrics"],
        len(resume_text.split()) >= 250,
    ]
    return round((sum(checks) / len(checks)) * 100, 2)


def category_breakdown(resume_skills: list[str], job_skills: list[str]) -> dict:
    breakdown = {}
    resume_set = set(resume_skills)
    job_set = set(job_skills)

    for category, skills in SKILL_CATEGORIES.items():
        required = sorted(job_set & skills)
        matched = sorted(resume_set & job_set & skills)
        score = round((len(matched) / len(required)) * 100, 2) if required else 0
        breakdown[category] = {
            "score": score,
            "required": required,
            "matched": matched,
            "missing": sorted(set(required) - set(matched)),
        }

    return breakdown


def predict_roles(resume_skills: list[str]) -> list[dict]:
    resume_set = set(resume_skills)
    predictions = []

    for role, required_skills in ROLE_PROFILES.items():
        matched = sorted(resume_set & required_skills)
        score = round((len(matched) / len(required_skills)) * 100, 2)
        predictions.append(
            {
                "role": role,
                "score": score,
                "matched_skills": matched,
                "next_skills": sorted(required_skills - resume_set)[:5],
            }
        )

    return sorted(predictions, key=lambda item: item["score"], reverse=True)


def extract_top_keywords(text: str, limit: int = 12) -> list[str]:
    cleaned = clean_text(text)
    words = [
        word
        for word in cleaned.split()
        if len(word) > 3 and word not in {"with", "from", "that", "this", "will", "your"}
    ]
    counts = Counter(words)
    return [word for word, _ in counts.most_common(limit)]


def generate_suggestions(
    resume_skills: list[str],
    job_skills: list[str],
    resume_text: str,
    job_description: str,
) -> list[str]:
    missing_skills = sorted(set(job_skills) - set(resume_skills))
    suggestions = []

    if missing_skills:
        suggestions.append(
            "Add evidence for these job-relevant skills if you have used them: "
            + ", ".join(missing_skills[:8])
            + "."
        )

    if not any(verb in clean_text(resume_text) for verb in ACTION_VERBS):
        suggestions.append(
            "Rewrite project bullets with strong action verbs such as built, deployed, optimized, and evaluated."
        )

    if not re.search(r"\d+%|\d+\s*(users|records|rows|accuracy|f1|latency|seconds)", resume_text.lower()):
        suggestions.append(
            "Add measurable impact, such as accuracy, F1-score, latency, dataset size, or user count."
        )

    if "deploy" in clean_text(job_description) and "deploy" not in clean_text(resume_text):
        suggestions.append(
            "Mention deployment details like FastAPI, Docker, cloud hosting, or CI/CD if applicable."
        )

    if len(resume_text.split()) < 180:
        suggestions.append(
            "Your resume text looks short. Add project details, tools used, model metrics, and outcomes."
        )

    section_report = analyze_sections(resume_text)

    if not section_report["projects"]:
        suggestions.append(
            "Add a Projects section with 2-3 AI/ML projects, each showing dataset, model, metrics, and deployment."
        )

    if not section_report["contact"]:
        suggestions.append(
            "Add clear contact links such as email, LinkedIn, GitHub, and portfolio."
        )

    if not suggestions:
        suggestions.append(
            "Your resume already covers many job requirements. Improve it further by adding more quantified achievements."
        )

    return suggestions


def build_resume_bullets(missing_skills: list[str]) -> list[str]:
    focus = ", ".join(missing_skills[:3]) if missing_skills else "machine learning and NLP"
    return [
        f"Built an end-to-end AI application using {focus}, including data processing, model logic, API integration, and dashboard visualization.",
        "Improved resume-job matching using TF-IDF semantic similarity, skill extraction, and keyword gap analysis.",
        "Deployed a FastAPI-based ML service with a responsive frontend for real-time resume analysis and recommendations.",
    ]


def recommend_projects(missing_skills: list[str], role_predictions: list[dict]) -> list[dict]:
    top_role = role_predictions[0]["role"] if role_predictions else "AI/ML Engineer"
    focus = missing_skills[:3] or ["model evaluation", "deployment", "dashboard"]

    return [
        {
            "title": "RAG Knowledge Assistant",
            "why": "Shows LLM, retrieval, embeddings, vector search, evaluation, and deployment skills.",
            "skills_to_show": ["rag", "llm", "vector database", "fastapi", "model evaluation"],
        },
        {
            "title": f"{top_role} Skill Gap Dashboard",
            "why": "Connects directly to your resume story and proves you can build useful ML products.",
            "skills_to_show": focus,
        },
        {
            "title": "MLOps Model Monitoring System",
            "why": "Makes the project look industry-ready by adding drift checks, metrics tracking, and API monitoring.",
            "skills_to_show": ["mlops", "docker", "api", "model deployment"],
        },
    ]


def analyze_match(resume_text: str, job_description: str) -> dict:
    resume_text = resume_text or ""
    job_description = job_description or ""

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)
    missing_skills = sorted(set(job_skills) - set(resume_skills))
    matched_skills = sorted(set(job_skills) & set(resume_skills))
    similarity_score = calculate_similarity(resume_text, job_description)
    keyword_score, missing_keywords = score_keyword_coverage(resume_text, job_description)
    sections = analyze_sections(resume_text)
    ats_score = calculate_ats_score(sections, resume_text)
    categories = category_breakdown(resume_skills, job_skills)
    roles = predict_roles(resume_skills)

    if job_skills:
        skill_score = round((len(matched_skills) / len(job_skills)) * 100, 2)
    else:
        skill_score = 0

    final_score = round(
        (similarity_score * 0.30)
        + (skill_score * 0.35)
        + (keyword_score * 0.20)
        + (ats_score * 0.15),
        2,
    )

    return {
        "overall_score": final_score,
        "similarity_score": similarity_score,
        "skill_score": skill_score,
        "keyword_score": keyword_score,
        "ats_score": ats_score,
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "missing_keywords": missing_keywords,
        "job_keywords": extract_top_keywords(job_description),
        "section_report": sections,
        "category_breakdown": categories,
        "role_predictions": roles,
        "suggestions": generate_suggestions(
            resume_skills,
            job_skills,
            resume_text,
            job_description,
        ),
        "improved_resume_bullets": build_resume_bullets(missing_skills),
        "recommended_projects": recommend_projects(missing_skills, roles),
    }
