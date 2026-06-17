"""
Question service — generates ALL interview questions automatically from
the candidate's resume and job description using an LLM.

Design:
  - PRIMARY: 100% AI-generated questions, personalized to resume + JD.
    No seed script needed. No manual question bank required.

  - FALLBACK: If LLM fails (timeout, API error), silently falls back to
    the question bank (if it has been seeded). This is purely a reliability
    safety net, not part of the normal flow.

  - OPTIONAL: Question bank can still be seeded for the fallback pool,
    but the system works perfectly without it.

Flow:
  POST /interview/generate
      → fetch resume_data + jd_data from DB
      → call LLM with full context
      → LLM returns N personalized questions
      → questions stored in session document
      → returned to client  (no seed script needed)
"""
import logging
import random
import uuid

from app.llm.client import OpenRouterClient
from app.prompts import question_generation as qg_prompt
from app.repositories.question_repo import QuestionRepository

logger = logging.getLogger(__name__)


class QuestionService:
    def __init__(self, question_repo: QuestionRepository, llm: OpenRouterClient) -> None:
        self._repo = question_repo
        self._llm = llm

    async def generate_interview_questions(
        self,
        resume_data: dict,
        jd_data: dict,
        interview_type: str,
        total_count: int = 10,
    ) -> list[dict]:
        """
        Generate ALL interview questions automatically via LLM.

        The LLM receives:
          - Candidate's name, skills, experience, projects
          - Job role, required/preferred skills, responsibilities
          - Interview type (hr / technical / telephonic / virtual)
          - Requested count

        Returns a list of question dicts with sequential ordering.
        Falls back to question bank if LLM is unavailable.
        """
        logger.info(
            "Generating AI interview questions",
            extra={
                "interview_type": interview_type,
                "total_count": total_count,
                "candidate": resume_data.get("name", "unknown"),
                "role": jd_data.get("role", "unknown"),
            },
        )

        # ── Primary path: 100% AI generation ──────────────────
        questions = await self._generate_ai_questions(
            resume_data=resume_data,
            jd_data=jd_data,
            interview_type=interview_type,
            count=total_count,
        )

        # ── If AI returned enough questions, use them ──────────
        if len(questions) >= total_count:
            questions = questions[:total_count]
        elif len(questions) > 0:
            # AI returned some but not enough → top up from bank
            shortfall = total_count - len(questions)
            logger.warning(
                "LLM returned fewer questions than requested, topping up from bank",
                extra={"got": len(questions), "needed": total_count, "shortfall": shortfall},
            )
            bank_extras = await self._get_bank_questions(interview_type, shortfall)
            questions.extend(bank_extras)
        else:
            # AI completely failed → use bank as fallback
            logger.error(
                "LLM question generation failed entirely — using question bank fallback",
                extra={"interview_type": interview_type},
            )
            questions = await self._get_bank_questions(interview_type, total_count)

            # Last resort: generate generic questions if bank is also empty
            if not questions:
                questions = _generic_fallback_questions(interview_type, total_count)

        # ── Assign sequential order ──────────────────────────────
        # Guarantee we never exceed total_count
        questions = questions[:total_count]
        random.shuffle(questions)
        for i, q in enumerate(questions, start=1):
            q["order"] = i

        logger.info(
            "Interview questions ready",
            extra={
                "count": len(questions),
                "ai_generated": sum(1 for q in questions if q["source"] == "ai_generated"),
                "from_bank": sum(1 for q in questions if q["source"] == "bank"),
                "generic": sum(1 for q in questions if q["source"] == "generic"),
            },
        )
        return questions

    # ── Internal: AI generation ────────────────────────────────

    async def _generate_ai_questions(
        self,
        resume_data: dict,
        jd_data: dict,
        interview_type: str,
        count: int,
    ) -> list[dict]:
        """Call LLM to generate personalized questions. Returns [] on failure."""
        try:
            prompt = qg_prompt.build_generation_prompt(
                resume_data=resume_data,
                jd_data=jd_data,
                interview_type=interview_type,
                count=count,
            )
            data = await self._llm.complete_json(
                user_prompt=prompt,
                system_prompt=qg_prompt.SYSTEM_PROMPT,
                temperature=0.7,
                max_tokens=4000,
            )

            raw_questions = data.get("questions", [])
            if not isinstance(raw_questions, list):
                logger.warning("LLM returned unexpected format for questions: %s", type(raw_questions))
                return []

            result = []
            for i, q in enumerate(raw_questions):
                text = q.get("question", "").strip()
                if not text:
                    continue
                result.append({
                    "question_id": f"ai_{uuid.uuid4().hex[:8]}",
                    "source": "ai_generated",
                    "question_text": text,
                    "category": q.get("category", _default_category(interview_type)),
                    "difficulty": _normalize_difficulty(q.get("difficulty", "medium")),
                    "rationale": q.get("rationale", ""),
                    "tags": [],
                })

            logger.info("LLM generated %d questions", len(result))
            return result

        except Exception as exc:
            logger.error("LLM question generation failed: %s", exc)
            return []

    # ── Internal: Bank fallback ────────────────────────────────

    async def _get_bank_questions(
        self, interview_type: str, count: int
    ) -> list[dict]:
        """Pull questions from bank — used only as fallback."""
        try:
            bank_count = await self._repo.get_count_by_type(interview_type)
            if bank_count == 0:
                logger.warning(
                    "Question bank is empty for type '%s'. "
                    "Run: python scripts/seed_questions.py  (optional fallback only)",
                    interview_type,
                )
                return []

            docs = await self._repo.get_random_sample(interview_type, count)
            return [
                {
                    "question_id": doc["_id"],
                    "source": "bank",
                    "question_text": doc["question"],
                    "category": doc.get("category", ""),
                    "difficulty": doc.get("difficulty", "medium"),
                    "tags": doc.get("tags", []),
                }
                for doc in docs
            ]
        except Exception as exc:
            logger.error("Bank fallback failed: %s", exc)
            return []


# ── Module-level helpers ───────────────────────────────────────

def _normalize_difficulty(value: str) -> str:
    """Ensure difficulty is one of easy/medium/hard."""
    v = str(value).lower().strip()
    return v if v in ("easy", "medium", "hard") else "medium"


def _default_category(interview_type: str) -> str:
    defaults = {
        "hr": "Behavioral",
        "technical": "Technical",
        "telephonic": "Screening",
        "virtual": "Mixed",
    }
    return defaults.get(interview_type, "General")


def _generic_fallback_questions(interview_type: str, count: int) -> list[dict]:
    """
    Absolute last resort — hardcoded generic questions used only when
    both LLM AND question bank are unavailable. This should never happen
    in production with a valid OPENROUTER_API_KEY.
    """
    GENERIC = {
        "hr": [
            "Tell me about yourself.",
            "What are your greatest strengths?",
            "Why are you interested in this role?",
            "Describe a challenge you overcame.",
            "Where do you see yourself in 5 years?",
            "How do you handle pressure?",
            "Tell me about a time you worked in a team.",
            "What motivates you professionally?",
            "How do you prioritize tasks?",
            "What are your salary expectations?",
        ],
        "technical": [
            "Explain the concept of object-oriented programming.",
            "What is the difference between SQL and NoSQL databases?",
            "How does REST API work?",
            "Explain what a microservice architecture is.",
            "What is version control and why is it important?",
            "How do you approach debugging a complex issue?",
            "What is the difference between concurrency and parallelism?",
            "Explain what CI/CD means.",
            "What are design patterns and why are they useful?",
            "How do you ensure code quality?",
        ],
        "telephonic": [
            "Can you walk me through your resume?",
            "Why are you looking for a new opportunity?",
            "What is your notice period?",
            "What are your salary expectations?",
            "What technologies are you most comfortable with?",
            "Describe your current role briefly.",
            "Are you open to remote or hybrid work?",
            "Can you describe your biggest achievement?",
            "Why do you want to work at our company?",
            "Do you have any questions for us?",
        ],
        "virtual": [
            "Tell me about yourself and your background.",
            "Walk me through the most complex project you've built.",
            "How do you stay productive in a remote environment?",
            "Describe a technical challenge you solved recently.",
            "How do you approach learning new technologies?",
            "Tell me about a time you led a project.",
            "How do you handle disagreements in a team?",
            "What tools do you use for collaboration?",
            "Describe your ideal engineering team.",
            "What would you do in your first 30 days here?",
        ],
    }
    pool = GENERIC.get(interview_type, GENERIC["hr"])
    # Cycle through pool if count > pool size
    selected = (pool * (count // len(pool) + 1))[:count]
    return [
        {
            "question_id": f"generic_{i}",
            "source": "generic",
            "question_text": q,
            "category": _default_category(interview_type),
            "difficulty": "medium",
            "tags": [],
        }
        for i, q in enumerate(selected)
    ]
