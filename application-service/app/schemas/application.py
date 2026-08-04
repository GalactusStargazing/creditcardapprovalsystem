import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

CardType = Literal["SILVER", "GOLD", "PLATINUM"]
ApplicationStatus = Literal["SUBMITTED", "UNDER_REVIEW", "APPROVED", "REJECTED"]


class ApplicationCreateRequest(BaseModel):
    full_name: str
    date_of_birth: date
    pan_number: str = Field(min_length=10, max_length=10)
    mobile_number: str = Field(min_length=10, max_length=15)
    email: EmailStr
    address: str
    occupation: str
    employer: str | None = None
    monthly_income: Decimal = Field(gt=0)
    existing_loan_amount: Decimal = Field(ge=0)
    credit_score: int = Field(ge=300, le=900)
    card_type: CardType


class ApplicationResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    date_of_birth: date
    pan_number: str
    mobile_number: str
    email: EmailStr
    address: str
    occupation: str
    employer: str | None
    monthly_income: Decimal
    existing_loan_amount: Decimal
    credit_score: int
    card_type: CardType
    status: ApplicationStatus
    card_number: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationListItem(BaseModel):
    id: uuid.UUID
    card_type: CardType
    status: ApplicationStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationStatusResponse(BaseModel):
    application_id: uuid.UUID
    status: ApplicationStatus
