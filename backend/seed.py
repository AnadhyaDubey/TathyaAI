import asyncio
import random
import uuid
import json
from datetime import timedelta
from faker import Faker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

from db.models import Base, Merchant, Customer, Device, Transaction, Case, CaseStatus

load_dotenv()
fake = Faker()
random.seed(42)

DATABASE_URL = os.getenv("DATABASE_URL")
MERCHANT_CATEGORIES = ["Electronics", "Fashion", "Grocery", "Travel", "Digital Services"]

async def seed():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    ground_truth = {}

    async with async_session() as session:
        merchants = [
            Merchant(
                id=f"merch_{uuid.uuid4().hex[:8]}",
                name=fake.company(),
                category=cat,
                chargeback_rate=round(random.uniform(0.005, 0.03), 4),
                auto_refund_limit=random.choice([5000, 10000, 15000]),
            ) for cat in MERCHANT_CATEGORIES
        ]
        session.add_all(merchants)

        devices = []
        for _ in range(45):
            linked = random.choices([1, 1, 1, 2, 3, 5], weights=[60, 15, 10, 8, 4, 3])[0]
            devices.append(Device(
                id=f"dev_{uuid.uuid4().hex[:8]}",
                fingerprint=fake.sha256()[:32],
                ip_address=fake.ipv4(),
                user_agent=fake.user_agent(),
                accounts_linked=linked,
                is_flagged=linked >= 3,
            ))
        session.add_all(devices)

        customers = []
        for _ in range(60):
            age_days = random.choice([
                random.randint(0, 3), random.randint(4, 30),
                random.randint(31, 365), random.randint(366, 2000),
            ])
            customers.append(Customer(
                id=f"cust_{uuid.uuid4().hex[:8]}",
                email=fake.email(),
                account_age_days=age_days,
                total_transactions=random.randint(1, 50),
            ))
        session.add_all(customers)
        await session.flush()

        transactions = []
        for _ in range(300):
            cust, merch, dev = random.choice(customers), random.choice(merchants), random.choice(devices)
            transactions.append(Transaction(
                id=f"txn_{uuid.uuid4().hex[:10]}",
                customer_id=cust.id, merchant_id=merch.id, device_id=dev.id,
                amount=round(random.uniform(200, 25000), 2),
                status="captured",
                payment_method=random.choice(["card", "upi", "netbanking"]),
                created_at=fake.date_time_between(start_date="-90d", end_date="now"),
            ))
        session.add_all(transactions)
        await session.flush()

        reasons = ["item_not_received", "unauthorized_transaction", "duplicate_charge",
                   "product_not_as_described", "subscription_cancelled"]
        cases = []
        for txn in random.sample(transactions, 50):
            cust = next(c for c in customers if c.id == txn.customer_id)
            dev = next(d for d in devices if d.id == txn.device_id)

            signals = 0
            if cust.account_age_days <= 3: signals += 1
            if dev.accounts_linked >= 3: signals += 1
            if txn.amount > 15000: signals += 1
            if random.random() < 0.15: signals += 1
            is_fraud = signals >= 2

            case = Case(
                id=uuid.uuid4(), status=CaseStatus.OPEN,
                chargeback_amount=txn.amount,
                chargeback_reason=random.choice(reasons),
                transaction_id=txn.id,
                created_at=txn.created_at + timedelta(days=random.randint(3, 45)),
            )
            cases.append(case)
            ground_truth[str(case.id)] = "fraud" if is_fraud else "legitimate"

        session.add_all(cases)
        await session.commit()

    with open("ground_truth.json", "w") as f:
        json.dump(ground_truth, f, indent=2)

    fraud_n = sum(1 for v in ground_truth.values() if v == "fraud")
    print(f"Seeded: {len(merchants)} merchants, {len(customers)} customers, "
          f"{len(devices)} devices, {len(transactions)} transactions, {len(cases)} cases")
    print(f"Ground truth: {fraud_n} fraud / {len(cases)-fraud_n} legitimate")
    print("ground_truth.json saved — keep this OUT of the agent's context, eval-only.")

if __name__ == "__main__":
    asyncio.run(seed())