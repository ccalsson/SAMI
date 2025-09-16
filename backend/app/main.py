# S.A.M.I. - Aplicación Principal FastAPI
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

from .core.config import settings
from .core.database import init_db, check_db_connection, check_redis_connection
from .api import api_router

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),gitb
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("Iniciando S.A.M.I. - Sistema Automático de Monitoreo Inteligente")
    
    # Verificar conexiones
    if not check_db_connection():
        logger.error("No se pudo conectar a la base de datos")
        raise Exception("Database connection failed")
    
    if not check_redis_connection():
        logger.error("No se pudo conectar a Redis")
        raise Exception("Redis connection failed")
    
    # Inicializar base de datos
    init_db()
    logger.info("Base de datos inicializada")
    
    # Inicializar servicios de IA
    try:
        from .services.ai_service import AIService
        ai_service = AIService()
        await ai_service.initialize()
        logger.info("Servicio de IA inicializado")
    except Exception as e:
        logger.warning(f"Error inicializando servicio de IA: {e}")
    
    # Inicializar servicio de voz
    try:
        from .services.voice_service import VoiceService
        voice_service = VoiceService()
        await voice_service.initialize()
        logger.info("Servicio de voz inicializado")
    except Exception as e:
        logger.warning(f"Error inicializando servicio de voz: {e}")
    
    yield
    
    # Shutdown
    logger.info("Cerrando S.A.M.I.")

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema Automático de Monitoreo Inteligente para empresas de movimiento de suelos y logística",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar hosts confiables
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else ["localhost", "127.0.0.1"]
)

# Incluir routers
app.include_router(api_router, prefix=settings.api_v1_prefix)

# Rutas principales
@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "S.A.M.I. - Sistema Automático de Monitoreo Inteligente",
        "version": settings.app_version,
        "status": "online",
        "environment": settings.environment
    }

@app.get("/health")
async def health_check():
    """Verificación de salud del sistema"""
    db_status = check_db_connection()
    redis_status = check_redis_connection()
    
    status_code = 200 if db_status and redis_status else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if status_code == 200 else "unhealthy",
            "database": "connected" if db_status else "disconnected",
            "redis": "connected" if redis_status else "disconnected",
            "version": settings.app_version
        }
    )

@app.get("/status")
async def system_status():
    """Estado detallado del sistema"""
    from .services.system_service import SystemService
    
    system_service = SystemService()
    status = await system_service.get_system_status()
    
    return status

# Manejo de errores globales
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Manejo de errores HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Manejo de errores generales"""
    logger.error(f"Error no manejado: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500
        }
    )

# Función para ejecutar la aplicación
def run_app():
    """Ejecutar la aplicación"""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

if __name__ == "__main__":
    run_app()
