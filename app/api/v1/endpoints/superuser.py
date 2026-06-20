from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_superuser
from app.services.auth_service import get_all_users_service

router = APIRouter(prefix="/admin", tags=["SuperUser"])

@router.get(path="/users", status_code=status.HTTP_200_OK)
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    _= Depends(require_superuser)
):
    return await get_all_users_service(db)