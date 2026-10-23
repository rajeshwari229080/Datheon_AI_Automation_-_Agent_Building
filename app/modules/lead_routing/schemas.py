import re
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator

class LeadIntakeRequest(BaseModel):
    """Input payload for lead intake from web forms, webhooks, or external integrations."""
    name: str = Field(..., min_length=2, max_length=150, description="Full name of the prospect")
    email: EmailStr = Field(..., description="Corporate or business email address")
    phone: Optional[str] = Field(default=None, max_length=50, description="Contact phone number")
    company: str = Field(..., min_length=2, max_length=150, description="Company name")
    company_size: str = Field(..., description="Company size range: 1-10, 11-50, 51-200, 201-1000, 1000+")
    budget: Optional[float] = Field(default=0.0, ge=0.0, description="Estimated budget in USD")
    budget_range: Optional[str] = Field(default=None, description="Descriptive budget tier (e.g. '$10k-$25k')")
    business_need: str = Field(..., min_length=10, description="Description of the business problem or requirement")
    product_interest: Optional[str] = Field(default="Enterprise AI Automation Suite", description="Product or service of interest")
    consent: bool = Field(..., description="Consent for data processing and contact")
    idempotency_key: Optional[str] = Field(default=None, description="Client-provided idempotency key")

    @field_validator("consent")
    @classmethod
    def validate_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Data processing consent is required to submit a lead.")
        return v

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        cleaned = re.sub(r"[^\d+extEXT\-\s\(\)]", "", v).strip()
        if len(cleaned) < 6:
            raise ValueError("Phone number must have at least 6 digits if provided.")
        return cleaned

class LeadQualificationResult(BaseModel):
    """Schema-validated qualification output from the AI and deterministic rule engine."""
    lead_summary: str = Field(..., description="Concise summary of the lead profile")
    budget_suitability: str = Field(..., description="SUITABLE, MARGINAL, or INSUFFICIENT")
    company_size_suitability: str = Field(..., description="ENTERPRISE, MID_MARKET, SMB, or UNQUALIFIED")
    business_need: str = Field(..., description="Structured breakdown of requirements")
    lead_score: int = Field(..., ge=0, le=100, description="Overall qualification score (0-100)")
    recommended_priority: str = Field(..., description="HIGH, MEDIUM, or LOW")
    talking_points: List[str] = Field(default_factory=list, description="Personalized talking points for sales outreach")
    missing_info: List[str] = Field(default_factory=list, description="List of missing data points to clarify")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence metric")

class LeadResponse(BaseModel):
    """Standardized API response for processed leads."""
    success: bool
    lead_id: str
    qualification_status: str
    score: int
    priority: str
    latency_ms: int
    airtable_status: str
    slack_status: str
    summary: str
    talking_points: List[str]
    is_duplicate: bool = False
    message: Optional[str] = None
