from website import db
from website.domain.models import VerificationCode


class VerificationCodeRepository:
    @staticmethod
    def create(vc: VerificationCode) -> None:
        db.session.add(vc)
        db.session.commit()

    @staticmethod
    def get_by_token(token: str) -> VerificationCode | None:
        return VerificationCode.query.filter_by(token=token, is_valid=False).first()

    @staticmethod
    def invalidate(vc: VerificationCode) -> None:
        vc.is_valid = True
        db.session.commit()
