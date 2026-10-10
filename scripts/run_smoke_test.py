"""
End-to-end smoke test script for Second Opinion.
Executes an audit request against the FastAPI application and validates results.
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from backend.app.main import app

def run_smoke_test():
    client = TestClient(app)
    fixtures_dir = Path(__file__).parent.parent / "backend" / "tests" / "fixtures"

    policy_file = fixtures_dir / "sample_policy.txt"
    if not policy_file.exists():
        print(f"Error: Fixture file not found at {policy_file}")
        sys.exit(1)

    policy_text = policy_file.read_text(encoding="utf-8")
    answer = (
        "Acme Corp provides employees with a $500 home office equipment reimbursement. "
        "Employees can purchase their own laptops and request reimbursement. "
        "In addition, workers receive a $100 monthly internet stipend."
    )

    print("==================================================")
    print("Running Second Opinion End-to-End Smoke Test")
    print("==================================================")
    print(f"Original Answer: {answer}")
    print(f"Source Document Length: {len(policy_text)} characters\n")

    response = client.post(
        "/api/audits",
        data={
            "answer": answer,
            "source_text": policy_text
        }
    )

    if response.status_code != 200:
        print(f"FAILED: HTTP {response.status_code}")
        print(response.json())
        sys.exit(1)

    data = response.json()
    print(f"Audit ID: {data['audit_id']}")
    print(f"Overall Assessment: {data['summary']['assessment']}")
    print(f"Review Recommendation: {data['summary']['review_recommendation']}")
    print(f"Summary Text: {data['summary']['summary_text']}\n")

    print("Claim Findings:")
    for idx, finding in enumerate(data['findings'], start=1):
        print(f"  [{idx}] {finding['verdict']}: \"{finding['claim_text']}\"")
        print(f"      Explanation: {finding['explanation']}")
        print(f"      Evidence Count: {len(finding['evidence'])}")
        if finding['evidence']:
            top_evi = finding['evidence'][0]
            print(f"      Top Evidence ({top_evi['source_name']}): \"{top_evi['quote'][:80]}...\"")
        print()

    # Verifications
    findings = data['findings']
    assert data.get('status') == 'completed', "Audit status should be completed"
    assert len(findings) == 3, f"Expected 3 claims, got {len(findings)}"
    assert findings[0]['verdict'] == "SUPPORTED_BY_SOURCE", "Claim 1 should be SUPPORTED"
    assert findings[1]['verdict'] == "CONTRADICTED_BY_SOURCE", "Claim 2 should be CONTRADICTED"
    assert findings[2]['verdict'] == "NOT_ESTABLISHED_BY_SOURCE", "Claim 3 should be NOT_ESTABLISHED"
    assert "verifier_mode" in data.get('engine_metadata', {}), "Engine metadata should declare verifier_mode"

    print("SUCCESS: All smoke test assertions passed! Pipeline is functioning 100%.")

if __name__ == "__main__":
    run_smoke_test()
