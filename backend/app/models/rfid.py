# S.A.M.I. - Modelos de RFID
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float, Enum, JSON
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, SoftDeleteMixin
import enum

class RFIDTagType(str, enum.Enum):
    EMPLOYEE = "employee"
    ASSET = "asset"
    VEHICLE = "vehicle"
    TOOL = "tool"
    FUEL_TANK = "fuel_tank"
    CONTAINER = "container"

class RFIDTransactionType(str, enum.Enum):
    CHECK_IN = "check_in"
    CHECK_OUT = "check_out"
    TRANSFER = "transfer"
    MAINTENANCE = "maintenance"
    INVENTORY = "inventory"
    FUEL_REFILL = "fuel_refill"

class RFIDTag(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "rfid_tags"
    
    # Información básica
    tag_id = Column(String(100), unique=True, nullable=False, index=True)
    tag_type = Column(Enum(RFIDTagType), nullable=False)
    description = Column(String(200), nullable=True)
    
    # Hardware
    frequency = Column(String(20), nullable=True)  # '125kHz', '13.56MHz', '860-960MHz'
    protocol = Column(String(50), nullable=True)  # 'ISO14443A', 'ISO15693', 'EPC'
    chip_type = Column(String(50), nullable=True)
    
    # Estado
    is_active = Column(Boolean, default=True)
    is_lost = Column(Boolean, default=False)
    battery_level = Column(Float, nullable=True)  # Para tags activos
    last_seen = Column(DateTime, nullable=True)
    
    # Ubicación
    current_location = Column(String(200), nullable=True)
    last_reader_id = Column(String(50), nullable=True)
    
    # Asociaciones
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    
    # Configuración
    read_range_meters = Column(Float, nullable=True)
    read_timeout_seconds = Column(Integer, default=5)
    retry_attempts = Column(Integer, default=3)
    
    # Metadatos
    metadata = Column(JSON, nullable=True)
    installation_date = Column(DateTime, nullable=True)
    warranty_expiry = Column(DateTime, nullable=True)
    
    # Relaciones
    employee = relationship("Employee")
    asset = relationship("Asset")
    vehicle = relationship("Vehicle")
    transactions = relationship("RFIDTransaction", back_populates="tag")
    
    def __repr__(self):
        return f"<RFIDTag(id={self.id}, tag_id='{self.tag_id}', type='{self.tag_type}')>"

class RFIDReader(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "rfid_readers"
    
    # Información básica
    reader_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(200), nullable=False)
    reader_type = Column(String(50), nullable=False)  # 'fixed', 'handheld', 'gateway'
    
    # Hardware
    model = Column(String(100), nullable=True)
    manufacturer = Column(String(100), nullable=True)
    firmware_version = Column(String(50), nullable=True)
    supported_frequencies = Column(JSON, nullable=True)
    
    # Configuración de red
    ip_address = Column(String(45), nullable=True)
    mac_address = Column(String(17), nullable=True)
    port = Column(Integer, nullable=True)
    protocol = Column(String(20), nullable=True)  # 'TCP', 'UDP', 'Serial'
    
    # Estado
    is_online = Column(Boolean, default=False)
    last_heartbeat = Column(DateTime, nullable=True)
    signal_strength = Column(Float, nullable=True)
    
    # Configuración de lectura
    read_power = Column(Float, nullable=True)  # Potencia de lectura
    read_sensitivity = Column(Float, nullable=True)
    read_timeout_ms = Column(Integer, default=1000)
    
    # Métricas
    total_reads = Column(Integer, default=0)
    successful_reads = Column(Integer, default=0)
    failed_reads = Column(Integer, default=0)
    average_read_time_ms = Column(Float, nullable=True)
    
    # Relaciones
    transactions = relationship("RFIDTransaction", back_populates="reader")
    
    def __repr__(self):
        return f"<RFIDReader(id={self.id}, reader_id='{self.reader_id}', location='{self.location}')>"
    
    @property
    def success_rate(self):
        if self.total_reads > 0:
            return self.successful_reads / self.total_reads
        return 0.0

class RFIDTransaction(Base, TimestampMixin):
    __tablename__ = "rfid_transactions"
    
    # Información básica
    tag_id = Column(Integer, ForeignKey("rfid_tags.id"), nullable=False)
    reader_id = Column(Integer, ForeignKey("rfid_readers.id"), nullable=False)
    transaction_type = Column(Enum(RFIDTransactionType), nullable=False)
    
    # Timestamps
    read_time = Column(DateTime, nullable=False, index=True)
    processed_time = Column(DateTime, nullable=True)
    
    # Datos de lectura
    raw_data = Column(Text, nullable=True)
    rssi = Column(Float, nullable=True)  # Received Signal Strength Indicator
    antenna_id = Column(String(20), nullable=True)
    read_count = Column(Integer, default=1)
    
    # Contexto
    location = Column(String(200), nullable=True)
    gps_latitude = Column(Float, nullable=True)
    gps_longitude = Column(Float, nullable=True)
    
    # Procesamiento
    is_processed = Column(Boolean, default=False)
    processing_result = Column(String(50), nullable=True)  # 'success', 'error', 'duplicate', 'invalid'
    error_message = Column(Text, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    
    # Entidades relacionadas
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    # Metadatos
    metadata = Column(JSON, nullable=True)
    session_id = Column(String(100), nullable=True)
    
    # Relaciones
    tag = relationship("RFIDTag", back_populates="transactions")
    reader = relationship("RFIDReader", back_populates="transactions")
    employee = relationship("Employee")
    asset = relationship("Asset")
    project = relationship("Project")
    
    def __repr__(self):
        return f"<RFIDTransaction(tag_id={self.tag_id}, reader_id={self.reader_id}, type='{self.transaction_type}')>"

class RFIDZone(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "rfid_zones"
    
    # Información básica
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    zone_type = Column(String(50), nullable=False)  # 'entrance', 'exit', 'worksite', 'warehouse', 'fuel_station'
    
    # Ubicación
    location = Column(String(200), nullable=True)
    gps_latitude = Column(Float, nullable=True)
    gps_longitude = Column(Float, nullable=True)
    radius_meters = Column(Float, nullable=True)
    
    # Configuración
    is_active = Column(Boolean, default=True)
    requires_authorization = Column(Boolean, default=False)
    allowed_tag_types = Column(JSON, nullable=True)
    restricted_hours = Column(JSON, nullable=True)  # Horarios restringidos
    
    # Alertas
    alert_on_unauthorized = Column(Boolean, default=True)
    alert_recipients = Column(JSON, nullable=True)
    
    # Relaciones
    readers = relationship("RFIDReader", secondary="rfid_zone_readers")
    
    def __repr__(self):
        return f"<RFIDZone(id={self.id}, name='{self.name}', type='{self.zone_type}')>"

class RFIDZoneReader(Base, TimestampMixin):
    __tablename__ = "rfid_zone_readers"
    
    zone_id = Column(Integer, ForeignKey("rfid_zones.id"), nullable=False)
    reader_id = Column(Integer, ForeignKey("rfid_readers.id"), nullable=False)
    is_primary = Column(Boolean, default=False)
    
    # Relaciones
    zone = relationship("RFIDZone")
    reader = relationship("RFIDReader")

class RFIDAlert(Base, TimestampMixin):
    __tablename__ = "rfid_alerts"
    
    # Información básica
    alert_type = Column(String(50), nullable=False)  # 'unauthorized_access', 'tag_lost', 'reader_offline', 'duplicate_read'
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), nullable=False)  # 'low', 'medium', 'high', 'critical'
    
    # Contexto
    tag_id = Column(Integer, ForeignKey("rfid_tags.id"), nullable=True)
    reader_id = Column(Integer, ForeignKey("rfid_readers.id"), nullable=True)
    zone_id = Column(Integer, ForeignKey("rfid_zones.id"), nullable=True)
    
    # Estado
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    
    # Notificaciones
    notification_sent = Column(Boolean, default=False)
    notification_recipients = Column(JSON, nullable=True)
    
    # Metadatos
    metadata = Column(JSON, nullable=True)
    
    # Relaciones
    tag = relationship("RFIDTag")
    reader = relationship("RFIDReader")
    zone = relationship("RFIDZone")
    resolved_by = relationship("Employee")
    
    def __repr__(self):
        return f"<RFIDAlert(id={self.id}, type='{self.alert_type}', severity='{self.severity}')>"
