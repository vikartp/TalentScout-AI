"""Conversational outreach agent — simulates recruiter-candidate conversations."""

import json
from openai import OpenAI
from app.config import OPENAI_API_KEY, OPENAI_API_BASE, CHAT_MODEL

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)

RECRUITER_SYSTEM = """You are a friendly, professional recruiter conducting outreach to a potential candidate.
Your goal is to:
1. Introduce the role and explain why you think they're a good fit
2. Gauge their genuine interest and enthusiasm
3. Ask about their availability and timeline
4. Understand their salary expectations
5. Explore their career motivations and cultural preferences

Keep the conversation natural, warm, and professional. Ask one or two questions at a time.
Based on the conversation context, guide through all topics naturally."""

CANDIDATE_SYSTEM = """You are simulating a real candidate responding to a recruiter's outreach.
Based on your profile, respond naturally and realistically.
Your responses should reflect your actual experience and skills.
Vary your enthusiasm level — not every candidate is equally excited.
Be realistic: ask clarifying questions, express concerns, or show excitement as appropriate.
Keep responses conversational and 2-4 sentences long."""

SCORER_SYSTEM = """Analyze this recruiter-candidate conversation and score the candidate's interest on these dimensions.
Return a JSON object with exactly these keys:
{
  "enthusiasm": <1-10 score>,
  "availability": <1-10 score>,
  "salary_alignment": <1-10 score>,
  "cultural_fit": <1-10 score>,
  "explanation": "Brief explanation of scores"
}
Score guidelines:
- enthusiasm: How excited/interested is the candidate? (1=disinterested, 10=very eager)
- availability: How soon can they start/interview? (1=unavailable, 10=immediately available)
- salary_alignment: Based on any salary discussion, how aligned are expectations? (5=not discussed, 1=far apart, 10=perfect match)
- cultural_fit: Based on motivation and values expressed (1=poor fit, 10=excellent fit)
Return ONLY valid JSON."""


async def run_conversation(
    jd_title: str,
    jd_summary: str,
    candidate_name: str,
    candidate_profile: str,
    match_highlights: str,
    num_turns: int = 4,
) -> dict:
    """Run a full simulated conversation and return transcript + scores."""
    transcript = []

    # Build recruiter context
    recruiter_context = f"""Role: {jd_title}
Key details: {jd_summary}
Candidate: {candidate_name}
Why they match: {match_highlights}"""

    # Build candidate context
    candidate_context = f"""Your profile: {candidate_profile}
The recruiter is reaching out about: {jd_title}"""

    # Recruiter opens
    recruiter_messages = [
        {"role": "system", "content": RECRUITER_SYSTEM},
        {"role": "user", "content": f"Context:\n{recruiter_context}\n\nStart the outreach conversation with the candidate."},
    ]
    recruiter_resp = client.chat.completions.create(
        model=CHAT_MODEL, temperature=0.7, messages=recruiter_messages
    )
    recruiter_msg = recruiter_resp.choices[0].message.content.strip()
    transcript.append({"role": "recruiter", "content": recruiter_msg})

    # Multi-turn conversation
    for turn in range(num_turns):
        # Candidate responds
        candidate_messages = [
            {"role": "system", "content": f"{CANDIDATE_SYSTEM}\n\nYour profile:\n{candidate_context}"},
        ]
        for msg in transcript:
            role = "assistant" if msg["role"] == "candidate" else "user"
            candidate_messages.append({"role": role, "content": msg["content"]})

        cand_resp = client.chat.completions.create(
            model=CHAT_MODEL, temperature=0.7, messages=candidate_messages
        )
        cand_msg = cand_resp.choices[0].message.content.strip()
        transcript.append({"role": "candidate", "content": cand_msg})

        # Recruiter follows up (except on last turn)
        if turn < num_turns - 1:
            recruiter_messages = [
                {"role": "system", "content": RECRUITER_SYSTEM},
                {"role": "user", "content": f"Context:\n{recruiter_context}"},
            ]
            for msg in transcript:
                role = "assistant" if msg["role"] == "recruiter" else "user"
                recruiter_messages.append({"role": role, "content": msg["content"]})
            recruiter_messages.append(
                {"role": "user", "content": "Continue the conversation naturally, covering any remaining topics."}
            )

            rec_resp = client.chat.completions.create(
                model=CHAT_MODEL, temperature=0.7, messages=recruiter_messages
            )
            rec_msg = rec_resp.choices[0].message.content.strip()
            transcript.append({"role": "recruiter", "content": rec_msg})

    return transcript


async def score_conversation(transcript: list[dict], jd_title: str) -> dict:
    """Analyze a conversation transcript and return interest scores."""
    convo_text = "\n".join(f"[{m['role'].upper()}]: {m['content']}" for m in transcript)

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SCORER_SYSTEM},
            {"role": "user", "content": f"Job: {jd_title}\n\nConversation:\n{convo_text}"},
        ],
        response_format={"type": "json_object"},
    )
    scores = json.loads(response.choices[0].message.content)

    # Compute weighted interest score (0-100)
    interest_score = round(
        (0.30 * scores["enthusiasm"] + 0.25 * scores["availability"]
         + 0.25 * scores["salary_alignment"] + 0.20 * scores["cultural_fit"]) * 10,
        1,
    )
    scores["interest_score"] = interest_score
    return scores
