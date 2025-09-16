# S.A.M.I. - Modelos de Eventos
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float, Enum, JSON
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum

class EventType(str, enum.Enum):
    # Eventos de personal
    EMPLOYEE_CHECK_IN = "employee_check_in"
    EMPLOYEE_CHECK_OUT = "employee_check_out"
    EMPLOYEE_OVERTIME = "employee_overtime"
    
    # Eventos de activos
    ASSET_CHECKOUT = "asset_checkout"
    ASSET_CHECKIN = "asset_checkin"
    ASSET_MAINTENANCE = "asset_maintenance"
    ASSET_LOST = "asset_lost"
    ASSET_FOUND = "asset_found"
    
    # Eventos de combustible
    FUEL_REFILL = "fuel_refill"
    FUEL_LOW_LEVEL = "fuel_low_level"
    FUEL_THEFT = "fuel_theft"
    
    # Eventos de seguridad
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SECURITY_BREACH = "security_breach"
    EMERGENCY = "emergency"
    
    # Eventos de proyecto
    PROJECT_START = "project_start"
    PROJECT_PHASE_CHANGE = "project_phase_change"
    PROJECT_DELAY = "project_delay"
    PROJECT_COMPLETION = "project_completion"
    
    # Eventos de sistema
    SYSTEM_ERROR = "system_error"
    CAMERA_OFFLINE = "camera_offline"
    SENSOR_OFFLINE = "sensor_offline"
    GPS_SIGNAL_LOST = "gps_signal_lost"
    
    # Eventos de voz
    VOICE_COMMAND = "voice_command"
    VOICE_RESPONSE = "voice_response"
    VOICE_ERROR = "voice_error"

class EventStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"

class EventPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Event(Base, TimestampMixin):
    __tablename__ = "events"
    
    # Información básica
    event_type = Column(Enum(EventType), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(EventStatus), default=EventStatus.PENDING, index=True)
    priority = Column(Enum(EventPriority), default=EventPriority.MEDIUM)
    
    # Ubicación y contexto
    location = Column(String(200), nullable=True)
    gps_latitude = Column(Float, nullable=True)
    gps_longitude = Column(Float, nullable=True)
    camera_id = Column(String(50), nullable=True)
    
    # Entidades relacionadas
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    # Datos adicionales (JSON)
    metadata = Column(JSON, nullable=True)
    ai_confidence = Column(Float, nullable=True)  # Confianza de la IA (0-1)
    
    # Timestamps
    detected_at = Column(DateTime, nullable=False, index=True)
    resolved_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    
    # Notificaciones
    notification_sent = Column(Boolean, default=False)
    notification_method = Column(String(50), nullable=True)  # 'email', 'whatsapp', 'sms'
    notification_recipients = Column(JSON, nullable=True)
    
    # Relaciones
    employee = relationship("Employee", foreign_keys=[employee_id])
    asset = relationship("Asset")
    project = relationship("Project")
    acknowledged_by = relationship("Employee", foreign_keys=[acknowledged_by_id])
    
    def __repr__(self):
        return f"<Event(id={self.id}, type='{self.event_type}', title='{self.title}', status='{self.status}')>"
    
    @property
    def is_resolved(self):
        return self.status == EventStatus.RESOLVED
    
    @property
    def is_critical(self):
        return self.priority == EventPriority.CRITICAL
    
    @property
    def duration_minutes(self):
        if self.resolved_at and self.detected_at:
            return (self.resolved_at - self.detected_at).total_seconds() / 60
        return None

class EventLog(Base, TimestampMixin):
    __tablename__ = "event_logs"
    
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    action = Column(String(100), nullable=False)  # 'created', 'updated', 'resolved', 'escalated'
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Relaciones
    event = relationship("Event")
    user = relationship("Employee")
    
    def __repr__(self):
        return f"<EventLog(event_id={self.event_id}, action='{self.action}')>"

class AlertRule(Base, TimestampMixin):
    __tablename__ = "alert_rules"
    
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(Enum(EventType), nullable=False)
    conditions = Column(JSON, nullable=False)  # Condiciones para activar la alerta
    priority = Column(Enum(EventPriority), default=EventPriority.MEDIUM)
    
    # Notificaciones
    notification_enabled = Column(Boolean, default=True)
    notification_methods = Column(JSON, nullable=True)  # ['email', 'whatsapp', 'sms']
    notification_recipients = Column(JSON, nullable=True)
    
    # Estado
    is_active = Column(Boolean, default=True)
    cooldown_minutes = Column(Integer, default=0)  # Tiempo entre alertas similares
    
    def __repr__(self):
        return f"<AlertRule(id={self.id}, name='{self.name}', event_type='{self.event_type}')>"
