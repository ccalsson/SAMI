# S.A.M.I. - Modelos de Interacción por Voz
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float, Enum, JSON
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum

class VoiceCommandType(str, enum.Enum):
    # Consultas de información
    FUEL_LEVEL = "fuel_level"
    EMPLOYEE_STATUS = "employee_status"
    ASSET_LOCATION = "asset_location"
    PROJECT_STATUS = "project_status"
    WEATHER = "weather"
    
    # Control de activos
    CHECKOUT_ASSET = "checkout_asset"
    CHECKIN_ASSET = "checkin_asset"
    REPORT_ISSUE = "report_issue"
    
    # Control de personal
    CHECK_IN = "check_in"
    CHECK_OUT = "check_out"
    REQUEST_HELP = "request_help"
    
    # Sistema
    SYSTEM_STATUS = "system_status"
    EMERGENCY = "emergency"
    TEST_VOICE = "test_voice"

class VoiceInteractionStatus(str, enum.Enum):
    LISTENING = "listening"
    PROCESSING = "processing"
    RESPONDING = "responding"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class VoiceInteraction(Base, TimestampMixin):
    __tablename__ = "voice_interactions"
    
    # Información básica
    session_id = Column(String(100), nullable=False, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    location = Column(String(100), nullable=True)  # 'surtidor', 'taller', 'oficina'
    
    # Audio
    audio_file_path = Column(String(300), nullable=True)
    audio_duration_seconds = Column(Float, nullable=True)
    audio_quality_score = Column(Float, nullable=True)  # 0-1
    
    # Procesamiento
    raw_transcript = Column(Text, nullable=True)
    processed_transcript = Column(Text, nullable=True)
    language_detected = Column(String(10), nullable=True)
    confidence_score = Column(Float, nullable=True)  # 0-1
    
    # Comando identificado
    command_type = Column(Enum(VoiceCommandType), nullable=True)
    command_parameters = Column(JSON, nullable=True)
    
    # Respuesta
    response_text = Column(Text, nullable=True)
    response_audio_path = Column(String(300), nullable=True)
    response_duration_seconds = Column(Float, nullable=True)
    
    # Estado
    status = Column(Enum(VoiceInteractionStatus), default=VoiceInteractionStatus.LISTENING)
    processing_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Contexto
    device_id = Column(String(50), nullable=True)
    microphone_id = Column(String(50), nullable=True)
    speaker_id = Column(String(50), nullable=True)
    
    # Relaciones
    employee = relationship("Employee", back_populates="voice_interactions")
    commands = relationship("VoiceCommand", back_populates="interaction")
    
    def __repr__(self):
        return f"<VoiceInteraction(id={self.id}, session_id='{self.session_id}', status='{self.status}')>"

class VoiceCommand(Base, TimestampMixin):
    __tablename__ = "voice_commands"
    
    # Información básica
    interaction_id = Column(Integer, ForeignKey("voice_interactions.id"), nullable=False)
    command_type = Column(Enum(VoiceCommandType), nullable=False)
    command_text = Column(String(500), nullable=False)
    
    # Parámetros
    parameters = Column(JSON, nullable=True)
    entities = Column(JSON, nullable=True)  # Entidades extraídas (nombres, números, fechas)
    
    # Procesamiento
    intent_confidence = Column(Float, nullable=True)  # 0-1
    entity_confidence = Column(Float, nullable=True)  # 0-1
    processing_time_ms = Column(Integer, nullable=True)
    
    # Resultado
    is_executed = Column(Boolean, default=False)
    execution_result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Contexto
    context_data = Column(JSON, nullable=True)
    
    # Relaciones
    interaction = relationship("VoiceInteraction", back_populates="commands")
    
    def __repr__(self):
        return f"<VoiceCommand(id={self.id}, type='{self.command_type}', text='{self.command_text}')>"

class VoiceProfile(Base, TimestampMixin):
    __tablename__ = "voice_profiles"
    
    # Información básica
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    voice_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Características de voz
    voice_encoding = Column(JSON, nullable=True)  # Embeddings de voz
    accent = Column(String(50), nullable=True)
    language = Column(String(10), default="es")
    speaking_rate = Column(Float, nullable=True)  # Palabras por minuto
    pitch_range = Column(JSON, nullable=True)  # Rango de tono
    
    # Preferencias
    preferred_voice_commands = Column(JSON, nullable=True)
    custom_commands = Column(JSON, nullable=True)
    
    # Estadísticas
    total_interactions = Column(Integer, default=0)
    successful_interactions = Column(Integer, default=0)
    average_confidence = Column(Float, nullable=True)
    
    # Estado
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime, nullable=True)
    
    # Relaciones
    employee = relationship("Employee")
    
    def __repr__(self):
        return f"<VoiceProfile(employee_id={self.employee_id}, voice_id='{self.voice_id}')>"
    
    @property
    def success_rate(self):
        if self.total_interactions > 0:
            return self.successful_interactions / self.total_interactions
        return 0.0

class VoiceDevice(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "voice_devices"
    
    # Información básica
    device_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    device_type = Column(String(50), nullable=False)  # 'microphone', 'speaker', 'both'
    location = Column(String(100), nullable=False)
    
    # Configuración de hardware
    microphone_model = Column(String(100), nullable=True)
    speaker_model = Column(String(100), nullable=True)
    sample_rate = Column(Integer, nullable=True)
    channels = Column(Integer, nullable=True)
    
    # Configuración de audio
    volume_level = Column(Float, default=0.5)  # 0-1
    noise_reduction = Column(Boolean, default=True)
    echo_cancellation = Column(Boolean, default=True)
    auto_gain_control = Column(Boolean, default=True)
    
    # Estado
    is_online = Column(Boolean, default=False)
    last_heartbeat = Column(DateTime, nullable=True)
    firmware_version = Column(String(50), nullable=True)
    
    # Métricas
    total_interactions = Column(Integer, default=0)
    average_response_time_ms = Column(Float, nullable=True)
    error_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<VoiceDevice(id={self.id}, device_id='{self.device_id}', type='{self.device_type}')>"

class VoiceTrainingData(Base, TimestampMixin):
    __tablename__ = "voice_training_data"
    
    # Información básica
    text = Column(Text, nullable=False)
    audio_file_path = Column(String(300), nullable=False)
    language = Column(String(10), default="es")
    
    # Anotaciones
    intent = Column(String(100), nullable=True)
    entities = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Metadatos
    speaker_id = Column(String(100), nullable=True)
    recording_quality = Column(String(20), nullable=True)  # 'excellent', 'good', 'fair', 'poor'
    background_noise_level = Column(String(20), nullable=True)
    
    # Estado
    is_verified = Column(Boolean, default=False)
    verified_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    # Relaciones
    verified_by = relationship("Employee")
    
    def __repr__(self):
        return f"<VoiceTrainingData(id={self.id}, text='{self.text[:50]}...', intent='{self.intent}')>"
