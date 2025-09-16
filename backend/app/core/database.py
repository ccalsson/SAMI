# S.A.M.I. - Configuración de Base de Datos
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis
from .config import settings

# Configuración de PostgreSQL
engine = create_engine(
    settings.database_url,
    poolclass=StaticPool,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.debug
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Configuración de Redis
redis_client = redis.from_url(settings.redis_url, decode_responses=True)

def get_db():
    """Dependencia para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    """Dependencia para obtener cliente Redis"""
    return redis_client

def init_db():
    """Inicializar base de datos"""
    from ..models import Base
    Base.metadata.create_all(bind=engine)

def check_db_connection():
    """Verificar conexión a base de datos"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"Error de conexión a base de datos: {e}")
        return False

def check_redis_connection():
    """Verificar conexión a Redis"""
    try:
        redis_client.ping()
        return True
    except Exception as e:
        print(f"Error de conexión a Redis: {e}")
        return False
