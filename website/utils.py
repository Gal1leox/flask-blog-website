import uuid
from datetime import datetime


def timesince(dt, default="just now"):
    now = datetime.utcnow()
    diff = now - dt
    periods = [
        (diff.days // 365, "y"),
        ((diff.days % 365) // 30, "mo"),
        (diff.days % 30, "d"),
        (diff.seconds // 3600, "h"),
        ((diff.seconds % 3600) // 60, "min"),
        (diff.seconds % 60, "s"),
    ]
    for amount, name in periods:
        if amount:
            return f"{amount}{name} ago"
    return default


def generate_username(max_length: int = 15) -> str:
    prefix = "usr."
    suffix_len = max_length - len(prefix)

    return f"{prefix}{uuid.uuid4().hex[:suffix_len]}"
