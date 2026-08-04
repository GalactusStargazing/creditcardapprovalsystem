import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application


class ApplicationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, application_data: dict) -> Application:
        application = Application(**application_data)
        self.db.add(application)
        await self.db.commit()
        await self.db.refresh(application)
        return application

    async def get_by_id(self, application_id: uuid.UUID) -> Application | None:
        result = await self.db.execute(
            select(Application).where(Application.id == application_id)
        )
        return result.scalar_one_or_none()

    async def get_all_by_user(self, user_id: uuid.UUID) -> list[Application]:
        result = await self.db.execute(
            select(Application)
            .where(Application.user_id == user_id)
            .order_by(Application.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_status(
        self, application: Application, status: str, card_number: str | None = None
    ) -> Application:
        application.status = status
        if card_number is not None:
            application.card_number = card_number
        await self.db.commit()
        await self.db.refresh(application)
        return application
