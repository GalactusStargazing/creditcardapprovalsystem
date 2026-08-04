from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.decision_repository import DecisionRepository
from app.services.decision_service import DecisionService


def get_decision_service(db: AsyncSession = Depends(get_db)) -> DecisionService:
    repo = DecisionRepository(db)
    return DecisionService(repo)
