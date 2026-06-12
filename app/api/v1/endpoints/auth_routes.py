from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas import auth_schemas
from app.services import auth_service
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
router = APIRouter()


@router.post(
    path="/register",
    response_model=auth_schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(user_data: auth_schemas.UserRegister, db: Session = Depends(get_db)):
    user = auth_service.register_user(db=db, user_data=user_data)
    return user


@router.post(path="/login-json", response_model=auth_schemas.TokenResponse)
def login_json(user_data: auth_schemas.UserLogin, db: Session = Depends(get_db)):
    return auth_service.login_user(user_data=user_data, db=db)


@router.post(path="/refresh", response_model=auth_schemas.TokenResponse)
def refresh(token: auth_schemas.RefreshTokenIn, db: Session = Depends(get_db)):
    return auth_service.refresh_token(token=token.token, db=db)


@router.post(path="/logout")
def logout(token: auth_schemas.RefreshTokenIn, db: Session = Depends(get_db)):
    return auth_service.logout(token=token.token, db=db)


@router.post(path="/login", response_model=auth_schemas.TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    return auth_service.login_form(form_data=form_data, db=db)


# === USER ENDPOINTS ===

@router.get(path="/me", response_model=auth_schemas.UserResponse)
def get_user(user: User = Depends(get_current_user)):
    return user
