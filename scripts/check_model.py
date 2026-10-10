"""
Check model environment and inspect NLI availability and label mapping.
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.config import settings
from backend.app.services.nli_verifier import NLIVerifier

def check_model():
    print("==================================================")
    print("Second Opinion — Model Environment Check")
    print("==================================================")
    print(f"Model ID: {settings.MODEL_ID}")
    print(f"Device: {settings.DEVICE}")
    print(f"Model Enabled: {settings.MODEL_ENABLED}")
    print(f"URL Ingestion Enabled: {settings.URL_INGESTION_ENABLED}")
    print(f"Web Evidence Fallback Enabled: {settings.WEB_EVIDENCE_ENABLED}")

    verifier = NLIVerifier.get_instance()
    loaded = verifier.load_model()
    
    if loaded:
        print("Status: Model successfully loaded!")
        print(f"Label Map: {verifier.label_map}")
    else:
        print("Status: Model not loaded. System operates in rules-only fallback mode.")
        if verifier.load_error:
            print(f"Reason: {verifier.load_error}")

if __name__ == "__main__":
    check_model()
