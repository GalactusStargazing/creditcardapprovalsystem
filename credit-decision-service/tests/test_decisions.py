import uuid

import pytest

from app.services.scoring import calculate_score, make_decision


def test_high_score_gets_approved():
    score = calculate_score(
        credit_score=750, monthly_income=80000, existing_loan_amount=10000, occupation="SALARIED"
    )
    decision, _ = make_decision(score)
    assert score == 100
    assert decision == "APPROVED"


def test_low_score_gets_rejected():
    score = calculate_score(
        credit_score=600, monthly_income=20000, existing_loan_amount=300000, occupation="STUDENT"
    )
    decision, _ = make_decision(score)
    assert score == 10
    assert decision == "REJECTED"


def test_score_calculation_is_additive():
    # Only credit score and income pass; loan too high, non-salaried
    score = calculate_score(
        credit_score=750, monthly_income=60000, existing_loan_amount=250000, occupation="SELF_EMPLOYED"
    )
    assert score == 30 + 30 + 0 + 10  # = 70


@pytest.mark.asyncio
async def test_evaluate_endpoint_saves_decision_history(client):
    application_id = str(uuid.uuid4())

    response = await client.post(
        "/api/v1/decisions/evaluate",
        json={
            "application_id": application_id,
            "monthly_income": 80000,
            "credit_score": 750,
            "existing_loan_amount": 10000,
            "occupation": "SALARIED",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["application_id"] == application_id
    assert data["score"] == 100
    assert data["decision"] == "APPROVED"


@pytest.mark.asyncio
async def test_evaluate_endpoint_rejects_invalid_credit_score(client):
    response = await client.post(
        "/api/v1/decisions/evaluate",
        json={
            "application_id": str(uuid.uuid4()),
            "monthly_income": 80000,
            "credit_score": 950,
            "existing_loan_amount": 10000,
            "occupation": "SALARIED",
        },
    )
    assert response.status_code == 422
