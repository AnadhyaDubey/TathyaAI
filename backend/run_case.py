import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from dotenv import load_dotenv

from db.models import Case, Transaction, Customer, Device
from schemas import CaseInput, TransactionContext, CustomerContext, DeviceContext
from agent_graph import build_graph

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


async def run_one_case():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(select(Case).limit(1))
        case_row = result.scalar_one()

        txn_result = await session.execute(
            select(Transaction).where(Transaction.id == case_row.transaction_id)
        )
        txn = txn_result.scalar_one()

        cust_result = await session.execute(
            select(Customer).where(Customer.id == txn.customer_id)
        )
        cust = cust_result.scalar_one()

        dev_result = await session.execute(
            select(Device).where(Device.id == txn.device_id)
        )
        dev = dev_result.scalar_one()

    case_input = CaseInput(
        case_id=case_row.id,
        chargeback_amount=case_row.chargeback_amount,
        chargeback_reason=case_row.chargeback_reason,
        transaction=TransactionContext(
            transaction_id=txn.id,
            customer_id=txn.customer_id,
            merchant_id=txn.merchant_id,
            device_id=txn.device_id,
            amount=txn.amount,
            payment_method=txn.payment_method,
            created_at=txn.created_at,
        ),
        customer=CustomerContext(
            customer_id=cust.id,
            account_age_days=cust.account_age_days,
            total_transactions=cust.total_transactions,
            total_chargebacks=cust.total_chargebacks,
            chargeback_rate=cust.chargeback_rate,
            is_flagged=cust.is_flagged,
        ),
        device=DeviceContext(
            device_id=dev.id,
            accounts_linked=dev.accounts_linked,
            is_flagged=dev.is_flagged,
            ip_address=dev.ip_address,
        ),
    )

    print(f"Running case {case_input.case_id} — chargeback amount ₹{case_input.chargeback_amount}")

    graph = build_graph()
    final_state = graph.invoke({"case": case_input})

    print("\n--- FRAUD HYPOTHESIS ---")
    print(final_state["fraud_hypothesis"])
    print("\n--- DEFENSE HYPOTHESIS ---")
    print(final_state["defense_hypothesis"])
    print("\n--- JUDGE VERDICT ---")
    print(final_state["verdict"])

    from policy_engine import apply_policy
    decision = apply_policy(
        final_state["verdict"],
        case_input.chargeback_amount,
        final_state["fraud_hypothesis"].confidence,
        final_state["defense_hypothesis"].confidence,
    )
    print("\n--- POLICY ENGINE DECISION ---")
    print(f"Final verdict: {decision.final_verdict}")
    print(f"Requires human: {decision.requires_human}")
    print(f"Override reason: {decision.override_reason}")


if __name__ == "__main__":
    asyncio.run(run_one_case())