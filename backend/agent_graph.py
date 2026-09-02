import os
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

from schemas import CaseInput, HypothesisOutput, JudgeVerdict
from tenacity import retry, wait_exponential, stop_after_attempt

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
)


class AgentState(TypedDict):
    case: CaseInput
    fraud_hypothesis: Optional[HypothesisOutput]
    defense_hypothesis: Optional[HypothesisOutput]
    verdict: Optional[JudgeVerdict]


def _build_context_block(case: CaseInput) -> str:
    return f"""
Transaction:
- ID: {case.transaction.transaction_id}
- Amount: {case.chargeback_amount} {case.transaction.currency}
- Payment method: {case.transaction.payment_method}
- Created at: {case.transaction.created_at}
- Chargeback reason: {case.chargeback_reason}

Customer:
- Account age (days): {case.customer.account_age_days}
- Total transactions: {case.customer.total_transactions}
- Total chargebacks: {case.customer.total_chargebacks}
- Chargeback rate: {case.customer.chargeback_rate}
- Flagged: {case.customer.is_flagged}

Device:
- Accounts linked to this device: {case.device.accounts_linked}
- Flagged: {case.device.is_flagged}
- IP: {case.device.ip_address}
""".strip()


@retry(wait=wait_exponential(multiplier=2, min=4, max=60), stop=stop_after_attempt(4))
def fraud_agent_node(state: AgentState) -> AgentState:
    context = _build_context_block(state["case"])
    prompt = f"""You are a fraud investigator building the strongest possible case that this chargeback is FRAUDULENT — meaning the cardholder is disputing a legitimate transaction they actually authorized, rather than a genuine unauthorized charge.

{context}

Build the fraud case. Cite specific signals from the data above (account age, device linkage, chargeback history, amount, etc). Do not invent facts not present in the context. If the evidence for fraud is genuinely weak, say so honestly in your argument and lower your confidence accordingly — do not manufacture a strong case from weak signals."""

    structured_llm = llm.with_structured_output(HypothesisOutput)
    hypothesis = structured_llm.invoke(prompt)
    return {"fraud_hypothesis": hypothesis}


@retry(wait=wait_exponential(multiplier=2, min=4, max=60), stop=stop_after_attempt(4))
def defense_agent_node(state: AgentState) -> AgentState:
    context = _build_context_block(state["case"])
    prompt = f"""You are a customer advocate building the strongest possible case that this chargeback is LEGITIMATE — meaning the cardholder has a genuine grievance (item not received, unauthorized charge, etc) and the merchant should honor the dispute.

{context}

Build the legitimacy case. Cite specific signals from the data above. Do not invent facts not present in the context. If the evidence for legitimacy is genuinely weak, say so honestly and lower your confidence accordingly."""

    structured_llm = llm.with_structured_output(HypothesisOutput)
    hypothesis = structured_llm.invoke(prompt)
    return {"defense_hypothesis": hypothesis}


@retry(wait=wait_exponential(multiplier=2, min=4, max=60), stop=stop_after_attempt(4))
def judge_node(state: AgentState) -> AgentState:
    context = _build_context_block(state["case"])
    fraud_case = state["fraud_hypothesis"]
    defense_case = state["defense_hypothesis"]

    prompt = f"""You are an impartial judge reviewing a chargeback dispute. Two advocates have made their cases. Weigh them against the raw evidence and reach a verdict.

{context}

FRAUD ADVOCATE'S CASE (confidence {fraud_case.confidence}):
{fraud_case.argument}
Cited signals: {fraud_case.cited_signals}

DEFENSE ADVOCATE'S CASE (confidence {defense_case.confidence}):
{defense_case.argument}
Cited signals: {defense_case.cited_signals}

Reach a verdict: "fraud", "legitimate", or "insufficient_evidence" if the two cases are too evenly matched or the evidence is too thin to decide confidently. Set requires_human=true if confidence is below 0.7 or verdict is insufficient_evidence. List the 2-4 key_factors that actually drove your decision."""

    structured_llm = llm.with_structured_output(JudgeVerdict)
    verdict = structured_llm.invoke(prompt)
    return {"verdict": verdict}


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("fraud_agent", fraud_agent_node)
    graph.add_node("defense_agent", defense_agent_node)
    graph.add_node("judge", judge_node)

    graph.set_entry_point("fraud_agent")
    graph.add_edge("fraud_agent", "defense_agent")
    graph.add_edge("defense_agent", "judge")
    graph.add_edge("judge", END)

    return graph.compile()


if __name__ == "__main__":
    print("Graph built successfully:", build_graph())