from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr

class ProjectIntakeRequest(BaseModel):
    """Customer intake payload initializing a new enterprise project."""
    client_name: str = Field(..., min_length=2, description="Authorized client contact name")
    client_email: EmailStr = Field(..., description="Corporate email address")
    company: str = Field(..., min_length=2, description="Client enterprise entity")
    service_type: str = Field(default="Enterprise AI Automation Suite", description="Contracted service tier")
    deal_value: float = Field(..., gt=0.0, description="Agreed contract value in currency")
    currency: str = Field(default="USD", description="Currency ISO code")

class ContractDraftResponse(BaseModel):
    """Template-based contract draft."""
    contract_id: str
    project_id: str
    template_name: str
    clauses: List[str]
    missing_fields: List[str]
    draft_content: str
    is_approved: bool

class StripeWebhookResponse(BaseModel):
    """Deterministic Stripe webhook ingestion outcome."""
    success: bool
    event_id: str
    event_type: str
    verified: bool
    signature_valid: bool
    project_id: Optional[str] = None
    amount: float
    currency: str
    status: str
    message: str

class ExecutiveDigestResponse(BaseModel):
    """Weekly executive digest payload distinguishing measured facts from AI summaries."""
    digest_id: str
    reporting_period: str
    source_coverage: List[str]
    last_refresh_time: str
    factual_stats: Dict[str, Any]
    ai_narrative: str
    verified_revenue: float
    discrepancies_flagged: int

class ProjectStateTransitionRequest(BaseModel):
    """Explicit state machine transition authorization."""
    target_state: str = Field(..., description="Target state to transition towards")
    actor: str = Field(..., min_length=2, description="Authorized human operator")
    notes: Optional[str] = Field(default=None, description="Operational notes")
