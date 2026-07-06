"""Test the full pipeline with mocked Qwen API responses."""
import os, sys, json, asyncio
sys.path.insert(0, os.path.dirname(__file__))
os.environ["QWEN_API_KEY"] = "test-key"

from unittest.mock import patch
from app.db import init_db, save_claim, get_claim
from app.agents.orchestrator import AgentOrchestrator

init_db()

# Create a test claim
claim_id = save_claim({
    "claimant_name": "Alice Johnson",
    "claimant_email": "alice@email.com",
    "claimant_phone": "+1-555-0001",
    "policy_number": "POL-2026-001",
    "claim_type": "auto",
    "description": "My car was rear-ended at a stoplight. The other driver admitted fault. Damage to rear bumper.",
    "incident_date": "2026-07-01",
    "location": "New York, NY",
    "estimated_loss": 3500.0,
    "status": "submitted",
    "current_agent": "intake",
})

print(f"Test claim created: {claim_id}")

# Mock responses for each agent
mock_responses = {
    "intake": {
        "claimant_name": "Alice Johnson",
        "claimant_email": "alice@email.com",
        "claimant_phone": "+1-555-0001",
        "policy_number": "POL-2026-001",
        "claim_type": "auto",
        "description": "Vehicle rear-ended at stoplight, other driver at fault. Damage to rear bumper.",
        "incident_date": "2026-07-01",
        "location": "New York, NY",
        "estimated_loss": 3500.0,
        "confidence": 0.95,
        "missing_fields": [],
        "flags": [],
    },
    "validation": {
        "policy_valid": True,
        "policy_match": True,
        "coverage_valid": True,
        "policy_active": True,
        "deductible": 500.0,
        "coverage_limit": 50000.0,
        "issues": [],
        "validation_status": "valid",
        "recommended_action": "proceed",
        "notes": "Policy is active and covers this claim type.",
    },
    "assessment": {
        "severity": "medium",
        "estimated_payout": 2500.0,
        "deductible_applied": 500.0,
        "net_payout": 2000.0,
        "fraud_risk_score": 0.1,
        "fraud_risk_factors": [],
        "assessment_confidence": 0.9,
        "requires_human_review": False,
        "review_reason": None,
        "recommended_action": "approve",
        "notes": "Standard rear-end collision. Damage consistent with reported incident.",
    },
    "review_gate": {
        "needs_human_review": False,
        "auto_approve": True,
        "review_priority": "low",
        "review_reason": None,
        "suggested_action": "approve",
        "confidence": 0.95,
        "flags": [],
    },
    "resolution": {
        "resolution_type": "approval",
        "subject": "Claim #1 - Claim Approved",
        "greeting": "Dear Alice Johnson,",
        "body": "We have reviewed your claim and are pleased to inform you that it has been approved.",
        "amount_details": "Approved Amount: $2,500.00, Deductible: $500.00, Net Payout: $2,000.00",
        "next_steps": "The payout will be processed within 5-7 business days.",
        "closing": "Sincerely, AutoClaims Processing Team",
        "reference_number": "CLM-2026-0001",
    },
}


async def run_test():
    orchestrator = AgentOrchestrator()

    # Mock the run method for all agents
    for agent_name, agent in orchestrator.pipeline:
        original_run = agent.run

        async def mocked_run(context, name=agent_name):
            print(f"  Agent '{name}' running (mocked)...")
            return mock_responses[name]

        agent.run = mocked_run

    print("\nRunning pipeline...")
    result = await orchestrator.process_claim(claim_id)
    print(f"\nPipeline result status: {result['status']}")

    claim = get_claim(claim_id)
    print(f"Final claim status: {claim['status']}")
    print(f"All agent data present: {all(claim.get(f'{a}_data') for a in ['intake', 'validation', 'assessment'])}")

    if result["status"] == "resolved":
        print("\n=== Pipeline test PASSED ===")
    else:
        print(f"\n=== Pipeline test: {result['status']} ===")


asyncio.run(run_test())
