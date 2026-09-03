import warnings
warnings.filterwarnings("ignore")

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_graph import build_graph
from policy_engine import apply_policy
from evidence_guard import find_unverifiable_signals
from injection_guard import detect_injection
from schemas import CaseInput, TransactionContext, CustomerContext, DeviceContext
from db.models import Case, Transaction, Customer, Device

_graph = build_graph()  # compiled once, reused across requests


def investigate(case_input: CaseInput) -> dict:
    """
    Runs the full TathyaAI pipeline end to end:
    injection guard -> fraud/defense agents -> judge -> policy engine -> evidence guard.
    Returns a fully structured trace, suitable for API response / UI rendering.
    """
    layer1_matches = detect_injection(case_input.chargeback_reason)

    final_state = _graph.invoke({"case": case_input})
    fraud = final_state["fraud_hypothesis"]
    defense = final_state["defense_hypothesis"]
    verdict = final_state["verdict"]

    decision = apply_policy(
        verdict,
        case_input.chargeback_amount,
        fraud.confidence,
        defense.confidence,
    )

    all_cited = fraud.cited_signals + defense.cited_signals
    unverifiable = find_unverifiable_signals(all_cited)

    final_requires_human = decision.requires_human or bool(layer1_matches) or bool(unverifiable)

    return {
        "case_id": str(case_input.case_id),
        "chargeback_amount": case_input.chargeback_amount,
        "chargeback_reason": case_input.chargeback_reason,
        "layer1_injection_guard": {
            "triggered": bool(layer1_matches),
            "matched_patterns": layer1_matches,
        },
        "fraud_hypothesis": fraud.model_dump(),
        "defense_hypothesis": defense.model_dump(),
        "judge_verdict": verdict.model_dump(),
        "policy_decision": {
            "final_verdict": decision.final_verdict,
            "requires_human": decision.requires_human,
            "override_reason": decision.override_reason,
        },
        "evidence_guard": {
            "unverifiable_signals": unverifiable,
            "triggered": bool(unverifiable),
        },
        "final_requires_human": final_requires_human,
        "final_verdict": decision.final_verdict,
    }


async def load_case_input_from_db(session: AsyncSession, case_id) -> CaseInput:
    """Loads a real seeded case + its linked transaction/customer/device and
    assembles the CaseInput the agent graph expects."""
    case_row = (await session.execute(select(Case).where(Case.id == case_id))).scalar_one_or_none()
    if case_row is None:
        raise ValueError(f"Case {case_id} not found")

    txn = (await session.execute(
        select(Transaction).where(Transaction.id == case_row.transaction_id)
    )).scalar_one()
    cust = (await session.execute(
        select(Customer).where(Customer.id == txn.customer_id)
    )).scalar_one()
    dev = (await session.execute(
        select(Device).where(Device.id == txn.device_id)
    )).scalar_one()

    return CaseInput(
        case_id=case_row.id,
        chargeback_amount=case_row.chargeback_amount,
        chargeback_reason=case_row.chargeback_reason,
        transaction=TransactionContext(
            transaction_id=txn.id, customer_id=txn.customer_id,
            merchant_id=txn.merchant_id, device_id=txn.device_id,
            amount=txn.amount, payment_method=txn.payment_method,
            created_at=txn.created_at,
        ),
        customer=CustomerContext(
            customer_id=cust.id, account_age_days=cust.account_age_days,
            total_transactions=cust.total_transactions,
            total_chargebacks=cust.total_chargebacks,
            chargeback_rate=cust.chargeback_rate, is_flagged=cust.is_flagged,
        ),
        device=DeviceContext(
            device_id=dev.id, accounts_linked=dev.accounts_linked,
            is_flagged=dev.is_flagged, ip_address=dev.ip_address,
        ),
    ), case_row