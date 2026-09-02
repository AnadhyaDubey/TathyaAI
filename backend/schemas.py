from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID


class TransactionContext(BaseModel):
    transaction_id: str
    customer_id: str
    merchant_id: str
    device_id: str
    amount: float
    currency: str = "INR"
    payment_method: str
    created_at: datetime


class CustomerContext(BaseModel):
    customer_id: str
    account_age_days: int
    total_transactions: int
    total_chargebacks: int
    chargeback_rate: float
    is_flagged: bool


class DeviceContext(BaseModel):
    device_id: str
    accounts_linked: int
    is_flagged: bool
    ip_address: str


class CaseInput(BaseModel):
    """Full context bundle handed to the agent graph for one chargeback case."""
    case_id: UUID
    chargeback_amount: float
    chargeback_reason: str
    transaction: TransactionContext
    customer: CustomerContext
    device: DeviceContext


class HypothesisOutput(BaseModel):
    """Output of either the fraud or defense agent."""
    stance: Literal["fraud", "legitimate"]
    argument: str = Field(..., description="The case being made, citing specific signals")
    cited_signals: list[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)


class JudgeVerdict(BaseModel):
    """Final output of the judge agent — this is what gets written back to the Case row."""
    verdict: Literal["fraud", "legitimate", "insufficient_evidence"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    requires_human: bool
    key_factors: list[str] = Field(default_factory=list)