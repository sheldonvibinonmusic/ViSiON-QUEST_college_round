"""
Utility functions for hashing and identifier generation.
"""
import hashlib
import uuid

def compute_sha256(data: bytes) -> str:
    """Compute hex SHA-256 digest of binary data."""
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest()

def compute_text_sha256(text: str) -> str:
    """Compute hex SHA-256 digest of utf-8 encoded string."""
    return compute_sha256(text.encode("utf-8"))

def generate_id(prefix: str = "") -> str:
    """Generate a unique short identifier."""
    short_uuid = uuid.uuid4().hex[:12]
    return f"{prefix}_{short_uuid}" if prefix else short_uuid
