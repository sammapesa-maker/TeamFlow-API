from sqlalchemy.orm import Session
from app.models.user_models import User

def create_user(email:str, hashed_password: str, db: Session):
    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(email: str, db: Session):
    return db.query(User).filter(User.email == email).first()