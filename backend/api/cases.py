from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from db.models import Case, CaseStatus, Verdict, AuditLog
from schemas import CaseInput, TransactionContext, CustomerContext, DeviceContext
from services.investigation import investigate, load_case_input_from_db

router = APIRouter(prefix="/api/cases", tags=["cases"])


DEMO_DEFAULTS = dict(
    transaction=dict(
        transaction_id="txn_demo", customer_id="cust_demo",
        merchant_id="merch_demo", device_id="dev_demo",
        amount=8000.0, payment_method="upi",
    ),
    customer=dict(
        customer_id="cust_demo", account_age_days=200,
        total_transactions=30, total_chargebacks=0,
        chargeback_rate=0.0, is_flagged=False,
    ),
    device=dict(
        device_id="dev_demo", accounts_linked=1,
        is_flagged=False, ip_address="203.0.113.5",
    ),
)


class AdhocCaseRequest(BaseModel):
    chargeback_amount: float
    chargeback_reason: str
    transaction: Optional[dict] = None
    customer: Optional[dict] = None
    device: Optional[dict] = None


class ApproveRequest(BaseModel):
    decision: Optional[str] = None


async def _persist_result(session: AsyncSession, case_row: Case, trace: dict):
    case_row.verdict = Verdict(trace["final_verdict"])
    case_row.confidence = trace["judge_verdict"]["confidence"]
    case_row.requires_human = trace["final_requires_human"]
    case_row.evidence_package = trace
    case_row.status = CaseStatus.PENDING_HUMAN if trace["final_requires_human"] else CaseStatus.RESOLVED
    if not trace["final_requires_human"]:
        case_row.resolved_at = datetime.utcnow()  # naive — matches DB column type

    for agent_name, key in [
        ("injection_guard", "layer1_injection_guard"),
        ("fraud_agent", "fraud_hypothesis"),
        ("defense_agent", "defense_hypothesis"),
        ("judge", "judge_verdict"),
        ("policy_engine", "policy_decision"),
        ("evidence_guard", "evidence_guard"),
    ]:
        session.add(AuditLog(case_id=case_row.id, agent=agent_name, action="investigate", payload=trace[key]))

    await session.commit()


# ── STATIC ROUTES FIRST — must come before any "/{case_id}..." pattern ──

@router.get("")
async def list_cases(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Case).order_by(Case.created_at.desc()).limit(100))
    cases = result.scalars().all()
    return [
        {
            "case_id": str(c.id),
            "status": c.status,
            "chargeback_amount": c.chargeback_amount,
            "chargeback_reason": c.chargeback_reason,
            "verdict": c.verdict,
            "confidence": c.confidence,
            "requires_human": c.requires_human,
            "created_at": c.created_at,
        }
        for c in cases
    ]


@router.post("/adhoc/investigate")
async def investigate_adhoc_case(payload: AdhocCaseRequest, db: AsyncSession = Depends(get_db)):
    """
    For live demo / red-team testing: submit a custom chargeback_reason and amount
    without needing a pre-seeded case.
    """
    txn = {**DEMO_DEFAULTS["transaction"], **(payload.transaction or {}), "amount": payload.chargeback_amount}
    cust = {**DEMO_DEFAULTS["customer"], **(payload.customer or {})}
    dev = {**DEMO_DEFAULTS["device"], **(payload.device or {})}

    case_id = uuid4()
    case_input = CaseInput(
        case_id=case_id,
        chargeback_amount=payload.chargeback_amount,
        chargeback_reason=payload.chargeback_reason,
        transaction=TransactionContext(**txn, created_at=datetime.utcnow()),
        customer=CustomerContext(**cust),
        device=DeviceContext(**dev),
    )

    case_row = Case(
        id=case_id,
        status=CaseStatus.INVESTIGATING,
        chargeback_amount=payload.chargeback_amount,
        chargeback_reason=payload.chargeback_reason,
        transaction_id=txn["transaction_id"],
    )
    db.add(case_row)
    await db.flush()

    trace = investigate(case_input)
    await _persist_result(db, case_row, trace)
    return trace


# ── DYNAMIC ROUTES — must come after all static routes above ──

@router.post("/{case_id}/investigate")
async def investigate_real_case(case_id: UUID, db: AsyncSession = Depends(get_db)):
    """Runs the full pipeline against a real seeded case already in the database."""
    try:
        case_input, case_row = await load_case_input_from_db(db, case_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    trace = investigate(case_input)
    await _persist_result(db, case_row, trace)
    return trace


@router.get("/{case_id}")
async def get_case(case_id: UUID, db: AsyncSession = Depends(get_db)):
    case_row = (await db.execute(select(Case).where(Case.id == case_id))).scalar_one_or_none()
    if case_row is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return {
        "case_id": str(case_row.id),
        "status": case_row.status,
        "chargeback_amount": case_row.chargeback_amount,
        "chargeback_reason": case_row.chargeback_reason,
        "verdict": case_row.verdict,
        "confidence": case_row.confidence,
        "requires_human": case_row.requires_human,
        "trace": case_row.evidence_package,
        "created_at": case_row.created_at,
        "resolved_at": case_row.resolved_at,
    }


@router.post("/{case_id}/approve")
async def approve_case(case_id: UUID, payload: ApproveRequest, db: AsyncSession = Depends(get_db)):
    case_row = (await db.execute(select(Case).where(Case.id == case_id))).scalar_one_or_none()
    if case_row is None:
        raise HTTPException(status_code=404, detail="Case not found")

    if payload.decision:
        case_row.verdict = Verdict(payload.decision)
    case_row.status = CaseStatus.RESOLVED
    case_row.requires_human = False
    case_row.resolved_at = datetime.utcnow()  # naive — matches DB column type

    db.add(AuditLog(
        case_id=case_row.id, agent="human_reviewer", action="approve",
        payload={"decision": payload.decision or str(case_row.verdict)},
    ))
    await db.commit()

    return {"case_id": case_id, "status": "resolved", "verdict": case_row.verdict}