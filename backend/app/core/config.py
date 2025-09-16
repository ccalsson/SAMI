# S.A.M.I. - Configuración del Sistema
from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    # Información básica
    app_name: str = "SAMI - Sistema Automático de Monitoreo Inteligente"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Base de datos
    database_url: str = "postgresql://sami_user:sami_password@localhost:5432/sami_db"
    redis_url: str = "redis://localhost:6379"
    
    # API
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Archivos y almacenamiento
    upload_dir: str = "uploads"
    data_dir: str = "data"
    models_dir: str = "models"
    reports_dir: str = "reports"
    
    # IA y Machine Learning
    ai_model_path: str = "models"
    face_recognition_model: str = "models/face_recognition.pkl"
    voice_model_path: str = "models/whisper"
    tts_model_path: str = "models/tts"
    
    # Cámaras y sensores
    camera_rtsp_urls: List[str] = []
    camera_timeout: int = 30
    sensor_polling_interval: int = 5
    
    # Comunicación
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # GPS y comunicación satelital
    gps_update_interval: int = 30  # segundos
    satellite_communication_enabled: bool = False
    satellite_api_key: Optional[str] = None
    
    # Reportes
    report_generation_timeout: int = 300  # segundos
    auto_report_enabled: bool = True
    report_retention_days: int = 365
    
    # Seguridad
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    password_min_length: int = 8
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/sami.log"
    log_rotation: str = "daily"
    log_retention_days: int = 30
    
    # Hardware específico
    raspberry_pi_mode: bool = False
    gpio_enabled: bool = False
    i2c_enabled: bool = False
    spi_enabled: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instancia global de configuración
settings = Settings()

# Configuración específica para Raspberry Pi
if settings.raspberry_pi_mode:
    settings.gpio_enabled = True
    settings.i2c_enabled = True
    settings.spi_enabled = True
    settings.camera_timeout = 60
    settings.sensor_polling_interval = 10
