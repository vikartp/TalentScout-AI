# Scoring System — TalentScout AI

TalentScout uses a **two-stage scoring pipeline** to rank candidates: a deterministic **Match Score** based on profile-to-JD fit, and an AI-generated **Interest Score** from simulated outreach conversations.

## Match Score (0–100)

Computed from four weighted signals:

| Signal | Weight | Method |
|--------|--------|--------|
| **Semantic Similarity** | 40% | Cosine similarity between JD and resume embeddings (`text-embedding-3-large`) |
| **Skill Match** | 30% | Fuzzy substring matching; must-have skills weighted 2× vs nice-to-have |
| **Experience Fit** | 15% | Gaussian penalty around the JD's ideal experience range (σ=3 years) |
| **Education Match** | 15% | Ordinal comparison of candidate's highest degree vs JD requirement |

### Formula

```
Match Score = (0.40 × Semantic + 0.30 × Skill + 0.15 × Experience + 0.15 × Education) × 100
```

### Signal Details

#### Semantic Similarity (40%)

Both the JD text and the candidate's full resume text are embedded using `text-embedding-3-large`. Cosine similarity between these vectors captures overall domain/role alignment that keyword matching would miss.

#### Skill Match (30%)

Skills from the candidate profile are compared against the JD's must-have and nice-to-have lists using fuzzy substring matching:

- **Exact match**: `"Python"` matches `"Python"`
- **Substring containment**: `"Machine Learning"` matches `"ML/Machine Learning"`
- **Delimiter splitting**: Skills separated by `/`, `,`, `&` are split and compared individually

Scoring:
```
Earned = (matched_must_have × 2) + matched_nice_to_have
Total  = (total_must_have × 2) + total_nice_to_have
Skill Score = Earned / Total
```

Must-have skills are weighted **2×** to penalize missing critical requirements.

#### Experience Fit (15%)

Uses a Gaussian decay function centered on the JD's experience range:

- Within range → **1.0** (perfect score)
- Outside range → exponential decay with **σ=3 years**
- Unknown experience → **0.5** (neutral)
- No JD requirement → **1.0**

```
Score = exp(-0.5 × (distance / 3)²)
```

#### Education Match (15%)

Ordinal degree comparison on a 5-level scale:

| Level | Value |
|-------|-------|
| High School | 1 |
| Associate | 2 |
| Bachelor's | 3 |
| Master's | 4 |
| PhD / Doctorate | 5 |

- Meets or exceeds requirement → **1.0**
- One level below → **0.7**
- Two+ levels below → **0.4**
- Unknown → **0.5**

---

## Interest Score (0–100)

Generated from AI-simulated **4-turn recruiter-candidate conversations**, then evaluated by an LLM scorer.

### Conversation Simulation

The system uses **dual-persona prompting**:

1. **Recruiter persona**: Professional, warm outreach that covers role details, team, timeline, and compensation
2. **Candidate persona**: Realistic responses based on the actual candidate profile — varying enthusiasm, asking questions, expressing concerns

The conversation runs for 4 exchanges (recruiter opens, then 4 candidate responses with recruiter follow-ups).

### Scoring Dimensions

After the conversation, a separate LLM call evaluates the transcript:

| Dimension | Weight | Scale | What it measures |
|-----------|--------|-------|-----------------|
| **Enthusiasm** | 30% | 1–10 | How excited/interested is the candidate? |
| **Availability** | 25% | 1–10 | How soon can they start/interview? |
| **Salary Alignment** | 25% | 1–10 | How aligned are compensation expectations? |
| **Cultural Fit** | 20% | 1–10 | Values and motivation alignment with role |

### Formula

```
Interest Score = (0.30 × Enthusiasm + 0.25 × Availability + 0.25 × Salary + 0.20 × Cultural) × 10
```

---

## Final Ranking

The two scores are combined with configurable weights (default 60/40):

```
Final Score = 0.6 × Match Score + 0.4 × Interest Score
```

**Rationale**: Match Score is weighted higher because technical fit is a prerequisite — a highly interested but unqualified candidate shouldn't rank above a strong match. The 60/40 split still gives meaningful weight to interest, reflecting that engaged candidates are more likely to accept and succeed.

Candidates are sorted by **Final Score descending** to produce the shortlist.

### Score Breakdown Example

```json
{
  "candidate": "Priya Sharma",
  "semantic_score": 87.2,
  "skill_score": 85.0,
  "experience_score": 100.0,
  "education_score": 100.0,
  "match_score": 82.4,
  "matched_skills": ["react.js", "node.js", "typescript", "postgresql", "rest apis", "docker"],
  "missing_skills": [],
  "interest_scores": {
    "enthusiasm": 9,
    "availability": 8,
    "salary_alignment": 8,
    "cultural_fit": 9,
    "interest_score": 85.0
  },
  "final_score": 83.4
}
```
