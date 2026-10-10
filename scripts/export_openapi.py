"""
Export the OpenAPI specification from the FastAPI app to contracts/openapi.json.
"""
import sys
import json
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.main import app

def export_openapi():
    contracts_dir = Path(__file__).parent.parent / "contracts"
    contracts_dir.mkdir(parents=True, exist_ok=True)
    out_file = contracts_dir / "openapi.json"

    openapi_data = app.openapi()
    out_file.write_text(json.dumps(openapi_data, indent=2), encoding="utf-8")
    print(f"OpenAPI schema successfully exported to: {out_file}")

if __name__ == "__main__":
    export_openapi()
