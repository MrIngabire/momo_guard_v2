import hashlib
import os
import re

_SALT = os.getenv("PII_HASH_SALT", "momoguard-default-salt")


def hash_sender(sender: str) -> str:
    if not sender:
        return sender
    digest = hashlib.sha256(f"{_SALT}:{sender}".encode("utf-8")).hexdigest()
    return f"sha256:{digest[:32]}"


def redact_text(text: str) -> str:
    return re.sub(r"\d{8,}", "[REDACTED]", text)