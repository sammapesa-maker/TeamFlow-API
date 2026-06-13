from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_superuser, get_db
from app.services import superuser
from app.schemas.auth_schemas import UserRegister, UserResponse, UserUpdate

router = APIRouter(prefix="/admin", tags=["Super Admin"])


# =========================
# USERS
# =========================
@router.post("/users", response_model=UserResponse)
def create_user(
    user: UserRegister,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_superuser),
):
    return superuser.create_user(user, db)

@router.get("/users", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    _: None = Depends(get_current_superuser),
):
    # add sorting. filtering, pagination and searching
    return superuser.list_users(db)

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(get_current_superuser),
):
    return superuser.get_user(db,user_id)


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(user_data: UserUpdate, user_id:int, db: Session = Depends(get_db), _=Depends(get_current_superuser)):
    return superuser.update_user(db,user_id,  user_data)


@router.delete("/users/{user_id}")
def delete_user_route(user_id: int, db: Session = Depends(get_db), _=Depends(get_current_superuser)):
    superuser.delete_user(db, user_id)
    return {"status": "deleted"}


@router.patch("/users/{user_id}/promote-to-superuser", response_model=UserResponse)
def promote_to_superuser( user_id:int, db: Session = Depends(get_db), _=Depends(get_current_superuser)):
    return superuser.promote_to_superuser(db,user_id)


@router.patch("/users/{user_id}/demote-superuser", response_model=UserResponse)
def demote_superuser( user_id:int, db: Session = Depends(get_db), _=Depends(get_current_superuser)):
    return superuser.demote_superuser(db,user_id)


@router.patch("/users/{user_id}/activate-user", response_model=UserResponse)
def activate_user( user_id:int, db: Session = Depends(get_db), _=Depends(get_current_superuser)):
    return superuser.activate_user(db,user_id)


@router.patch("/users/{user_id}/deactivate-user", response_model=UserResponse)
def deactivate_user( user_id:int, db: Session = Depends(get_db), _=Depends(get_current_superuser)):
    return superuser.deactivate_user(db,user_id)

# QUIZ: What is the role of a superuser? (on others data)