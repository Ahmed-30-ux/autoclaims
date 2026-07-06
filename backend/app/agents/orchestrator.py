import json
import logging
from datetime import datetime

from app.db import get_claim, update_claim, get_policy, create_human_review
from app.agents.intake_agent import IntakeAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.assessment_agent import AssessmentAgent
from app.agents.review_gate import ReviewGateAgent
from app.agents.resolution_agent import ResolutionAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    def __init__(self):
        self.intake = IntakeAgent()
        self.validation = ValidationAgent()
        self.assessment = AssessmentAgent()
        self.review_gate = ReviewGateAgent()
        self.resolution = ResolutionAgent()

        self.pipeline = [
            ("intake", self.intake),
            ("validation", self.validation),
            ("assessment", self.assessment),
            ("review_gate", self.review_gate),
            ("resolution", self.resolution),
        ]

    async def process_claim(self, claim_id: int) -> dict:
        claim = get_claim(claim_id)
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")

        context = {"claim": claim}
        results = {}

        for agent_name, agent in self.pipeline:
            logger.info(f"Running agent: {agent_name} for claim {claim_id}")
            update_claim(claim_id, {"current_agent": agent_name, "status": self._status_for_agent(agent_name)})

            if agent_name == "validation":
                policy = get_policy(claim.get("policy_number", ""))
                context["policy"] = policy or {}

            try:
                result = await agent.run(context)
                results[agent_name] = result

                update_claim(claim_id, {f"{agent_name}_data": json.dumps(result)})
                context[f"{agent_name}_data"] = result

                if agent_name == "review_gate":
                    needs_review = result.get("needs_human_review", False)
                    if not needs_review:
                        context["human_review"] = {
                            "status": "auto_approved",
                            "reviewer": "system",
                            "notes": "Auto-approved based on assessment criteria",
                        }
                    else:
                        review_id = create_human_review(claim_id)
                        update_claim(claim_id, {
                            "status": "pending_review",
                            f"{agent_name}_data": json.dumps(result),
                        })
                        logger.info(f"Claim {claim_id} sent for human review (ID: {review_id})")
                        return {
                            "claim_id": claim_id,
                            "status": "pending_review",
                            "agent": agent_name,
                            "result": result,
                            "review_id": review_id,
                        }

            except Exception as e:
                logger.error(f"Agent {agent_name} failed for claim {claim_id}: {e}")
                update_claim(claim_id, {"status": "error"})
                raise

        update_claim(claim_id, {"status": "resolved", "current_agent": "completed"})
        return {
            "claim_id": claim_id,
            "status": "resolved",
            "agent": "completed",
            "result": results,
        }

    async def resolve_review(self, claim_id: int, review_decision: dict) -> dict:
        claim = get_claim(claim_id)
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")

        assessment_data = json.loads(claim.get("assessment_data") or "{}")
        review_gate_data = json.loads(claim.get("review_gate_data") or "{}")

        context = {
            "claim": claim,
            "assessment": assessment_data,
            "review": review_gate_data,
            "human_review": review_decision,
        }

        result = await self.resolution.run(context)
        update_claim(claim_id, {
            "status": "resolved",
            "current_agent": "completed",
            "resolution_data": json.dumps(result),
        })
        return {"claim_id": claim_id, "status": "resolved", "result": result}

    def _status_for_agent(self, agent_name: str) -> str:
        status_map = {
            "intake": "intake_complete",
            "validation": "validated",
            "assessment": "assessed",
            "review_gate": "assessed",
            "resolution": "resolved",
        }
        return status_map.get(agent_name, "processing")
