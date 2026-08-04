CREDIT_SCORE_THRESHOLD = 700
INCOME_THRESHOLD = 50000
LOAN_THRESHOLD = 200000

APPROVAL_CUTOFF = 80


def calculate_score(
    credit_score: int,
    monthly_income: float,
    existing_loan_amount: float,
    occupation: str,
) -> int:
    score = 0

    # Rule 1: Credit score
    if credit_score >= CREDIT_SCORE_THRESHOLD:
        score += 30

    # Rule 2: Monthly income
    if monthly_income >= INCOME_THRESHOLD:
        score += 30

    # Rule 3: Existing loan amount
    if existing_loan_amount < LOAN_THRESHOLD:
        score += 20

    # Rule 4: Employment type
    if occupation == "SALARIED":
        score += 20
    else:
        score += 10

    return score


def make_decision(score: int) -> tuple[str, str]:
    """
    Returns (decision, reason) based on the calculated score.
    """
    if score >= APPROVAL_CUTOFF:
        return "APPROVED", "Applicant meets the required eligibility criteria."
    return "REJECTED", "Applicant did not meet the minimum eligibility score."
