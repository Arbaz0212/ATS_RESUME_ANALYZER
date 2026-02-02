from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def text_similarity(resume_text: str, jd_text: str) -> float:
    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform([resume_text, jd_text])
    return cosine_similarity(vectors[0:1], vectors[1:2])[0][0]


def calculate_ats_score(
    matched_skills: list[str],
    jd_skills: list[str],
    resume_text: str,
    jd_text: str
) -> float:

    if not jd_skills:
        return 0.0

    # Only count REAL skills
    matched_count = len(matched_skills)
    total_required = max(len(jd_skills), 5)  # avoid tiny JD inflation

    skill_coverage = matched_count / total_required
    similarity_score = text_similarity(resume_text, jd_text)

    depth_bonus = min(matched_count * 0.02, 0.1)

    final_score = (
        (skill_coverage * 0.6) +
        (similarity_score * 0.3) +
        depth_bonus
    ) * 100

    return round(min(final_score, 95.0), 2)
