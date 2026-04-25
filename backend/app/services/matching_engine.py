"""Matching engine — computes Match Score between a JD and candidates."""

import json
import math
from openai import OpenAI
from app.config import OPENAI_API_KEY, OPENAI_API_BASE, CHAT_MODEL
from app.db.vector_store import embeddings

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def compute_skill_score(
    candidate_skills: list[str],
    must_have: list[str],
    nice_to_have: list[str],
) -> tuple[float, list[str], list[str]]:
    """Fuzzy skill matching with must-have weighted 2x.

    Uses substring containment so 'Machine Learning' matches 'ML/Machine Learning',
    and 'Python' matches 'Python 3' etc.
    """
    cand_lower = [s.lower().strip() for s in candidate_skills]
    must_lower = [s.lower().strip() for s in must_have]
    nice_lower = [s.lower().strip() for s in nice_to_have]

    def _skill_matches(required: str, candidate_list: list[str]) -> bool:
        """Check if a required skill matches any candidate skill via substring or vice-versa."""
        for c in candidate_list:
            if required == c:
                return True
            if required in c or c in required:
                return True
            # Handle common abbreviations: split on / , & and check parts
            req_parts = {p.strip() for p in required.replace("/", ",").replace("&", ",").split(",")}
            cand_parts = {p.strip() for p in c.replace("/", ",").replace("&", ",").split(",")}
            if req_parts & cand_parts:
                return True
        return False

    matched_must_labels = []
    missing_must_labels = []
    for skill in must_lower:
        if _skill_matches(skill, cand_lower):
            matched_must_labels.append(skill)
        else:
            missing_must_labels.append(skill)

    matched_nice_labels = []
    for skill in nice_lower:
        if _skill_matches(skill, cand_lower):
            matched_nice_labels.append(skill)

    # Weighted score: must-have counts 2x
    total_weight = len(must_lower) * 2 + len(nice_lower)
    if total_weight == 0:
        return 1.0, matched_must_labels + matched_nice_labels, []
    earned = len(matched_must_labels) * 2 + len(matched_nice_labels)
    score = earned / total_weight

    matched = matched_must_labels + matched_nice_labels
    missing = missing_must_labels
    return score, matched, missing


def compute_experience_score(
    candidate_years: float | None,
    jd_min: int | None,
    jd_max: int | None,
) -> float:
    """Gaussian penalty around ideal experience range."""
    if candidate_years is None:
        return 0.5  # unknown → neutral
    if jd_min is None and jd_max is None:
        return 1.0  # no requirement

    ideal_min = jd_min or 0
    ideal_max = jd_max or ideal_min + 5

    if ideal_min <= candidate_years <= ideal_max:
        return 1.0

    # Distance from nearest bound
    if candidate_years < ideal_min:
        dist = ideal_min - candidate_years
    else:
        dist = candidate_years - ideal_max
    # Gaussian decay with sigma=3
    return math.exp(-0.5 * (dist / 3) ** 2)


def compute_education_score(
    candidate_education: list[dict] | str | None,
    jd_education: str | None,
) -> float:
    """Simple ordinal education matching."""
    if not jd_education:
        return 1.0
    if not candidate_education:
        return 0.3

    levels = {"high school": 1, "associate": 2, "bachelor": 3, "master": 4, "phd": 5, "doctorate": 5}
    jd_lower = jd_education.lower()
    jd_level = 3  # default bachelor
    for key, val in levels.items():
        if key in jd_lower:
            jd_level = val
            break

    # Parse candidate's highest degree
    cand_level = 0
    if isinstance(candidate_education, list):
        for edu in candidate_education:
            degree = edu.get("degree", "").lower() if isinstance(edu, dict) else str(edu).lower()
            for key, val in levels.items():
                if key in degree:
                    cand_level = max(cand_level, val)
            # Also check "B.S.", "M.S.", etc.
            if "b.s" in degree or "b.a" in degree or "bs " in degree or "ba " in degree:
                cand_level = max(cand_level, 3)
            elif "m.s" in degree or "m.a" in degree or "ms " in degree or "mba" in degree:
                cand_level = max(cand_level, 4)
    elif isinstance(candidate_education, str):
        for key, val in levels.items():
            if key in candidate_education.lower():
                cand_level = max(cand_level, val)

    if cand_level == 0:
        return 0.5  # couldn't determine
    if cand_level >= jd_level:
        return 1.0
    if cand_level == jd_level - 1:
        return 0.7
    return 0.4


async def compute_match_score(
    jd_text: str,
    jd_parsed: dict,
    candidate_text: str,
    candidate_parsed: dict,
) -> dict:
    """Compute full match score with breakdown."""
    # 1. Semantic similarity via embeddings
    jd_emb = embeddings.embed_query(jd_text)
    cand_emb = embeddings.embed_query(candidate_text)
    semantic = cosine_similarity(jd_emb, cand_emb)

    # 2. Skill match
    cand_skills = candidate_parsed.get("skills", []) or []
    must_have = jd_parsed.get("skills_must_have", []) or []
    nice_to_have = jd_parsed.get("skills_nice_to_have", []) or []
    skill_score, matched_skills, missing_skills = compute_skill_score(cand_skills, must_have, nice_to_have)

    # 3. Experience fit
    cand_exp = candidate_parsed.get("total_experience_years")
    exp_score = compute_experience_score(cand_exp, jd_parsed.get("experience_min"), jd_parsed.get("experience_max"))

    # 4. Education match
    cand_edu = candidate_parsed.get("education")
    edu_score = compute_education_score(cand_edu, jd_parsed.get("education"))

    # Weighted combination → 0-100 scale
    match_score = round(
        (0.40 * semantic + 0.30 * skill_score + 0.15 * exp_score + 0.15 * edu_score) * 100, 1
    )

    return {
        "semantic_score": round(semantic * 100, 1),
        "skill_score": round(skill_score * 100, 1),
        "experience_score": round(exp_score * 100, 1),
        "education_score": round(edu_score * 100, 1),
        "match_score": match_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }


async def generate_match_explanation(
    jd_title: str,
    candidate_name: str,
    scores: dict,
) -> str:
    """Generate a human-readable match explanation using LLM."""
    prompt = f"""Given these matching results between the job "{jd_title}" and candidate "{candidate_name}":
- Overall Match Score: {scores['match_score']}/100
- Semantic Similarity: {scores['semantic_score']}/100
- Skill Match: {scores['skill_score']}/100 (Matched: {scores['matched_skills']}, Missing: {scores['missing_skills']})
- Experience Fit: {scores['experience_score']}/100
- Education Fit: {scores['education_score']}/100

Write a concise 2-3 sentence explanation of why this candidate does or doesn't match the role. Be specific about strengths and gaps."""

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0.3,
        messages=[
            {"role": "system", "content": "You are a recruitment analyst. Be concise and specific."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content.strip()
