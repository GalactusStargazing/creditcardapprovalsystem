from app.repositories.decision_repository import DecisionRepository
from app.schemas.decision import DecisionEvaluateRequest, DecisionResponse
from app.services.scoring import calculate_score, make_decision


class DecisionService:
    def __init__(self, repo: DecisionRepository):
        self.repo = repo

    async def evaluate(self, data: DecisionEvaluateRequest) -> DecisionResponse:
        score = calculate_score(
            credit_score=data.credit_score,
            monthly_income=data.monthly_income,
            existing_loan_amount=data.existing_loan_amount,
            occupation=data.occupation,
        )
        decision, reason = make_decision(score)

        await self.repo.save(
            application_id=data.application_id,
            score=score,
            decision=decision,
            reason=reason,
        )

        return DecisionResponse(
            application_id=data.application_id,
            score=score,
            decision=decision,
            reason=reason,
        )
