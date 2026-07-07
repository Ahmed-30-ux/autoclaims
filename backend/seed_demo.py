"""Seed the database with demo claims for the frontend dashboard."""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
os.environ["QWEN_API_KEY"] = "test"

from app.db import init_db, save_claim, get_all_claims, update_claim, create_human_review

DB_PATH = os.path.join(os.path.dirname(__file__), "autoclaims.db")
init_db()

existing = get_all_claims()
if len(existing) > 0:
    print(f"Database already has {len(existing)} claims, skipping seed.")
    sys.exit(0)

demo_claims = [
    # Submitted claims
    {
        "claimant_name": "Alice Johnson",
        "claimant_email": "alice@email.com",
        "claimant_phone": "+1-555-0001",
        "policy_number": "POL-2026-001",
        "claim_type": "auto",
        "description": "My car was rear-ended at a stoplight on Main Street. The other driver admitted fault. Damage to rear bumper and trunk.",
        "incident_date": "2026-07-01",
        "location": "New York, NY",
        "estimated_loss": 3500.0,
        "status": "submitted",
        "current_agent": "intake",
    },
    {
        "claimant_name": "Bob Smith",
        "claimant_email": "bob@email.com",
        "claimant_phone": "+1-555-0002",
        "policy_number": "POL-2026-002",
        "claim_type": "home",
        "description": "Water damage from burst pipe in the kitchen ceiling. Significant damage to cabinets and flooring.",
        "incident_date": "2026-06-28",
        "location": "Brooklyn, NY",
        "estimated_loss": 8500.0,
        "status": "submitted",
        "current_agent": "intake",
    },
    {
        "claimant_name": "Carol Davis",
        "claimant_email": "carol@email.com",
        "claimant_phone": "+1-555-0003",
        "policy_number": "POL-2026-003",
        "claim_type": "health",
        "description": "Emergency room visit for severe allergic reaction. Hospital bill attached.",
        "incident_date": "2026-06-25",
        "location": "Manhattan, NY",
        "estimated_loss": 12000.0,
        "status": "submitted",
        "current_agent": "intake",
    },
    # Resolved claims (pre-filled with agent data)
    {
        "claimant_name": "Daniel Lee",
        "claimant_email": "daniel@email.com",
        "claimant_phone": "+1-555-0004",
        "policy_number": "POL-2026-004",
        "claim_type": "travel",
        "description": "Lost luggage during connecting flight from JFK to London. Bag contained valuables worth $2,000.",
        "incident_date": "2026-06-20",
        "location": "JFK Airport, NY",
        "estimated_loss": 2000.0,
        "status": "resolved",
        "current_agent": "completed",
        "intake_data": json.dumps({"claimant_name": "Daniel Lee", "claim_type": "travel", "confidence": 0.97, "incident_date": "2026-06-20", "location": "JFK Airport, NY"}),
        "validation_data": json.dumps({"policy_valid": True, "coverage": "active", "confidence": 0.94, "policy_type": "travel"}),
        "assessment_data": json.dumps({"estimated_payout": 1800.0, "damage_severity": "moderate", "fraud_risk": "low", "confidence": 0.91}),
        "review_gate_data": json.dumps({"needs_human_review": False, "auto_approved": True, "confidence": 0.88}),
        "resolution_data": json.dumps({"outcome": "approved", "payout_amount": 1800.0, "deductible_applied": 100.0, "net_payout": 1700.0, "summary": "Claim approved for lost luggage."}),
    },
    {
        "claimant_name": "Eve Martinez",
        "claimant_email": "eve@email.com",
        "claimant_phone": "+1-555-0005",
        "policy_number": "POL-2026-005",
        "claim_type": "property",
        "description": "Storm damage to roof and exterior walls during heavy rain. Multiple tiles missing, water leaking into attic.",
        "incident_date": "2026-06-15",
        "location": "Staten Island, NY",
        "estimated_loss": 15000.0,
        "status": "resolved",
        "current_agent": "completed",
        "intake_data": json.dumps({"claimant_name": "Eve Martinez", "claim_type": "property", "confidence": 0.98, "incident_date": "2026-06-15", "location": "Staten Island, NY"}),
        "validation_data": json.dumps({"policy_valid": True, "coverage": "active", "confidence": 0.96, "policy_type": "property"}),
        "assessment_data": json.dumps({"estimated_payout": 12000.0, "damage_severity": "severe", "fraud_risk": "low", "confidence": 0.93}),
        "review_gate_data": json.dumps({"needs_human_review": False, "auto_approved": True, "confidence": 0.90}),
        "resolution_data": json.dumps({"outcome": "approved", "payout_amount": 12000.0, "deductible_applied": 1500.0, "net_payout": 10500.0, "summary": "Claim approved for storm damage repair."}),
    },
    # Pending review claim
    {
        "claimant_name": "Frank Wilson",
        "claimant_email": "frank@email.com",
        "claimant_phone": "+1-555-0006",
        "policy_number": "POL-2026-006",
        "claim_type": "liability",
        "description": "Third-party injury claim from customer slipping on wet floor at retail location. Medical bills totaling $25,000.",
        "incident_date": "2026-06-10",
        "location": "Manhattan, NY",
        "estimated_loss": 25000.0,
        "status": "pending_review",
        "current_agent": "review_gate",
        "intake_data": json.dumps({"claimant_name": "Frank Wilson", "claim_type": "liability", "confidence": 0.95, "incident_date": "2026-06-10", "location": "Manhattan, NY"}),
        "validation_data": json.dumps({"policy_valid": True, "coverage": "active", "confidence": 0.93, "policy_type": "liability"}),
        "assessment_data": json.dumps({"estimated_payout": 25000.0, "damage_severity": "severe", "fraud_risk": "medium", "confidence": 0.85}),
        "review_gate_data": json.dumps({"needs_human_review": True, "reason": "High payout amount exceeds $5,000 threshold", "confidence": 0.82}),
    },
    # Rejected claim
    {
        "claimant_name": "Grace Kim",
        "claimant_email": "grace@email.com",
        "claimant_phone": "+1-555-0007",
        "policy_number": "POL-2026-001",
        "claim_type": "auto",
        "description": "Claim for pre-existing damage to front bumper. No new incident reported.",
        "incident_date": "2026-06-05",
        "location": "Queens, NY",
        "estimated_loss": 1500.0,
        "status": "resolved",
        "current_agent": "completed",
        "intake_data": json.dumps({"claimant_name": "Grace Kim", "claim_type": "auto", "confidence": 0.90, "incident_date": "2026-06-05", "location": "Queens, NY"}),
        "validation_data": json.dumps({"policy_valid": True, "coverage": "active", "confidence": 0.95, "policy_type": "auto"}),
        "assessment_data": json.dumps({"estimated_payout": 0.0, "damage_severity": "minor", "fraud_risk": "high", "confidence": 0.78, "fraud_flags": "Pre-existing damage, no new incident"}),
        "review_gate_data": json.dumps({"needs_human_review": False, "auto_approved": False, "reason": "High fraud risk flagged by assessment", "confidence": 0.85}),
        "resolution_data": json.dumps({"outcome": "rejected", "payout_amount": 0.0, "deductible_applied": 0.0, "net_payout": 0.0, "summary": "Claim rejected: pre-existing damage with no new incident."}),
    },
    # Fresh auto claim
    {
        "claimant_name": "Henry Nakamura",
        "claimant_email": "henry@email.com",
        "claimant_phone": "+1-555-0008",
        "policy_number": "POL-2026-001",
        "claim_type": "auto",
        "description": "Hit a deer on the highway. Front grille, headlight, and hood damaged. Car is drivable but needs repair.",
        "incident_date": "2026-07-03",
        "location": "Albany, NY",
        "estimated_loss": 4500.0,
        "status": "submitted",
        "current_agent": "intake",
    },
    # Home claim in progress
    {
        "claimant_name": "Isabella Ortiz",
        "claimant_email": "isabella@email.com",
        "claimant_phone": "+1-555-0009",
        "policy_number": "POL-2026-002",
        "claim_type": "home",
        "description": "Basement flooded due to heavy rainfall. Water damage to carpet, drywall, and stored belongings.",
        "incident_date": "2026-07-02",
        "location": "Bronx, NY",
        "estimated_loss": 7500.0,
        "image_paths": "[]",
        "status": "submitted",
        "current_agent": "intake",
    },
    # Fully rejected claim
    {
        "claimant_name": "James Brown",
        "claimant_email": "james@email.com",
        "claimant_phone": "+1-555-0010",
        "policy_number": "POL-2026-004",
        "claim_type": "travel",
        "description": "Claim for lost Rolex watch valued at $50,000 during domestic flight. No proof of purchase or police report provided. Incident reported 3 weeks after travel ended.",
        "incident_date": "2026-06-01",
        "location": "Los Angeles, CA",
        "estimated_loss": 50000.0,
        "image_paths": "[]",
        "status": "rejected",
        "current_agent": "completed",
        "intake_data": json.dumps({"claimant_name": "James Brown", "claim_type": "travel", "confidence": 0.72, "incident_date": "2026-06-01", "location": "Los Angeles, CA", "flags": "delayed_reporting, high_value, no_police_report"}),
        "validation_data": json.dumps({"policy_valid": True, "coverage": "limited", "confidence": 0.65, "policy_type": "travel", "max_item_coverage": 500, "warnings": "Single-item value far exceeds policy limit of $500"}),
        "assessment_data": json.dumps({"estimated_payout": 0.0, "damage_severity": "n/a", "fraud_risk": "high", "confidence": 0.95, "fraud_flags": "Delayed reporting (21 days), no police report, no proof of purchase, item value 100x policy limit, inconsistent travel dates"}),
        "review_gate_data": json.dumps({"needs_human_review": True, "reason": "High fraud risk + delayed reporting + excessive claim amount", "auto_recommendation": "reject", "confidence": 0.93}),
        "resolution_data": json.dumps({"outcome": "rejected", "payout_amount": 0.0, "deductible_applied": 0.0, "net_payout": 0.0, "summary": "Claim rejected: fraudulent pattern detected — delayed reporting, no police report, no proof of purchase, and claim amount exceeds policy limits by 100x."}),
    },
]

for c in demo_claims:
    cid = save_claim(c)
    print(f"Created demo claim #{cid}: {c['claimant_name']} - {c['claim_type']} [{c['status']}]")

    # Save agent data fields (save_claim only stores base fields)
    agent_fields = ["intake_data", "validation_data", "assessment_data", "review_gate_data", "resolution_data"]
    agent_data = {}
    for f in agent_fields:
        val = c.get(f)
        if val is not None:
            agent_data[f] = json.loads(val) if isinstance(val, str) else val
    if agent_data:
        update_claim(cid, agent_data)
        print(f"  -> Saved agent data: {', '.join(agent_data.keys())}")

    # If pending_review, create human review record
    if c["status"] == "pending_review":
        rid = create_human_review(cid)
        print(f"  -> Created human review #{rid} for claim #{cid}")

print(f"\nTotal claims: {len(get_all_claims())}")
print("Demo data seeded successfully!")
