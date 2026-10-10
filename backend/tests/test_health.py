"""
Tests for health check and system information endpoints.
"""
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Second Opinion API is running" in data["message"]

def test_health_endpoint_schema_and_values():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"
    assert data["verifier_mode"] in ("rules_and_model", "rules_only")
    assert isinstance(data["model_loaded"], bool)
    assert data["model_id"] == "microsoft/deberta-base-mnli"
    
    assert ".txt" in data["supported_file_types"]
    assert ".pdf" in data["supported_file_types"]
    assert ".docx" in data["supported_file_types"]
    
    limits = data["limits"]
    assert limits["max_answer_chars"] == 40000
    assert limits["max_source_chars"] == 150000
    assert limits["max_files"] == 5
    assert limits["max_file_bytes"] == 10485760
    assert limits["max_claims"] == 50
