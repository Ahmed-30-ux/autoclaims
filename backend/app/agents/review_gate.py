import json
from . import BaseAgent
from app.config import settings


SYSTEM_PROMPT = """You are a Review Gate Agent for an insurance claims processing system.
Your job is to evaluate whether a claim needs human review or can be auto-approved.

Given the claim assessment and validation data, decide:
1. needs_human_review: Whether this requires human intervention (boolean)
2. auto_approve: Whether this can be auto-approved (boolean)
3. review_priority: "low", "medium", "high", "urgent"
4. review_reason: Why human review is needed (if applicable)
5. suggested_action: What you recommend the human reviewer decides
6. confidence: Your confidence in this decision (0.0-1.0)
7. flags: Any specific flags or concerns

Triggers for human review:
- Estimated payout > $5,000
- High fraud risk score (>0.7)
- Policy coverage questions
- Incomplete documentation
- First-time claimant with high value
- Claim near policy start/end dates

Output as JSON with these exact field names."""


class ReviewGateAgent(BaseAgent):
    name = "review_gate"
    model = settings.qwen_model_max

    def __init__(self):
        super().__init__()
        self.system_prompt = SYSTEM_PROMPT

    def build_messages(self, context: dict) -> list[dict]:
        claim = context.get("claim", {})
        assessment = context.get("assessment", {})
        validation = context.get("validation", {})
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Claim: {json.dumps(claim, indent=2, default=str)}\n\nValidation: {json.dumps(validation, indent=2, default=str)}\n\nAssessment: {json.dumps(assessment, indent=2, default=str)}"},
        ]
