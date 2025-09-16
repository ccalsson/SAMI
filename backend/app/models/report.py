# S.A.M.I. - Modelos de Reportes
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float, Enum, JSON, Date
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, SoftDeleteMixin
import enum

class ReportType(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"

class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    SENT = "sent"

class ReportFormat(str, enum.Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    HTML = "html"

class Report(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "reports"
    
    # Información básica
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(Enum(ReportType), nullable=False)
    template_id = Column(Integer, ForeignKey("report_templates.id"), nullable=True)
    
    # Fechas
    report_date = Column(Date, nullable=False, index=True)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Configuración
    format = Column(Enum(ReportFormat), default=ReportFormat.PDF)
    language = Column(String(10), default="es")
    timezone = Column(String(50), default="America/Argentina/Buenos_Aires")
    
    # Estado
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING)
    progress_percentage = Column(Float, default=0.0)
    
    # Archivos
    file_path = Column(String(300), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    file_hash = Column(String(64), nullable=True)
    
    # Generación
    generated_at = Column(DateTime, nullable=True)
    generated_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    generation_time_seconds = Column(Float, nullable=True)
    
    # Distribución
    is_auto_generated = Column(Boolean, default=False)
    recipients = Column(JSON, nullable=True)  # Lista de destinatarios
    sent_at = Column(DateTime, nullable=True)
    sent_via = Column(String(50), nullable=True)  # 'email', 'whatsapp', 'ftp'
    
    # Parámetros
    parameters = Column(JSON, nullable=True)
    filters = Column(JSON, nullable=True)
    
    # Relaciones
    template = relationship("ReportTemplate", back_populates="reports")
    generated_by = relationship("Employee")
    
    def __repr__(self):
        return f"<Report(id={self.id}, name='{self.name}', type='{self.report_type}', date='{self.report_date}')>"

class ReportTemplate(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "report_templates"
    
    # Información básica
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(Enum(ReportType), nullable=False)
    category = Column(String(100), nullable=True)  # 'operational', 'financial', 'maintenance', 'compliance'
    
    # Configuración
    format = Column(Enum(ReportFormat), default=ReportFormat.PDF)
    language = Column(String(10), default="es")
    is_auto_generated = Column(Boolean, default=False)
    generation_schedule = Column(String(100), nullable=True)  # Cron expression
    
    # Plantilla
    template_content = Column(Text, nullable=True)  # HTML/Jinja2 template
    template_file_path = Column(String(300), nullable=True)
    css_styles = Column(Text, nullable=True)
    
    # Configuración de datos
    data_sources = Column(JSON, nullable=True)  # Fuentes de datos
    required_parameters = Column(JSON, nullable=True)  # Parámetros requeridos
    default_filters = Column(JSON, nullable=True)  # Filtros por defecto
    
    # Distribución
    default_recipients = Column(JSON, nullable=True)
    distribution_method = Column(String(50), nullable=True)  # 'email', 'whatsapp', 'ftp'
    
    # Estado
    is_active = Column(Boolean, default=True)
    version = Column(String(20), default="1.0")
    
    # Relaciones
    reports = relationship("Report", back_populates="template")
    
    def __repr__(self):
        return f"<ReportTemplate(id={self.id}, name='{self.name}', type='{self.report_type}')>"

class ReportData(Base, TimestampMixin):
    __tablename__ = "report_data"
    
    # Información básica
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    data_type = Column(String(50), nullable=False)  # 'fuel_consumption', 'employee_hours', 'asset_usage', etc.
    
    # Datos
    data_json = Column(JSON, nullable=False)
    summary_stats = Column(JSON, nullable=True)
    
    # Metadatos
    source_table = Column(String(100), nullable=True)
    query_execution_time_ms = Column(Integer, nullable=True)
    record_count = Column(Integer, nullable=True)
    
    # Relaciones
    report = relationship("Report")
    
    def __repr__(self):
        return f"<ReportData(report_id={self.report_id}, type='{self.data_type}', records={self.record_count})>"

class ReportSchedule(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "report_schedules"
    
    # Información básica
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    template_id = Column(Integer, ForeignKey("report_templates.id"), nullable=False)
    
    # Programación
    cron_expression = Column(String(100), nullable=False)
    timezone = Column(String(50), default="America/Argentina/Buenos_Aires")
    next_run = Column(DateTime, nullable=True)
    last_run = Column(DateTime, nullable=True)
    
    # Configuración
    is_active = Column(Boolean, default=True)
    max_retries = Column(Integer, default=3)
    retry_delay_minutes = Column(Integer, default=5)
    
    # Parámetros
    parameters = Column(JSON, nullable=True)
    filters = Column(JSON, nullable=True)
    recipients = Column(JSON, nullable=True)
    
    # Estado
    status = Column(String(20), default="active")  # 'active', 'paused', 'error'
    error_message = Column(Text, nullable=True)
    
    # Relaciones
    template = relationship("ReportTemplate")
    
    def __repr__(self):
        return f"<ReportSchedule(id={self.id}, name='{self.name}', cron='{self.cron_expression}')>"

class ReportRecipient(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "report_recipients"
    
    # Información básica
    name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    whatsapp = Column(String(20), nullable=True)
    
    # Configuración
    preferred_format = Column(Enum(ReportFormat), default=ReportFormat.PDF)
    language = Column(String(10), default="es")
    timezone = Column(String(50), default="America/Argentina/Buenos_Aires")
    
    # Notificaciones
    receive_daily = Column(Boolean, default=False)
    receive_weekly = Column(Boolean, default=False)
    receive_monthly = Column(Boolean, default=False)
    receive_alerts = Column(Boolean, default=True)
    
    # Estado
    is_active = Column(Boolean, default=True)
    last_sent = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<ReportRecipient(id={self.id}, name='{self.name}', email='{self.email}')>"

class ReportLog(Base, TimestampMixin):
    __tablename__ = "report_logs"
    
    # Información básica
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=True)
    action = Column(String(100), nullable=False)  # 'created', 'generated', 'sent', 'failed'
    message = Column(Text, nullable=True)
    
    # Contexto
    user_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Detalles
    execution_time_ms = Column(Integer, nullable=True)
    error_code = Column(String(50), nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    # Relaciones
    report = relationship("Report")
    user = relationship("Employee")
    
    def __repr__(self):
        return f"<ReportLog(report_id={self.report_id}, action='{self.action}')>"
