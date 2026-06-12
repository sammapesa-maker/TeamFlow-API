from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User


def _get_user(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


def promote_to_superuser(db: Session, user_id: int) -> User:
    user = _get_user(db, user_id)

    if not user.is_superuser:
        user.is_superuser = True # type: ignore
        db.commit()
        db.refresh(user)

    return user


def demote_superuser(db: Session, user_id: int) -> User:
    user = _get_user(db, user_id)

    if user.is_superuser:
        user.is_superuser = False # type: ignore
        db.commit()
        db.refresh(user)

    return user


def deactivate_user(db: Session, user_id: int) -> User:
    user = _get_user(db, user_id)

    if user.is_active:
        user.is_active = False # type: ignore
        db.commit()
        db.refresh(user)

    return user


def activate_user(db: Session, user_id: int) -> User:
    user = _get_user(db, user_id)

    if not user.is_active:
        user.is_active = True # type: ignore
        db.commit()
        db.refresh(user)

    return user


def delete_user(db: Session, user_id: int) -> None:
    user = _get_user(db, user_id)

    db.delete(user)
    db.commit()


def list_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.id.desc()).all()