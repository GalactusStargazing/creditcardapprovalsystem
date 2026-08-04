import uuid

from fastapi import HTTPException, status

from app.models.application import Application
from app.repositories.application_repository import ApplicationRepository
from app.schemas.application import ApplicationCreateRequest


class ApplicationService:
    def __init__(self, repo: ApplicationRepository):
        self.repo = repo

    async def create_application(
        self, user_id: uuid.UUID, data: ApplicationCreateRequest
    ) -> Application:
        application_data = data.model_dump()
        application_data["user_id"] = user_id
        application_data["status"] = "SUBMITTED"

        application = await self.repo.create(application_data)
        return application

    async def get_user_applications(self, user_id: uuid.UUID) -> list[Application]:
        return await self.repo.get_all_by_user(user_id)

    async def get_application_detail(
        self, application_id: uuid.UUID, user_id: uuid.UUID
    ) -> Application:
        application = await self.repo.get_by_id(application_id)

        if application is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )

        if application.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this application",
            )

        return application

    async def get_application_status(
        self, application_id: uuid.UUID, user_id: uuid.UUID
    ) -> Application:
        # Reuses the same ownership check - status lookup has identical
        # authorization rules to fetching the full detail.
        return await self.get_application_detail(application_id, user_id)
