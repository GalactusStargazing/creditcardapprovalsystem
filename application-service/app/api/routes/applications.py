import uuid
import logging

from fastapi import APIRouter, Depends, status

from app.api.deps import get_application_service, get_current_user_id
from app.schemas.application import (
    ApplicationCreateRequest,
    ApplicationListItem,
    ApplicationResponse,
    ApplicationStatusResponse,
)
from app.services.application_service import ApplicationService

logger = logging.getLogger("application-service")

router = APIRouter(prefix="/api/v1/applications", tags=["applications"])


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    data: ApplicationCreateRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ApplicationService = Depends(get_application_service),
):
    logger.info(f"Application creation requested: user_id={user_id}, card_type={data.card_type}")
    application = await service.create_application(user_id, data)
    logger.info(f"Application created: application_id={application.id}, user_id={user_id}, status={application.status}")
    return application


@router.get("", response_model=list[ApplicationListItem])
async def list_my_applications(
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ApplicationService = Depends(get_application_service),
):
    applications = await service.get_user_applications(user_id)
    return applications


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ApplicationService = Depends(get_application_service),
):
    application = await service.get_application_detail(application_id, user_id)
    return application


@router.get("/{application_id}/status", response_model=ApplicationStatusResponse)
async def get_application_status(
    application_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ApplicationService = Depends(get_application_service),
):
    application = await service.get_application_status(application_id, user_id)
    return ApplicationStatusResponse(application_id=application.id, status=application.status)
