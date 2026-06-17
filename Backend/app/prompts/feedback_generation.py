"""
Prompt templates for personalized feedback generation.
"""

PROMPT_VERSION = "feedback_generation_v1"

SYSTEM_PROMPT = (
    "You are a career coach and interview expert. "
    "You provide actionable, constructive, and encouraging feedback. "
    "Return only valid JSON. No markdown."
)


def build_feedback_prompt(evaluation_summary: dict) -> str:
    score = evaluation_summary.get("score", 0)
    strengths = "; ".join(evaluation_summary.get("strengths", []))
    weaknesses = "; ".join(evaluation_summary.get("weaknesses", []))
    missing = "; ".join(evaluation_summary.get("missing_points", []))
    question = evaluation_summary.get("question", "")
    answer_summary = evaluation_summary.get("summary", "")

    return f"""Based on this interview answer evaluation, generate personalized coaching feedback.

Question asked: {question}
Evaluation score: {score}/10
Strengths identified: {strengths or 'none noted'}
Weaknesses identified: {weaknesses or 'none noted'}
Missing points: {missing or 'none noted'}
Evaluator summary: {answer_summary}

Generate specific, actionable coaching feedback.

Return ONLY this JSON:
{{
  "strengths": ["specific strength 1", "specific strength 2"],
  "areas_for_improvement": ["specific improvement area 1", "improvement area 2"],
  "recommendations": ["actionable recommendation 1", "actionable recommendation 2", "resource or practice suggestion"]
}}

Guidelines:
- Be encouraging even when pointing out weaknesses.
- Give specific, concrete recommendations (not generic advice).
- Reference the actual question and answer context.
- Recommendations should be actionable (e.g., 'Practice explaining X by...' not just 'Study X').
- Maximum 3 items per list."""


def build_session_feedback_prompt(
    session_evaluations: list[dict],
    interview_type: str,
    overall_score: float,
) -> str:
    """Generate overall session-level feedback after all questions are evaluated."""
    question_summaries = "\n".join(
        f"Q{i+1}: score={e.get('score', 0)}/10 — {e.get('summary', '')}"
        for i, e in enumerate(session_evaluations[:10])
    )

    return f"""Generate comprehensive interview session feedback for a {interview_type.upper()} interview.

Overall score: {overall_score:.1f}/10
Number of questions evaluated: {len(session_evaluations)}

Per-question summaries:
{question_summaries}

Return ONLY this JSON:
{{
  "overall_assessment": "2-3 sentence overall performance summary",
  "key_strengths": ["strength 1", "strength 2", "strength 3"],
  "priority_improvements": ["most important thing to improve", "second priority"],
  "interview_readiness": "ready" | "almost_ready" | "needs_preparation",
  "next_steps": ["specific action 1", "specific action 2", "specific action 3"]
}}"""
