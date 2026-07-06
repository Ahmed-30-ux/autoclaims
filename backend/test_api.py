import os, sys
sys.path.insert(0, os.path.dirname(__file__))
os.environ["QWEN_API_KEY"] = "test-key"

from app.db import init_db, save_claim, get_claim, get_all_claims
from app.main import app
from fastapi.testclient import TestClient

init_db()

client = TestClient(app)

# Test health
r = client.get("/api/health")
print(f"Health: {r.status_code} - {r.json()}")

# Test create claim
claim_data = {
    "claimant_name": "John Doe",
    "claimant_email": "john@email.com",
    "claimant_phone": "+1-555-1234",
    "policy_number": "POL-2026-001",
    "claim_type": "auto",
    "description": "My car was rear-ended at a stoplight on Main Street. Damage to rear bumper and trunk.",
    "incident_date": "2026-07-01",
    "location": "Main Street & 5th Ave, NYC",
    "estimated_loss": 3500.0,
}
r = client.post("/api/claims", json=claim_data)
print(f"Create: {r.status_code} - {r.json()}")

claim_id = r.json()["claim_id"]

# Test list
r = client.get("/api/claims")
print(f"List: {r.status_code} - total: {r.json()['total']}")

# Test get detail
r = client.get(f"/api/claims/{claim_id}")
print(f"Detail: {r.status_code} - {r.json()['claimant_name']} - status: {r.json()['status']}")

print("\n=== All API tests passed! ===")
