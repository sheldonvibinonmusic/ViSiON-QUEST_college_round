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
    content = json.dumps(openapi_data, indent=2)
    out_file.write_text(content, encoding="utf-8")
    num_paths = len(openapi_data.get("paths", {}))
    file_size_kb = len(content.encode("utf-8")) / 1024
    print(f"OpenAPI schema ({num_paths} paths, {file_size_kb:.1f} KB) successfully exported to: {out_file}")

if __name__ == "__main__":
    export_openapi()
