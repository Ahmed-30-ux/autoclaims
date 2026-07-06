import requests

r = requests.get('http://localhost:8000/api/claims/4')
c = r.json()

print(f'Claim #{c["id"]}: {c["claimant_name"]}')
print(f'Status: {c["status"]}')
print(f'Progress: {c["pipeline_progress"]}%')
print(f'Agent: {c["current_agent"]}')

if c.get('intake_data'):
    print(f'Intake confidence: {c["intake_data"].get("confidence")}')
if c.get('validation_data'):
    print(f'Validation: {c["validation_data"].get("validation_status")}')
if c.get('assessment_data'):
    print(f'Estimated payout: ${c["assessment_data"].get("estimated_payout")}')
    print(f'Fraud risk: {c["assessment_data"].get("fraud_risk_score")}')
if c.get('resolution_data'):
    print(f'Resolution: {c["resolution_data"].get("resolution_type")}')
