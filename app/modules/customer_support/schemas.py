import re
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator

# Known prompt injection and manipulation heuristics
INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|above|system)\s+instructions?", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(an?\s+)?(unrestricted|jailbreak|dan)", re.IGNORECASE),
    re.compile(r"system\s+prompt", re.IGNORECASE),
    re.compile(r"output\s+all\s+(api\s+keys?|passwords?|credentials?|secrets?)", re.IGNORECASE),
    re.compile(r"reveal\s+your\s+(instructions|system\s+message)", re.IGNORECASE),
    re.compile(r"bypass\s+(safety|policy|guardrails?)", re.IGNORECASE)
]

# Sensitive operations that mandate human approval
SENSITIVE_PATTERNS = [
    (re.compile(r"refund|chargeback|credit\s+my\s+account", re.IGNORECASE), "REFUND_REQUEST"),
    (re.compile(r"delete\s+my\s+account|erase\s+all\s+data|gdpr\s+deletion", re.IGNORECASE), "ACCOUNT_DELETION"),
    (re.compile(r"legal\s+action|lawsuit|attorney|sue\s+you", re.IGNORECASE), "LEGAL_RISK"),
    (re.compile(r"security\s+incident|breach|vulnerability|exploit", re.IGNORECASE), "SECURITY_INCIDENT"),
    (re.compile(r"urgent|outage|production\s+down|critical\s+failure", re.IGNORECASE), "CRITICAL_INCIDENT")
]

def sanitize_untrusted_input(text: str) -> tuple[str, List[str]]:
    """Sanitize untrusted customer text and flag security and prompt injection attempts."""
    detected_risks = []

    # Check for prompt injection
    for pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            detected_risks.append("PROMPT_INJECTION_ATTEMPT")
            break

    # Check for sensitive operations
    for pattern, risk_name in SENSITIVE_PATTERNS:
        if pattern.search(text):
            detected_risks.append(risk_name)

    # Sanitize: strip null bytes and escape system delimiters
    cleaned = text.replace("\x00", "").strip()
    return cleaned, list(set(detected_risks))

class EmailIngestRequest(BaseModel):
    """Incoming email message payload."""
    sender_email: EmailStr = Field(..., description="Sender's email address")
    sender_name: Optional[str] = Field(default=None, description="Sender's display name")
    subject: str = Field(..., min_length=2, max_length=255, description="Email subject line")
    body: str = Field(..., min_length=5, description="Full body text of the email message")
    thread_id: Optional[str] = Field(default=None, description="Email thread or conversation ID")

class TriageClassificationResult(BaseModel):
    """Schema-validated multi-task triage output."""
    intent: str = Field(..., description="BILLING, TECHNICAL, ACCOUNT_ACCESS, PRODUCT_ORDER, COMPLAINT, URGENT_INCIDENT, SPAM, UNKNOWN")
    urgency: str = Field(..., description="LOW, NORMAL, HIGH, CRITICAL")
    sentiment: str = Field(..., description="POSITIVE, NEUTRAL, NEGATIVE, FRUSTRATED")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    requires_human_approval: bool = Field(default=True)
    risk_flags: List[str] = Field(default_factory=list)
    draft_subject: str = Field(..., description="Subject for the proposed response draft")
    draft_body: str = Field(..., description="Safe, grounded response draft")
    grounded_sources: List[str] = Field(default_factory=list)
    missing_info: List[str] = Field(default_factory=list)

class EmailApprovalRequest(BaseModel):
    """Human approval action on an email draft."""
    action: str = Field(..., description="APPROVE_DRAFT, SEND_EMAIL, ESCALATE, or REJECT")
    approved_by: str = Field(..., min_length=2, description="Authorized operator name or email")
    custom_notes: Optional[str] = Field(default=None, description="Optional modifications or review remarks")

class SupportTicketResponse(BaseModel):
    """Response returned upon triaging an incoming support email."""
    success: bool
    ticket_id: str
    thread_id: Optional[str]
    intent: str
    urgency: str
    sentiment: str
    status: str
    requires_human_approval: bool
    risk_flags: List[str]
    draft_id: Optional[str]
    draft_subject: Optional[str]
    draft_body: Optional[str]
    grounded_sources: List[str]
    provider_draft_status: str
