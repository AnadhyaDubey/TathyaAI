import asyncio
import time
import json
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from dotenv import load_dotenv

from db.models import Case, Transaction, Customer, Device
from schemas import CaseInput, TransactionContext, CustomerContext, DeviceContext
from agent_graph import build_graph
from policy_engine import apply_policy

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

with open("ground_truth.json") as f:
    ground_truth = json.load(f)


async def eval_all():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    graph = build_graph()

    results = []

    async with async_session() as session:
        cases_result = await session.execute(select(Case))
        all_cases = cases_result.scalars().all()

        for case_row in all_cases:
            txn = (await session.execute(
                select(Transaction).where(Transaction.id == case_row.transaction_id)
            )).scalar_one()
            cust = (await session.execute(
                select(Customer).where(Customer.id == txn.customer_id)
            )).scalar_one()
            dev = (await session.execute(
                select(Device).where(Device.id == txn.device_id)
            )).scalar_one()

            case_input = CaseInput(
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
            )

            try:
                final_state = graph.invoke({"case": case_input})
                verdict = final_state["verdict"]
                decision = apply_policy(
                    verdict, case_input.chargeback_amount,
                    final_state["fraud_hypothesis"].confidence,
                    final_state["defense_hypothesis"].confidence,
                )
                expected = ground_truth.get(str(case_row.id))

                results.append({
                    "case_id": str(case_row.id),
                    "expected": expected,
                    "predicted": decision.final_verdict,
                    "confidence": verdict.confidence,
                    "requires_human": decision.requires_human,
                    "amount": case_input.chargeback_amount,
                })
                print(f"[{len(results)}/{len(all_cases)}] {case_row.id} → predicted={decision.final_verdict} expected={expected} human={decision.requires_human}")
                time.sleep(2)

            except Exception as e:
                print(f"[ERROR] {case_row.id}: {e}")
                results.append({
                    "case_id": str(case_row.id), "expected": ground_truth.get(str(case_row.id)),
                    "predicted": "error", "confidence": None,
                    "requires_human": True, "amount": case_input.chargeback_amount,
                })

    with open("eval_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Metrics
    auto_decided = [r for r in results if not r["requires_human"] and r["predicted"] != "error"]
    tp = sum(1 for r in auto_decided if r["predicted"] == "fraud" and r["expected"] == "fraud")
    fp = sum(1 for r in auto_decided if r["predicted"] == "fraud" and r["expected"] == "legitimate")
    fn = sum(1 for r in auto_decided if r["predicted"] == "legitimate" and r["expected"] == "fraud")
    tn = sum(1 for r in auto_decided if r["predicted"] == "legitimate" and r["expected"] == "legitimate")

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    escalation_rate = sum(1 for r in results if r["requires_human"]) / len(results)

    avg_txn_value = sum(r["amount"] for r in results) / len(results)
    fp_cost = fp * avg_txn_value

    print("\n" + "="*50)
    print(f"Total cases: {len(results)}")
    print(f"Auto-decided: {len(auto_decided)} | Escalated to human: {len(results) - len(auto_decided)}")
    print(f"Escalation rate: {escalation_rate:.1%}")
    print(f"Precision: {precision:.2f} | Recall: {recall:.2f}")
    print(f"False positives: {fp} | False negatives: {fn}")
    print(f"Estimated ₹ cost of false positives: ₹{fp_cost:,.0f}")
    print("="*50)


if __name__ == "__main__":
    asyncio.run(eval_all())