from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum
from datetime import datetime


class ClaimStatus(str, Enum):
    SUBMITTED = "submitted"
    INTAKE_COMPLETE = "intake_complete"
    ERROR = "error"
    VALIDATING = "validating"
    VALIDATED = "validated"
    ASSESSING = "assessing"
    ASSESSED = "assessed"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    RESOLVED = "resolved"


class ClaimType(str, Enum):
    AUTO = "auto"
    HOME = "home"
    HEALTH = "health"
    TRAVEL = "travel"
    PROPERTY = "property"
    LIABILITY = "liability"
    OTHER = "other"


class ClaimCreate(BaseModel):
    claimant_name: str
    claimant_email: str
    claimant_phone: Optional[str] = None
    policy_number: str
    claim_type: ClaimType
    description: str
    incident_date: str
    location: Optional[str] = None
    estimated_loss: Optional[float] = None


class ClaimInDB(ClaimCreate):
    id: int
    status: ClaimStatus = ClaimStatus.SUBMITTED
    created_at: str
    updated_at: str

    intake_data: Optional[dict] = None
    validation_data: Optional[dict] = None
    assessment_data: Optional[dict] = None
    review_gate_data: Optional[dict] = None
    resolution_data: Optional[dict] = None
    current_agent: str = "intake"


class ClaimResponse(BaseModel):
    id: int
    status: ClaimStatus
    claimant_name: str
    claim_type: ClaimType
    description: str
    policy_number: str
    created_at: str
    updated_at: str
    pipeline_progress: float = 0.0
    current_agent: str = "intake"
    image_paths: list[str] = []

    intake_data: Optional[dict] = None
    validation_data: Optional[dict] = None
    assessment_data: Optional[dict] = None
    review_gate_data: Optional[dict] = None
    resolution_data: Optional[dict] = None


class ClaimListResponse(BaseModel):
    claims: list[ClaimResponse]
    total: int
