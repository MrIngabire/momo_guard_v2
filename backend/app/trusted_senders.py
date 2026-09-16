"""
Official MTN Rwanda sender IDs. These alphanumeric sender IDs are reserved
at the SMSC level and cannot be spoofed by ordinary senders on the MTN
Rwanda network.

Update this list when MTN publishes new service senders.
"""

TRUSTED_SENDERS = {
    # Case-insensitive exact matches
    "m-money",
    "mtn momo",
    "mtn momo rwanda",
    "mtn",
    "mtn-rw",
    "mtn rw",
    "momo",
    "mtnservice",
    "mtn service",
    "mtn mobile money",
    "momo rwanda",
}

TRUST_SCORE_CAP = 0.30          # trusted sender → cap score at this
BLACKLIST_SCORE_FLOOR = 0.80    # blacklisted sender → raise score at least this
TRUST_BYPASS_CEILING = 0.75     # if raw score ≥ this, don't trust-cap it


def is_trusted(sender: str | None) -> bool:
    """True if the sender matches one of the official MTN sender IDs."""
    if not sender:
        return False
    return sender.strip().lower() in TRUSTED_SENDERS