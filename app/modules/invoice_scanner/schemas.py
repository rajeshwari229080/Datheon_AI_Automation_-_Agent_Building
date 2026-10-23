from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class LineItemSchema(BaseModel):
    """Schema for individual invoice line items."""
    description: str = Field(..., min_length=1, description="Item or service description")
    quantity: float = Field(default=1.0, ge=0.0, description="Item quantity or hours billed")
    unit_price: float = Field(default=0.0, ge=0.0, description="Price per unit in currency")
    total_amount: float = Field(default=0.0, description="Total line amount (quantity * unit_price)")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

class InvoiceExtractionSchema(BaseModel):
    """Structured extraction format for OCR and Vision models."""
    vendor_name: Optional[str] = Field(default=None, description="Name of the billing vendor or supplier")
    invoice_number: Optional[str] = Field(default=None, description="Invoice or receipt reference number")
    invoice_date: Optional[str] = Field(default=None, description="Date of invoice issue (YYYY-MM-DD)")
    due_date: Optional[str] = Field(default=None, description="Payment due date")
    currency: str = Field(default="USD", description="Currency ISO code (USD, EUR, GBP, etc.)")
    subtotal: float = Field(default=0.0, description="Subtotal before taxes and discounts")
    tax_rate: float = Field(default=0.0, description="Tax rate percentage (e.g. 8.25 for 8.25%)")
    tax_amount: float = Field(default=0.0, description="Explicit tax amount stated on document")
    discount_amount: float = Field(default=0.0, description="Discount amount applied")
    total_amount: float = Field(default=0.0, description="Grand total stated on document")
    payment_status: Optional[str] = Field(default="UNPAID", description="Payment status: PAID, UNPAID, PARTIAL, DUE")
    line_items: List[LineItemSchema] = Field(default_factory=list, description="Extracted line items")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

class InvoiceValidationResult(BaseModel):
    """Integrity and arithmetic verification findings."""
    is_valid: bool
    status: str  # VALID, ARITHMETIC_MISMATCH, DUPLICATE, MISSING_FIELDS, MANUAL_REVIEW
    arithmetic_discrepancy: bool
    discrepancy_details: Dict[str, Any]
    is_duplicate: bool
    duplicate_of_id: Optional[str] = None
    calculated_subtotal: float
    calculated_total: float
    delta_subtotal: float
    delta_total: float

class InvoiceResponse(BaseModel):
    """Standardized API response for processed invoices."""
    success: bool
    invoice_id: str
    filename: str
    file_hash: str
    vendor_name: Optional[str]
    invoice_number: Optional[str]
    invoice_date: Optional[str]
    currency: str
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    validation_status: str
    arithmetic_discrepancy: bool
    is_duplicate: bool
    export_status: str
    line_items: List[LineItemSchema]
    discrepancy_details: Dict[str, Any] = {}

class LineItemUpdateRequest(BaseModel):
    """Schema for manual adjustments from the line-item editor screen."""
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    currency: Optional[str] = None
    subtotal: Optional[float] = None
    tax_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    total_amount: Optional[float] = None
    line_items: List[LineItemSchema] = Field(default_factory=list)
