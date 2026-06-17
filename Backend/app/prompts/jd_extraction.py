"""
Prompt templates for Job Description structured data extraction.
"""

PROMPT_VERSION = "jd_extraction_v1"


def build_extraction_prompt(raw_text: str) -> str:
    return f"""You are an expert HR data extractor. Extract structured information from the job description below.

Return ONLY a valid JSON object — no markdown, no explanation, no code block.

Required JSON structure:
{{
  "role": "job title / role name",
  "company": "company name or empty string if not mentioned",
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill1", "skill2"],
  "experience_required": "e.g. 3+ years or 2-4 years",
  "responsibilities": ["responsibility 1", "responsibility 2"]
}}

Rules:
- If a field is not found, use an empty string or empty array.
- Separate must-have from nice-to-have skills accurately.
- Return ONLY the JSON object.

Job Description:
---
{raw_text[:6000]}
---"""


SYSTEM_PROMPT = (
    "You are a precise HR data extractor. You parse job descriptions into structured JSON. "
    "Never add commentary or markdown. Return only valid JSON."
)
