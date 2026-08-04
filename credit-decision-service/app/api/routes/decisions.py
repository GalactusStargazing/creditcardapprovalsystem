from fastapi import APIRouter, Depends

from app.api.deps import get_decision_service
from app.schemas.decision import DecisionEvaluateRequest, DecisionResponse
from app.services.decision_service import DecisionService

router = APIRouter(prefix="/api/v1/decisions", tags=["decisions"])


@router.post("/evaluate", response_model=DecisionResponse)
async def evaluate(
    data: DecisionEvaluateRequest,
    service: DecisionService = Depends(get_decision_service),
):
    return await service.evaluate(data)
