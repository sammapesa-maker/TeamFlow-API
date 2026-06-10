from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas import auth_schemas
from app.services import auth_service
from app.core.dependencies import get_db

router = APIRouter()


@router.post(
    "/register",
    response_model=auth_schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(user_data: auth_schemas.UserRegister, db: Session = Depends(get_db)):
    user = auth_service.register_user(user_data, db)
    return user


@router.post("/login")
def login_user(user_data: auth_schemas.UserLogin, db: Session = Depends(get_db)):
    user = auth_service.login_user(user_data, db)
    return {
        "message": "Login successful",
        "user": auth_schemas.UserResponse.model_validate(user),
    }
