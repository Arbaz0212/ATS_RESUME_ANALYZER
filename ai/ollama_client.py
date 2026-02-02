import requests
from app.config import OLLAMA_MODEL, OLLAMA_URL

def ai_suggestions(resume, jd):
    prompt = f"""
You are an ATS expert.
Give improvement suggestions only.

Resume:
{resume}

Job Description:
{jd}
"""
    response = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    )
    return response.json().get("response", "")
