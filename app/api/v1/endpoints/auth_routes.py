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


@router.post("/login", response_model=auth_schemas.TokenResponse)
def login_user(user_data: auth_schemas.UserLogin, db: Session = Depends(get_db)):
    return auth_service.login_user(user_data, db)

@router.post("/refresh", response_model=auth_schemas.TokenResponse)
def refresh(token: auth_schemas.RefreshIn, db: Session = Depends(get_db)):
    return auth_service.refresh_token(token.token, db)

@router.post("/logout")
def logout(token: auth_schemas.RefreshIn, db: Session = Depends(get_db)):
    return auth_service.logout(token.token, db)