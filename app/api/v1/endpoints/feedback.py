"""
Feedback endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.database import get_db, UserFeedback
from app.core.schemas import FeedbackRequest

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", status_code=201)
async def submit_feedback(
    feedback: FeedbackRequest,
    db: AsyncSession = Depends(get_db)
):
    """Submit feedback for a generated persona."""
    
    # Create feedback record
    db_feedback = UserFeedback(
        persona_id=feedback.persona_id,
        user_id=feedback.user_id,
        rating=feedback.rating,
        corrections=feedback.corrections,
        comments=feedback.comments
    )
    db.add(db_feedback)
    await db.commit()
    
    logger.info(f"Feedback submitted for persona {feedback.persona_id}")
    
    return {"message": "Feedback submitted successfully", "feedback_id": db_feedback.feedback_id}
