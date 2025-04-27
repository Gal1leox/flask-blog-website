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


def get_verification_code(token: str):
    from website.infrastructure.repositories import (
        VerificationCodeRepository,
    )

    vc = VerificationCodeRepository.get_by_token(token)
    if not vc or vc.is_valid:
        return None
    return vc
