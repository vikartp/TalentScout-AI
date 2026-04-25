# Sample Inputs & Outputs — TalentScout AI

This document shows example data at each stage of the pipeline. Sample JDs and resumes are also available in the [`sample-data/`](sample-data/) folder.

---

## 1. Job Description Input

Raw text pasted into the JD parser:

```
Senior Full-Stack Developer — React + Node.js

Company: TechCorp Solutions
Location: Bangalore, India (Hybrid)
Department: Engineering
Seniority: Senior

Must-Have Skills:
- React.js
- Node.js
- TypeScript
- PostgreSQL
- REST APIs

Nice-to-Have Skills:
- GraphQL
- AWS/GCP
- Docker
- CI/CD pipelines

Experience: 4-8 years
Education: Bachelor's in Computer Science or equivalent
Salary Range: 25-40 LPA
```

### Parsed JD Output

```json
{
  "title": "Senior Full-Stack Developer — React + Node.js",
  "company": "TechCorp Solutions",
  "location": "Bangalore, India (Hybrid)",
  "seniority": "Senior",
  "skills_must_have": ["React.js", "Node.js", "TypeScript", "PostgreSQL", "REST APIs"],
  "skills_nice_to_have": ["GraphQL", "AWS/GCP", "Docker", "CI/CD pipelines"],
  "experience_min": 4,
  "experience_max": 8,
  "education": "Bachelor's in Computer Science or equivalent",
  "salary_range": "25-40 LPA"
}
```

---

## 2. Resume Upload & Parsing

A PDF resume is uploaded and AI-extracted into a structured profile:

### Parsed Candidate Profile

```json
{
  "name": "Priya Sharma",
  "email": "priya.sharma@email.com",
  "phone": "+91-98765-43210",
  "skills": ["React.js", "Node.js", "TypeScript", "PostgreSQL", "REST APIs", "Docker", "Redis", "MongoDB"],
  "total_experience_years": 6,
  "education": [
    {"degree": "B.Tech Computer Science", "institution": "IIT Delhi", "year": 2019}
  ],
  "summary": "Full-stack developer with 6 years of experience building scalable web applications using React, Node.js, and TypeScript. Led a team of 4 at a B2B SaaS startup."
}
```

---

## 3. Matching Results

After running the matcher against the JD:

### Shortlist Table

| Rank | Candidate | Match Score | Interest Score | Final Score |
|------|-----------|-------------|----------------|-------------|
| 1 | Priya Sharma | 82.4 | 85.0 | 83.4 |
| 2 | Rahul Mehta | 78.1 | 72.0 | 75.7 |
| 3 | Ananya Iyer | 71.5 | 68.0 | 70.1 |
| 4 | Vikram Singh | 65.3 | 74.0 | 68.8 |
| 5 | Sneha Patel | 62.0 | 55.0 | 59.2 |

### Detailed Score Breakdown (Top Candidate)

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
  "match_explanation": "Priya is an excellent match for this Senior Full-Stack Developer role. Her 6 years of React + Node.js experience falls squarely in the 4-8 year range, she covers all must-have skills, and her B.Tech from IIT Delhi meets the education requirement. She also brings Docker experience as a bonus."
}
```

---

## 4. AI Conversation

Simulated 4-turn recruiter-candidate outreach:

### Conversation Transcript

```
[RECRUITER]: Hi Priya! I came across your profile and was really impressed by your
full-stack experience, especially your work with React and Node.js at scale. We have
a Senior Full-Stack Developer role at TechCorp Solutions that I think could be a
great fit for you. Would you be open to hearing more about it?

[CANDIDATE]: Hi! Thanks for reaching out. I'm always open to learning about new
opportunities, especially if they involve React and Node.js — that's where I've
spent most of my career. What does the team look like?

[RECRUITER]: Great question! It's a cross-functional team of 8 engineers working
on our B2B SaaS platform. You'd be leading feature development and mentoring
junior devs. The stack is React, Node, TypeScript, and PostgreSQL — right up
your alley. We're hybrid in Bangalore, 3 days in office. How does that sound?

[CANDIDATE]: That sounds exciting! The mentoring aspect is something I really
enjoy — I led a team of 4 at my current role. The hybrid setup works for me
since I'm based in Bangalore. What's the timeline for this role?

[RECRUITER]: We're looking to fill it within the next 4-6 weeks. The interview
process is 3 rounds — a technical screen, a system design session, and a culture
fit chat. The compensation range is 25-40 LPA depending on experience. Does
that align with your expectations?

[CANDIDATE]: That timeline works — I'd need to give my current employer about a
month's notice, so 4-6 weeks is perfect. The compensation range sounds good. I'm
currently at 28 LPA so something in the upper half of that range would be ideal.
I'd love to move forward with the process!

[RECRUITER]: Wonderful! I'll send over the details and schedule the first round
this week. Thanks for your time, Priya — I think this could be a really great
match for both sides.

[CANDIDATE]: Thank you! I'm looking forward to it. Please send over anything I
should prepare for the technical screen. Have a great day!
```

### Interest Scores

```json
{
  "enthusiasm": 9,
  "availability": 8,
  "salary_alignment": 8,
  "cultural_fit": 9,
  "interest_score": 85.0,
  "explanation": "Priya showed strong enthusiasm throughout, expressing genuine excitement about the role and team. She's available within the hiring timeline with a standard notice period. Salary expectations are aligned within the offered range. Her values around mentoring and team leadership indicate excellent cultural fit."
}
```

---

## 5. Final Shortlist Output

The combined output that the hiring manager sees:

```json
[
  {
    "rank": 1,
    "candidate": "Priya Sharma",
    "match_score": 82.4,
    "interest_score": 85.0,
    "final_score": 83.4,
    "recommendation": "Strong Hire — excellent technical fit with high enthusiasm"
  },
  {
    "rank": 2,
    "candidate": "Rahul Mehta",
    "match_score": 78.1,
    "interest_score": 72.0,
    "final_score": 75.7,
    "recommendation": "Hire — solid skills, moderate interest, may need persuasion"
  },
  {
    "rank": 3,
    "candidate": "Ananya Iyer",
    "match_score": 71.5,
    "interest_score": 68.0,
    "final_score": 70.1,
    "recommendation": "Consider — meets core requirements, lukewarm interest"
  }
]
```

---

## Sample Data Files

The [`sample-data/`](sample-data/) directory contains ready-to-use test data:

| File | Description |
|------|-------------|
| `jds/jd-senior-fullstack.txt` | Senior Full-Stack Developer JD |
| `jds/jd-data-scientist.txt` | Data Scientist — Machine Learning JD |
| `jds/jd-devops-engineer.txt` | DevOps Engineer JD |
| `resumes/` | 12 sample resume PDFs with diverse profiles |
| `resume_data.py` | Raw resume data used to generate PDFs |
| `generate_resumes.py` | Script to regenerate resume PDFs |
