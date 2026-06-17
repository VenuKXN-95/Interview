"""
Prompt templates for resume structured data extraction.
All prompts are version-tagged so we can track which prompt produced which output.
"""

PROMPT_VERSION = "resume_extraction_v1"


def build_extraction_prompt(raw_text: str) -> str:
    """
    Build the LLM prompt to extract structured data from raw resume text.
    Returns a strict JSON-only prompt.
    """
    return f"""You are an expert resume parser. Extract structured information from the resume text below.

Return ONLY a valid JSON object — no markdown, no explanation, no code block.

Required JSON structure:
{{
  "name": "full name of the candidate",
  "email": "email address or empty string",
  "phone": "phone number or empty string",
  "skills": ["skill1", "skill2", "..."],
  "experience": [
    {{
      "company": "company name",
      "role": "job title",
      "duration": "e.g. Jan 2020 - Dec 2022",
      "description": "brief description of responsibilities"
    }}
  ],
  "projects": [
    {{
      "name": "project name",
      "description": "what the project does",
      "technologies": ["tech1", "tech2"]
    }}
  ],
  "education": [
    {{
      "institution": "university or college name",
      "degree": "degree name and specialization",
      "year": "graduation year"
    }}
  ]
}}

Rules:
- If a field is not found, use an empty string or empty array.
- Do NOT invent information.
- Extract ALL skills mentioned anywhere in the resume.
- Return ONLY the JSON object.

Resume Text:
---
{raw_text[:6000]}
---"""


SYSTEM_PROMPT = (
    "You are a precise resume parser. You extract structured data from resumes "
    "and return only valid JSON. Never add commentary or markdown."
)
