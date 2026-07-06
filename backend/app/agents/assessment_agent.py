import json
from . import BaseAgent
from app.config import settings


SYSTEM_PROMPT = """You are an Assessment Agent for an insurance claims processing system.
Your job is to evaluate a validated claim and determine an appropriate payout.

Given the claim details, policy information, and validation results:
1. severity: Severity level ("low", "medium", "high", "critical")
2. estimated_payout: Recommended payout amount in dollars
3. deductible_applied: The deductible to subtract
4. net_payout: Final payout after deductible (estimated_payout - deductible, floored at 0)
5. fraud_risk_score: 0.0-1.0 likelihood of fraud
6. fraud_risk_factors: List of factors indicating potential fraud
7. assessment_confidence: 0.0-1.0 confidence in your assessment
8. requires_human_review: Whether this needs human review (boolean)
9. review_reason: Why human review is needed (if applicable)
10. recommended_action: "approve", "flag_for_review", or "reject"
11. notes: Detailed assessment notes

Flags that should trigger human review:
- Estimated payout > $5,000
- High fraud risk score (>0.7)
- Incomplete or conflicting information
- Unusual claim patterns
- Policy just recently started

Be thorough and conservative. Output as JSON."""


class AssessmentAgent(BaseAgent):
    name = "assessment"
    model = settings.qwen_model_max

    def __init__(self):
        super().__init__()
        self.system_prompt = SYSTEM_PROMPT

    def build_messages(self, context: dict) -> list[dict]:
        claim = context.get("claim", {})
        policy = context.get("policy", {})
        validation = context.get("validation", {})
        intake = context.get("intake", {})
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Claim: {json.dumps(claim, indent=2, default=str)}\n\nPolicy: {json.dumps(policy, indent=2, default=str)}\n\nIntake: {json.dumps(intake, indent=2, default=str)}\n\nValidation: {json.dumps(validation, indent=2, default=str)}"},
        ]
