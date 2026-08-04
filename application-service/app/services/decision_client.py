import uuid

import httpx

from app.core.config import settings


class DecisionServiceUnavailable(Exception):
    pass


async def evaluate_application(
    application_id: uuid.UUID,
    monthly_income: float,
    credit_score: int,
    existing_loan_amount: float,
    occupation: str,
) -> dict:
    url = f"{settings.credit_decision_service_url}/api/v1/decisions/evaluate"
    payload = {
        "application_id": str(application_id),
        "monthly_income": float(monthly_income),
        "credit_score": credit_score,
        "existing_loan_amount": float(existing_loan_amount),
        "occupation": occupation,
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
    except (httpx.ConnectError, httpx.TimeoutException) as exc:
        raise DecisionServiceUnavailable(
            "Credit decision service is currently unavailable."
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise DecisionServiceUnavailable(
            f"Credit decision service returned an error: {exc.response.status_code}"
        ) from exc
