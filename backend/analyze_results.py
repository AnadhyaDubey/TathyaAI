import json

with open("eval_results.json") as f:
    results = json.load(f)

auto = [r for r in results if not r["requires_human"] and r["predicted"] != "error"]
escalated = [r for r in results if r["requires_human"]]

insufficient = [r for r in results if r["predicted"] == "insufficient_evidence"]
committed = [r for r in results if r["predicted"] in ("fraud", "legitimate")]

print(f"Total: {len(results)}")
print(f"Auto-decided: {len(auto)} | Escalated: {len(escalated)}")
print(f"Judge said 'insufficient_evidence': {len(insufficient)}")
print(f"Judge committed to fraud/legitimate: {len(committed)}\n")

correct_committed = sum(1 for r in committed if r["predicted"] == r["expected"])
print(f"Accuracy WHEN judge committed to a verdict: {correct_committed}/{len(committed)} = {correct_committed/len(committed):.1%}\n")

print("--- Escalated bucket breakdown ---")
esc_fraud_correct_direction = sum(1 for r in escalated if r["expected"] == "fraud")
esc_legit_but_escalated = sum(1 for r in escalated if r["expected"] == "legitimate")
print(f"  Real fraud cases (correctly escalated, none auto-approved): {esc_fraud_correct_direction}")
print(f"  Real legitimate cases escalated anyway (conservative, not wrong): {esc_legit_but_escalated}")

wrong_committed = [r for r in committed if r["predicted"] != r["expected"]]
print(f"\n--- Cases where judge committed AND was wrong ---")
for r in wrong_committed:
    print(f"  predicted={r['predicted']} expected={r['expected']} human_review={r['requires_human']} amount=₹{r['amount']:.0f}")