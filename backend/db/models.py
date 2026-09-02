from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
import enum

Base = declarative_base()

class CaseStatus(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    PENDING_HUMAN = "pending_human"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

class Verdict(str, enum.Enum):
    FRAUD = "fraud"
    LEGITIMATE = "legitimate"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"

class Case(Base):
    __tablename__ = "cases"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(Enum(CaseStatus), default=CaseStatus.OPEN)
    chargeback_amount = Column(Float, nullable=False)
    chargeback_reason = Column(String(255))
    transaction_id = Column(String(100), nullable=False)
    verdict = Column(Enum(Verdict), nullable=True)
    confidence = Column(Float, nullable=True)
    requires_human = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    evidence_package = Column(JSONB, nullable=True)
    audit_trail = relationship("AuditLog", back_populates="case")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(String(100), primary_key=True)
    customer_id = Column(String(100), nullable=False)
    merchant_id = Column(String(100), nullable=False)
    device_id = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    status = Column(String(50))
    payment_method = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata_ = Column(JSONB, nullable=True)

class Customer(Base):
    __tablename__ = "customers"
    id = Column(String(100), primary_key=True)
    email = Column(String(255))
    account_age_days = Column(Integer)
    total_transactions = Column(Integer, default=0)
    total_chargebacks = Column(Integer, default=0)
    chargeback_rate = Column(Float, default=0.0)
    is_flagged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Device(Base):
    __tablename__ = "devices"
    id = Column(String(100), primary_key=True)
    fingerprint = Column(String(255))
    ip_address = Column(String(50))
    user_agent = Column(Text)
    accounts_linked = Column(Integer, default=1)
    is_flagged = Column(Boolean, default=False)

class Merchant(Base):
    __tablename__ = "merchants"
    id = Column(String(100), primary_key=True)
    name = Column(String(255))
    category = Column(String(100))
    chargeback_rate = Column(Float, default=0.0)
    auto_refund_limit = Column(Float, default=10000.0)
    policy_notes = Column(Text, nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"))
    agent = Column(String(100))
    action = Column(String(255))
    payload = Column(JSONB)
    timestamp = Column(DateTime, default=datetime.utcnow)
    case = relationship("Case", back_populates="audit_trail")

class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"))
    evidence_type = Column(String(100))
    content = Column(Text)
    source = Column(String(100))
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)