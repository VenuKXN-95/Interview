"""
Prompt templates for AI-powered interview question generation.

All questions are generated 100% by the LLM based on:
  - The candidate's actual resume (skills, experience, projects, education)
  - The job description (role, required skills, responsibilities)
  - The interview type (hr / technical / telephonic / virtual)

No pre-seeded question bank is needed. Every question is personalized.
"""

PROMPT_VERSION = "question_generation_v2"

# Per-interview-type guidance for the LLM
_TYPE_CONTEXT = {
    "hr": {
        "focus": "behavioral patterns, communication style, culture fit, career motivation, teamwork, and leadership",
        "style": "open-ended behavioral questions using the STAR framework (Situation, Task, Action, Result)",
        "question_types": "Behavioral, Culture Fit, Communication, Leadership, Conflict Resolution, Career Growth",
        "avoid": "deep technical questions, coding problems",
        "example": "Tell me about a time you had to manage conflicting priorities at {company}.",
    },
    "technical": {
        "focus": "technical depth, system design, architecture decisions, debugging approach, code quality, and domain expertise",
        "style": "specific technical questions directly about the candidate's own tech stack, past projects, and job requirements",
        "question_types": "Technical Concept, System Design, Architecture, Project Deep-dive, Problem Solving, Code Quality",
        "avoid": "generic HR/behavioral questions, overly broad generic questions",
        "example": "In your {project} project, how did you handle {specific_aspect}? What would you do differently?",
    },
    "telephonic": {
        "focus": "resume validation, role fit, communication clarity, motivation, availability, and basic qualifications",
        "style": "concise, direct screening questions answerable in 1-3 minutes",
        "question_types": "Resume Validation, Role Fit, Availability, Salary, Basic Technical, Motivation",
        "avoid": "complex multi-part questions, long behavioral stories, deep technical dives",
        "example": "What is your current notice period and are you open to {location/remote} work?",
    },
    "virtual": {
        "focus": "balanced mix of technical competency, behavioral patterns, situational judgment, and remote work suitability",
        "style": "well-rounded questions combining technical depth with communication and situational thinking",
        "question_types": "Technical, Behavioral, Situational, Case Study, Project, Remote Work",
        "avoid": "excessively narrow niche questions",
        "example": "Walk me through how you designed the architecture for {project}. What trade-offs did you make?",
    },
}

SYSTEM_PROMPT = (
    "You are a senior technical interviewer and HR expert with 15 years of experience "
    "conducting interviews at top technology companies. "
    "Your task is to generate highly personalized, relevant interview questions based on "
    "a candidate's actual background and the specific job requirements. "
    "Questions must reference the candidate's real experience, not be generic. "
    "Return ONLY valid JSON. No markdown code fences. No explanatory text."
)


def build_generation_prompt(
    resume_data: dict,
    jd_data: dict,
    interview_type: str,
    count: int,
) -> str:
    """
    Build a fully-contextualized question generation prompt.
    The LLM receives complete candidate + JD context and generates
    `count` personalized questions.
    """
    ctx = _TYPE_CONTEXT.get(interview_type, _TYPE_CONTEXT["hr"])

    # Candidate context
    candidate_name = resume_data.get("name", "the candidate")
    candidate_email = resume_data.get("email", "")
    skills = resume_data.get("skills", [])
    candidate_skills = ", ".join(skills[:20]) if skills else "not specified"
    candidate_experience = _format_experience(resume_data.get("experience", []))
    candidate_projects = _format_projects(resume_data.get("projects", []))
    candidate_education = _format_education(resume_data.get("education", []))
    years_exp = _estimate_experience_years(resume_data.get("experience", []))

    # JD context
    jd_role = jd_data.get("role", "the role")
    jd_company = jd_data.get("company", "the company")
    jd_required_skills = ", ".join(jd_data.get("required_skills", [])[:12]) or "not specified"
    jd_preferred_skills = ", ".join(jd_data.get("preferred_skills", [])[:8]) or "none listed"
    jd_responsibilities = _format_list(jd_data.get("responsibilities", [])[:6])
    jd_experience_req = jd_data.get("experience_required", "not specified")

    # Difficulty distribution guidance
    easy_count = max(1, round(count * 0.25))
    medium_count = max(1, round(count * 0.50))
    hard_count = count - easy_count - medium_count

    return f"""You are conducting a {interview_type.upper()} interview.

CANDIDATE: {candidate_name}
  - Skills: {candidate_skills}
  - Experience: {candidate_experience}
  - Approximate years of experience: {years_exp}
  - Projects: {candidate_projects}
  - Education: {candidate_education}

POSITION BEING APPLIED FOR:
  - Role: {jd_role}
  - Company: {jd_company}
  - Required Skills: {jd_required_skills}
  - Preferred Skills: {jd_preferred_skills}
  - Key Responsibilities: {jd_responsibilities}
  - Experience Required: {jd_experience_req}

INTERVIEW TYPE: {interview_type.upper()}
  - Focus: {ctx['focus']}
  - Question Style: {ctx['style']}
  - Question Types to Include: {ctx['question_types']}
  - Avoid: {ctx['avoid']}

YOUR TASK:
Generate exactly {count} interview questions that are:

1. PERSONALIZED — Reference this candidate's actual skills, specific projects, companies they worked at, or technologies they used. Do NOT ask generic questions that could apply to any candidate.

2. RELEVANT — Every question must relate to either the candidate's background OR the job requirements (ideally both).

3. DIFFICULTY SPREAD — Include approximately:
   - {easy_count} easy questions (foundational, confidence-building)
   - {medium_count} medium questions (core competency)
   - {hard_count} hard questions (challenging, differentiating)

4. REALISTIC — Ask questions exactly as a real interviewer would in a {interview_type} interview.

5. DIVERSE — Cover different categories: {ctx['question_types']}

Return ONLY this JSON (no markdown, no explanation):
{{
  "questions": [
    {{
      "question": "<the full interview question text>",
      "category": "<one of: {ctx['question_types']}>",
      "difficulty": "<easy | medium | hard>",
      "rationale": "<1 sentence: why this question is relevant to this specific candidate and role>"
    }}
  ]
}}

Generate all {count} questions now:"""


def _format_experience(experience: list[dict]) -> str:
    if not experience:
        return "not specified"
    parts = []
    for e in experience[:4]:
        role = e.get("role", "")
        company = e.get("company", "")
        duration = e.get("duration", "")
        desc = e.get("description", "")[:80]
        line = f"{role} at {company}"
        if duration:
            line += f" ({duration})"
        if desc:
            line += f" — {desc}"
        parts.append(line)
    return "; ".join(parts)


def _format_projects(projects: list[dict]) -> str:
    if not projects:
        return "not listed"
    parts = []
    for p in projects[:4]:
        name = p.get("name", "")
        tech = ", ".join(p.get("technologies", [])[:5])
        desc = p.get("description", "")[:120]
        line = name
        if tech:
            line += f" [{tech}]"
        if desc:
            line += f": {desc}"
        parts.append(line)
    return "; ".join(parts)


def _format_education(education: list[dict]) -> str:
    if not education:
        return "not listed"
    parts = []
    for e in education[:2]:
        degree = e.get("degree", "")
        institution = e.get("institution", "")
        year = e.get("year", "")
        line = degree
        if institution:
            line += f" from {institution}"
        if year:
            line += f" ({year})"
        parts.append(line)
    return "; ".join(parts)


def _format_list(items: list[str]) -> str:
    if not items:
        return "not specified"
    return "; ".join(str(i) for i in items[:6])


def _estimate_experience_years(experience: list[dict]) -> str:
    """Best-effort estimate of years of experience."""
    if not experience:
        return "unknown"
    count = len(experience)
    if count >= 4:
        return "5+ years"
    elif count == 3:
        return "3-5 years"
    elif count == 2:
        return "2-3 years"
    else:
        return "0-2 years"
