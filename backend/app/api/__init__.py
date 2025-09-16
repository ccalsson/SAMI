# S.A.M.I. - API Endpoints
from fastapi import APIRouter
from .auth import router as auth_router
from .employees import router as employees_router
from .assets import router as assets_router
from .projects import router as projects_router
from .events import router as events_router
from .fuel import router as fuel_router
from .gps import router as gps_router
from .voice import router as voice_router
from .reports import router as reports_router
from .rfid import router as rfid_router
from .camera import router as camera_router

# Router principal
api_router = APIRouter()

# Incluir todos los routers
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(employees_router, prefix="/employees", tags=["employees"])
api_router.include_router(assets_router, prefix="/assets", tags=["assets"])
api_router.include_router(projects_router, prefix="/projects", tags=["projects"])
api_router.include_router(events_router, prefix="/events", tags=["events"])
api_router.include_router(fuel_router, prefix="/fuel", tags=["fuel"])
api_router.include_router(gps_router, prefix="/gps", tags=["gps"])
api_router.include_router(voice_router, prefix="/voice", tags=["voice"])
api_router.include_router(reports_router, prefix="/reports", tags=["reports"])
api_router.include_router(rfid_router, prefix="/rfid", tags=["rfid"])
api_router.include_router(camera_router, prefix="/camera", tags=["camera"])
