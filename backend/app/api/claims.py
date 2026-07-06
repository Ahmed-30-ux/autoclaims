import json
import os
import uuid
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.db import save_claim, get_claim, get_all_claims, update_claim, get_pending_reviews, update_human_review
from app.models.claim import ClaimCreate, ClaimResponse, ClaimStatus, ClaimListResponse
from app.agents.orchestrator import AgentOrchestrator

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/api/claims", tags=["claims"])
orchestrator = AgentOrchestrator()


def claim_to_response(c: dict) -> ClaimResponse:
    pipeline_stages = ["intake", "validation", "assessment", "review_gate", "resolution"]
    stage_index = pipeline_stages.index(c.get("current_agent", "intake")) if c.get("current_agent") in pipeline_stages else 0
    progress = (stage_index + 1) / len(pipeline_stages) * 100 if c.get("status") != "resolved" else 100.0

    def safe_json(val):
        if val is None:
            return None
        if isinstance(val, dict):
            return val
        if isinstance(val, str):
            try:
                return json.loads(val)
            except (json.JSONDecodeError, TypeError):
                return None
        return None

    img_paths = c.get("image_paths", "[]")
    if isinstance(img_paths, str):
        try:
            img_paths = json.loads(img_paths)
        except (json.JSONDecodeError, TypeError):
            img_paths = []
    elif not isinstance(img_paths, list):
        img_paths = []

    return ClaimResponse(
        id=c["id"],
        status=c.get("status", ClaimStatus.SUBMITTED),
        claimant_name=c.get("claimant_name", ""),
        claim_type=c.get("claim_type", "other"),
        description=c.get("description", ""),
        policy_number=c.get("policy_number", ""),
        created_at=c.get("created_at", ""),
        updated_at=c.get("updated_at", ""),
        pipeline_progress=progress,
        current_agent=c.get("current_agent", "intake"),
        image_paths=img_paths,
        intake_data=safe_json(c.get("intake_data")),
        validation_data=safe_json(c.get("validation_data")),
        assessment_data=safe_json(c.get("assessment_data")),
        review_gate_data=safe_json(c.get("review_gate_data")),
        resolution_data=safe_json(c.get("resolution_data")),
    )


@router.post("")
async def create_claim(claim: ClaimCreate):
    data = claim.model_dump()
    data["status"] = "submitted"
    data["current_agent"] = "intake"
    data["image_paths"] = "[]"
    claim_id = save_claim(data)
    return {"claim_id": claim_id, "status": "submitted", "message": "Claim submitted successfully"}


@router.post("/with-photos")
async def create_claim_with_photos(
    claimant_name: str = Form(...),
    claimant_email: str = Form(...),
    claimant_phone: str = Form(""),
    policy_number: str = Form(...),
    claim_type: str = Form(...),
    description: str = Form(...),
    incident_date: str = Form(...),
    location: str = Form(""),
    estimated_loss: str = Form(""),
    photos: list[UploadFile] = File(default=[]),
):
    saved_paths = []
    for photo in photos:
        ext = os.path.splitext(photo.filename or "photo.jpg")[1] or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        content = await photo.read()
        with open(filepath, "wb") as f:
            f.write(content)
        saved_paths.append(f"/uploads/{filename}")

    data = {
        "claimant_name": claimant_name,
        "claimant_email": claimant_email,
        "claimant_phone": claimant_phone,
        "policy_number": policy_number,
        "claim_type": claim_type,
        "description": description,
        "incident_date": incident_date,
        "location": location,
        "estimated_loss": float(estimated_loss) if estimated_loss else None,
        "image_paths": json.dumps(saved_paths),
        "status": "submitted",
        "current_agent": "intake",
    }
    claim_id = save_claim(data)
    return {
        "claim_id": claim_id,
        "status": "submitted",
        "photos_saved": len(saved_paths),
        "message": "Claim submitted successfully with photos",
    }


@router.get("/uploads/{filename}")
async def serve_upload(filename: str):
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    from fastapi.responses import FileResponse
    return FileResponse(filepath, media_type="image/jpeg")


@router.get("")
async def list_claims():
    claims = get_all_claims()
    responses = [claim_to_response(c) for c in claims]
    return ClaimListResponse(claims=responses, total=len(responses))


@router.get("/{claim_id}")
async def get_claim_detail(claim_id: int):
    claim = get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim_to_response(claim)


@router.post("/{claim_id}/process")
async def process_claim(claim_id: int):
    claim = get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    try:
        result = await orchestrator.process_claim(claim_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reviews/pending")
async def get_pending_reviews_endpoint():
    reviews = get_pending_reviews()
    return {"reviews": reviews, "total": len(reviews)}


@router.post("/{claim_id}/review")
async def resolve_human_review(claim_id: int, decision: dict):
    claim = get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    review_id = decision.get("review_id")
    status = decision.get("status", "approved")
    notes = decision.get("notes", "")
    reviewer = decision.get("reviewer", "human_operator")

    if review_id:
        update_human_review(review_id, status, notes, reviewer)

    review_decision = {
        "status": status,
        "notes": notes,
        "reviewer": reviewer,
        "reviewed_at": decision.get("reviewed_at", ""),
    }
    update_claim(claim_id, {"review_gate_data": json.dumps(review_decision)})

    try:
        result = await orchestrator.resolve_review(claim_id, review_decision)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
