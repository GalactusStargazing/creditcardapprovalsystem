import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Identifies the customer who submitted this application.
    # This is NOT a foreign key - Auth Service owns user data, and
    # Application Service must never directly reference auth_db.
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    pan_number: Mapped[str] = mapped_column(String(20), nullable=False)
    mobile_number: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    occupation: Mapped[str] = mapped_column(String(100), nullable=False)
    employer: Mapped[str] = mapped_column(String(255), nullable=True)

    monthly_income: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    existing_loan_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    credit_score: Mapped[int] = mapped_column(nullable=False)

    card_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="SUBMITTED")
    card_number: Mapped[str | None] = mapped_column(String(15), nullable=True, unique=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
