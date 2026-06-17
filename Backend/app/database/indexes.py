"""
MongoDB index definitions.
Called once on startup. All indexes are idempotent (create_index is safe to call
multiple times — MongoDB ignores if the index already exists).

Design rationale is documented per collection.
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, IndexModel

from app.core.logging import get_logger

logger = get_logger(__name__)


async def create_all_indexes(db: AsyncIOMotorDatabase) -> None:
    await _index_resumes(db)
    await _index_job_descriptions(db)
    await _index_question_bank(db)
    await _index_interview_sessions(db)
    await _index_answers(db)
    await _index_evaluations(db)
    await _index_reports(db)
    await _index_users(db)
    logger.info("All MongoDB indexes verified/created.")


async def _index_resumes(db: AsyncIOMotorDatabase) -> None:
    """
    - created_at DESC: list resumes by newest first.
    """
    await db.resumes.create_indexes(
        [IndexModel([("created_at", DESCENDING)], name="resumes_created_at")]
    )


async def _index_job_descriptions(db: AsyncIOMotorDatabase) -> None:
    """
    - created_at DESC: list JDs by newest first.
    """
    await db.job_descriptions.create_indexes(
        [IndexModel([("created_at", DESCENDING)], name="jds_created_at")]
    )


async def _index_question_bank(db: AsyncIOMotorDatabase) -> None:
    """
    - (interview_type, difficulty): primary query for 40% bank sampling.
      Enables index-only query with no collection scan.
    - tags (multikey): skill-based question lookup when AI generation needs bank hints.
    - is_active: filter inactive questions without scanning full collection.
    """
    await db.question_bank.create_indexes(
        [
            IndexModel(
                [("interview_type", ASCENDING), ("difficulty", ASCENDING)],
                name="qbank_type_difficulty",
            ),
            IndexModel([("tags", ASCENDING)], name="qbank_tags"),
            IndexModel([("is_active", ASCENDING)], name="qbank_active"),
        ]
    )


async def _index_interview_sessions(db: AsyncIOMotorDatabase) -> None:
    """
    - resume_id + jd_id: join sessions back to source documents.
    - status: dashboard / monitoring queries (e.g., all 'running' sessions).
    - created_at DESC: chronological listing.
    """
    await db.interview_sessions.create_indexes(
        [
            IndexModel([("resume_id", ASCENDING)], name="sessions_resume_id"),
            IndexModel([("jd_id", ASCENDING)], name="sessions_jd_id"),
            IndexModel([("status", ASCENDING)], name="sessions_status"),
            IndexModel([("created_at", DESCENDING)], name="sessions_created_at"),
        ]
    )


async def _index_answers(db: AsyncIOMotorDatabase) -> None:
    """
    - session_id: virtually all answer queries filter by session.
      This is the most important index in this collection.
    - submitted_at: ordering within a session.
    """
    await db.answers.create_indexes(
        [
            IndexModel([("session_id", ASCENDING)], name="answers_session_id"),
            IndexModel([("submitted_at", ASCENDING)], name="answers_submitted_at"),
        ]
    )


async def _index_evaluations(db: AsyncIOMotorDatabase) -> None:
    """
    - session_id: score aggregation queries always group by session.
    - answer_id (unique): prevents duplicate LLM evaluations on retry.
    """
    await db.evaluations.create_indexes(
        [
            IndexModel([("session_id", ASCENDING)], name="evals_session_id"),
            IndexModel(
                [("answer_id", ASCENDING)],
                unique=True,
                name="evals_answer_id_unique",
            ),
        ]
    )


async def _index_reports(db: AsyncIOMotorDatabase) -> None:
    """
    - session_id (unique): exactly one report per session.
    """
    await db.reports.create_indexes(
        [
            IndexModel(
                [("session_id", ASCENDING)],
                unique=True,
                name="reports_session_id_unique",
            )
        ]
    )


async def _index_users(db: AsyncIOMotorDatabase) -> None:
    """
    - email (unique): ensures no duplicate accounts and fast login lookup.
    - created_at DESC: admin listing by newest first.
    """
    await db.users.create_indexes(
        [
            IndexModel(
                [("email", ASCENDING)],
                unique=True,
                name="users_email_unique",
            ),
            IndexModel([("created_at", DESCENDING)], name="users_created_at"),
        ]
    )
