from datetime import datetime


def timesince(dt, default="just now"):
    now = datetime.utcnow()
    diff = now - dt
    periods = [
        (diff.days // 365, "year"),
        ((diff.days % 365) // 30, "month"),
        (diff.days % 30, "day"),
        (diff.seconds // 3600, "hour"),
        ((diff.seconds % 3600) // 60, "minute"),
        (diff.seconds % 60, "second"),
    ]
    for amount, name in periods:
        if amount:
            return f"{amount} {name}{'s ago' if amount > 1 else ''}"
    return default


def get_verification_code(token: str):
    from website.infrastructure.repositories import (
        VerificationCodeRepository,
    )

    vc = VerificationCodeRepository.get_by_token(token)
    if not vc or vc.is_valid:
        return None
    return vc
