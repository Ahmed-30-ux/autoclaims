import json
from . import BaseAgent
from app.config import settings


SYSTEM_PROMPT = """You are a Validation Agent for an insurance claims processing system.
Your job is to validate a claim against the policy holder's policy details.

Given the claim data and policy information, determine:
1. policy_valid: Whether the policy number exists and is active (boolean)
2. policy_match: Whether the claimant name matches the policy holder (boolean)
3. coverage_valid: Whether the claim type is covered by the policy (boolean)
4. policy_active: Whether the policy is within its effective dates (boolean)
5. deductible: The deductible amount from the policy
6. coverage_limit: The coverage limit for this claim type
7. issues: List of any issues found
8. validation_status: One of: "valid", "partial", "invalid"
9. recommended_action: What to do next ("proceed", "flag_for_review", "reject")
10. notes: Additional notes for the underwriter

Consider the policy details:
- Policy holder name should match the claimant
- Policy must be active (within start/end dates)
- Claim type should be covered by the policy type
- Estimated loss should be within coverage limits

Output as JSON with these exact field names."""


class ValidationAgent(BaseAgent):
    name = "validation"
    model = settings.qwen_model_max

    def __init__(self):
        super().__init__()
        self.system_prompt = SYSTEM_PROMPT

    def build_messages(self, context: dict) -> list[dict]:
        claim = context.get("claim", {})
        policy = context.get("policy", {})
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Claim Data:\n{json.dumps(claim, indent=2, default=str)}\n\nPolicy Data:\n{json.dumps(policy, indent=2, default=str)}"},
        ]
