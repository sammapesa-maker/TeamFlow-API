from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth_routes,
    superuser,
    task,
    team,
    team_member
)

# This is the master router for ALL v1 endpoints
v1_router = APIRouter()

# Include individual routers
v1_router.include_router(auth_routes.router, prefix="/auth", tags=["Authentication & Users"])
v1_router.include_router(superuser.router)
v1_router.include_router(task.router)
v1_router.include_router(team.router)
v1_router.include_router(team_member.router)