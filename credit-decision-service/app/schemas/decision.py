import uuid
from typing import Literal

from pydantic import BaseModel, Field

Occupation = Literal["SALARIED", "SELF_EMPLOYED", "STUDENT"]
DecisionResult = Literal["APPROVED", "REJECTED"]


class DecisionEvaluateRequest(BaseModel):
    application_id: uuid.UUID
    monthly_income: float = Field(gt=0)
    credit_score: int = Field(ge=300, le=900)
    existing_loan_amount: float = Field(ge=0)
    occupation: Occupation


class DecisionResponse(BaseModel):
    application_id: uuid.UUID
    score: int
    decision: DecisionResult
    reason: str
