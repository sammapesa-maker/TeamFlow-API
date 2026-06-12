from sqlalchemy.orm import Session
from app.models.user import User
from typing import Optional, List


def create_user(email: str, username: str, hashed_password: str, db: Session) -> User:
    user = User(email=email, username=username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(email: str, db: Session) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(username: str, db: Session) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(user_id: int, db: Session) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def update_user(
    user: User,
    db: Session,
    *,
    username: Optional[str] = None,
    email: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> User:
    """
    Partial update of user fields
    """

    if username is not None:
        user.username = username # type: ignore

    if email is not None:
        user.email = email # type: ignore

    if is_active is not None:
        user.is_active = is_active # type: ignore

    db.commit()
    db.refresh(user)
    return user


def delete_user(user: User, db: Session) -> None:
    """
    Deletes a user instance (soft delete)
    """
    user.is_active = False # type : ignore
    db.commit()


def get_all_users(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()


def update_user_password(user: User, hashed_password: str, db: Session) -> User:
    user.hashed_password = hashed_password # type: ignore
    db.commit()
    db.refresh(user)
    return user