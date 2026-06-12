from sqlalchemy.orm import Session
from app.models.user import User


def create_user(email: str, username: str, hashed_password: str, db: Session):
    user = User(email=email, username=username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(email: str, db: Session):
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(username: str, db: Session):
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


# to implement all other repositories operations
def delete_user(user_id: int, db: Session):
    pass

def update_user():
    pass

def get_all_users():
    pass