import logging

from app.repositories.decision_repository import DecisionRepository
from app.schemas.decision import DecisionEvaluateRequest, DecisionResponse
from app.services.scoring import calculate_score, make_decision

logger = logging.getLogger("decision-service")


class DecisionService:
    def __init__(self, repo: DecisionRepository):
        self.repo = repo

    async def evaluate(self, data: DecisionEvaluateRequest) -> DecisionResponse:
        try:
            score = calculate_score(
                credit_score=data.credit_score,
                monthly_income=data.monthly_income,
                existing_loan_amount=data.existing_loan_amount,
                occupation=data.occupation,
            )
            logger.info(f"Score calculated: application_id={data.application_id}, score={score}")

            decision, reason = make_decision(score)
            logger.info(
                f"Decision made: application_id={data.application_id}, "
                f"decision={decision}, reason={reason}"
            )

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
        except Exception as e:
            logger.error(
                f"Unexpected error evaluating application: application_id={data.application_id}, error={str(e)}",
                exc_info=True,
            )
            raise
