from fastapi import APIRouter
from app.api.v1.endpoints import auth_routes

# This is the master router for ALL v1 endpoints
v1_router = APIRouter()

# Include individual routers
v1_router.include_router(auth_routes.router, prefix="/auth", tags=["Authentication & Users"])