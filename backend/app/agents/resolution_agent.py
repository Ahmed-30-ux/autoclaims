import json
from . import BaseAgent
from app.config import settings


SYSTEM_PROMPT = """You are a Resolution Agent for an insurance claims processing system.
Your job is to generate the final resolution documents for a claim.

Given the full claim lifecycle data, generate:
1. resolution_type: "approval" or "rejection"
2. subject: Email subject line for the resolution notice
3. greeting: Greeting for the claimant
4. body: The main resolution letter body text explaining the decision
5. amount_details: Summary of approved amount, deductible, net payout (if approved)
6. next_steps: What the claimant should do next
7. closing: Professional closing statement
8. reference_number: The claim reference number

The letter should be professional, empathetic, and clear.
Output as JSON with these exact field names."""


class ResolutionAgent(BaseAgent):
    name = "resolution"
    model = settings.qwen_model_flash

    def __init__(self):
        super().__init__()
        self.system_prompt = SYSTEM_PROMPT

    def build_messages(self, context: dict) -> list[dict]:
        claim = context.get("claim", {})
        assessment = context.get("assessment", {})
        review = context.get("review", {})

        human_review = context.get("human_review", {})
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Claim: {json.dumps(claim, indent=2, default=str)}\n\nAssessment: {json.dumps(assessment, indent=2, default=str)}\n\nReview Gate Decision: {json.dumps(review, indent=2, default=str)}\n\nHuman Review: {json.dumps(human_review, indent=2, default=str)}"},
        ]
