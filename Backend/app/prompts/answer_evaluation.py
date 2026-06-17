"""
Prompt templates for answer evaluation.
Produces structured JSON evaluation with score and feedback.
"""

PROMPT_VERSION = "answer_evaluation_v1"

SYSTEM_PROMPT = (
    "You are an expert interviewer and evaluator. "
    "You evaluate candidate answers objectively and provide constructive feedback. "
    "Return only valid JSON. No markdown. No commentary."
)


def build_evaluation_prompt(
    question: str,
    answer: str,
    interview_type: str,
    category: str = "",
) -> str:
    return f"""Evaluate the following interview answer for a {interview_type.upper()} interview.

Question: {question}

Category: {category or 'General'}

Candidate's Answer: {answer or '[No answer provided]'}

Evaluation Criteria:
- Technical Accuracy: Is the answer factually correct and technically sound?
- Completeness: Does it cover all key aspects of the question?
- Relevance: Does it directly address what was asked?
- Communication: Is it well-structured, clear, and articulate?

Return ONLY this JSON:
{{
  "score": <integer 0-10>,
  "category_scores": {{
    "technical_accuracy": <0-10>,
    "completeness": <0-10>,
    "relevance": <0-10>,
    "communication": <0-10>
  }},
  "strengths": ["strength 1", "strength 2"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "missing_points": ["important point not mentioned"],
  "summary": "2-3 sentence overall assessment",
  "feedback": {{
    "strengths": ["specific coaching strength 1", "specific coaching strength 2"],
    "areas_for_improvement": ["specific improvement area 1", "improvement area 2"],
    "recommendations": ["actionable coaching recommendation 1", "actionable coaching recommendation 2"]
  }}
}}

Scoring guide:
  9-10: Exceptional — exceeds expectations
  7-8:  Good — meets expectations well
  5-6:  Average — partially addresses the question
  3-4:  Below average — significant gaps
  0-2:  Poor — incorrect or no meaningful answer

Coaching Feedback Guidelines:
- feedback.strengths: specific positive aspects of their answer (encouraging tone)
- feedback.areas_for_improvement: specific gaps or areas to build on
- feedback.recommendations: concrete, actionable steps to improve the answer or general skills (max 3 items per list)

Be fair, constructive, and specific. Reference the actual answer content."""
