import uuid
import logging

from fastapi import HTTPException, status

from app.core.card_utils import generate_card_number
from app.models.application import Application
from app.repositories.application_repository import ApplicationRepository
from app.schemas.application import ApplicationCreateRequest
from app.services.decision_client import DecisionServiceUnavailable, evaluate_application

logger = logging.getLogger("application-service")


class ApplicationService:
    def __init__(self, repo: ApplicationRepository):
        self.repo = repo

    async def create_application(
        self, user_id: uuid.UUID, data: ApplicationCreateRequest
    ) -> Application:
        try:
            application_data = data.model_dump()
            application_data["user_id"] = user_id
            application_data["status"] = "SUBMITTED"

            application = await self.repo.create(application_data)
            logger.info(f"Application saved: application_id={application.id}, status=SUBMITTED")

            # Move to UNDER_REVIEW before calling out to Credit Decision Service
            application = await self.repo.update_status(application, "UNDER_REVIEW")
            logger.info(f"Application status updated: application_id={application.id}, status=UNDER_REVIEW")

            try:
                logger.info(f"Calling decision-service: application_id={application.id}")
                result = await evaluate_application(
                    application_id=application.id,
                    monthly_income=float(application.monthly_income),
                    credit_score=application.credit_score,
                    existing_loan_amount=float(application.existing_loan_amount),
                    occupation=application.occupation,
                )
                logger.info(
                    f"decision-service responded: application_id={application.id}, "
                    f"decision={result['decision']}, score={result.get('score')}"
                )
            except DecisionServiceUnavailable:
                logger.warning(f"decision-service unavailable: application_id={application.id}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=(
                        "Credit decision service is currently unavailable. "
                        "Your application has been saved and is under review."
                    ),
                )

            decision = result["decision"]
            card_number = generate_card_number() if decision == "APPROVED" else None

            application = await self.repo.update_status(
                application, decision, card_number=card_number
            )
            logger.info(f"Application finalized: application_id={application.id}, final_status={decision}")

            return application

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating application: user_id={user_id}, error={str(e)}", exc_info=True)
            raise

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
