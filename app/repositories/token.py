from sqlalchemy.orm import Session
from app.models.token import RefreshToken
from app.core.security import hash_token


def get_refresh_token_by_jti(jti: str, db: Session):
    return db.query(RefreshToken).filter(RefreshToken.id == jti).first()


def revoke_refresh_token(jti: str, db: Session):
    token = get_refresh_token_by_jti(jti, db)
    if token:
        token.revoked = True
        db.commit()


def create_refresh_token_entry(
    user_id: str, token: str, jti: str, expires_at, db: Session
):
    db_token = RefreshToken(
        id=jti, user_id=user_id, token_hash=hash_token(token), expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
