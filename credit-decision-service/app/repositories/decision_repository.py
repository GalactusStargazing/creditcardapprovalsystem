import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.decision import DecisionHistory


class DecisionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(
        self, application_id: uuid.UUID, score: int, decision: str, reason: str
    ) -> DecisionHistory:
        record = DecisionHistory(
            application_id=application_id,
            score=score,
            decision=decision,
            reason=reason,
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record
