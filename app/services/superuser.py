from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.repositories import user as user_crud
from app.schemas.auth_schemas import UserRegister, UserUpdate
from app.services.auth_service import register_user, update_profile

def _get_user(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


def get_user(db:Session, user_id: int):
    return user_crud.get_user_by_id(user_id=user_id, db=db)


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
    return user_crud.get_all_users(db)

def create_user(user: UserRegister, db: Session):
    return register_user(user_data=user, db=db)

def update_user(db: Session, user_id:int,  user_data: UserUpdate):
    user = get_user(db, user_id)
    return update_profile(data=user_data, user=user, db=db)