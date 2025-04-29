from website import db
from website.domain.models import VerificationCode


class VerificationCodeRepository:
    @staticmethod
    def create(verification_code: VerificationCode) -> None:
        db.session.add(verification_code)
        db.session.commit()

    @staticmethod
    def get_by_token(token: str) -> VerificationCode | None:
        return VerificationCode.query.filter_by(token=token).first()

    @staticmethod
    def invalidate(verification_code: VerificationCode) -> None:
        verification_code.is_valid = True
        db.session.commit()
