# S.A.M.I. - Modelos de Combustible
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, SoftDeleteMixin
import enum

class FuelType(str, enum.Enum):
    DIESEL = "diesel"
    GASOLINE = "gasoline"
    LPG = "lpg"
    HYDRAULIC_OIL = "hydraulic_oil"
    ENGINE_OIL = "engine_oil"

class TransactionType(str, enum.Enum):
    REFILL = "refill"
    CONSUMPTION = "consumption"
    TRANSFER = "transfer"
    THEFT = "theft"
    LEAK = "leak"
    MAINTENANCE = "maintenance"

class FuelTank(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "fuel_tanks"
    
    # Información básica
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    fuel_type = Column(Enum(FuelType), nullable=False)
    capacity_liters = Column(Float, nullable=False)
    current_level_liters = Column(Float, default=0.0)
    min_level_liters = Column(Float, default=0.0)
    max_level_liters = Column(Float, nullable=True)
    
    # Ubicación
    location = Column(String(200), nullable=True)
    gps_latitude = Column(Float, nullable=True)
    gps_longitude = Column(Float, nullable=True)
    
    # Estado
    is_active = Column(Boolean, default=True)
    last_maintenance = Column(DateTime, nullable=True)
    next_maintenance = Column(DateTime, nullable=True)
    
    # Sensores
    sensor_id = Column(String(50), nullable=True)
    sensor_type = Column(String(50), nullable=True)  # 'ultrasonic', 'pressure', 'float'
    calibration_factor = Column(Float, default=1.0)
    
    # Relaciones
    transactions = relationship("FuelTransaction", back_populates="tank")
    
    def __repr__(self):
        return f"<FuelTank(id={self.id}, name='{self.name}', type='{self.fuel_type}', level={self.current_level_liters}L)>"
    
    @property
    def level_percentage(self):
        if self.capacity_liters > 0:
            return (self.current_level_liters / self.capacity_liters) * 100
        return 0.0
    
    @property
    def is_low_level(self):
        return self.current_level_liters <= self.min_level_liters
    
    @property
    def is_empty(self):
        return self.current_level_liters <= 0

class FuelTransaction(Base, TimestampMixin):
    __tablename__ = "fuel_transactions"
    
    # Información básica
    transaction_type = Column(Enum(TransactionType), nullable=False)
    fuel_type = Column(Enum(FuelType), nullable=False)
    quantity_liters = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=True)
    total_cost = Column(Float, nullable=True)
    
    # Ubicación y contexto
    tank_id = Column(Integer, ForeignKey("fuel_tanks.id"), nullable=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    
    # Detalles de la transacción
    supplier = Column(String(200), nullable=True)
    invoice_number = Column(String(100), nullable=True)
    receipt_image_path = Column(String(300), nullable=True)
    
    # Niveles antes y después
    level_before = Column(Float, nullable=True)
    level_after = Column(Float, nullable=True)
    
    # Ubicación GPS
    gps_latitude = Column(Float, nullable=True)
    gps_longitude = Column(Float, nullable=True)
    
    # Notas
    notes = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False)
    verified_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    # Relaciones
    tank = relationship("FuelTank", back_populates="transactions")
    asset = relationship("Asset", back_populates="fuel_transactions")
    project = relationship("Project")
    employee = relationship("Employee", foreign_keys=[employee_id])
    verified_by = relationship("Employee", foreign_keys=[verified_by_id])
    
    def __repr__(self):
        return f"<FuelTransaction(id={self.id}, type='{self.transaction_type}', quantity={self.quantity_liters}L)>"

class FuelConsumption(Base, TimestampMixin):
    __tablename__ = "fuel_consumption"
    
    # Información básica
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    date = Column(DateTime, nullable=False, index=True)
    
    # Consumo
    fuel_type = Column(Enum(FuelType), nullable=False)
    consumption_liters = Column(Float, nullable=False)
    hours_worked = Column(Float, nullable=True)
    consumption_per_hour = Column(Float, nullable=True)
    
    # Contexto
    work_type = Column(String(100), nullable=True)  # 'excavation', 'leveling', 'transport', 'idle'
    weather_conditions = Column(String(100), nullable=True)
    operator_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    
    # Métricas
    efficiency_rating = Column(Float, nullable=True)  # 1-10
    notes = Column(Text, nullable=True)
    
    # Relaciones
    asset = relationship("Asset")
    project = relationship("Project")
    operator = relationship("Employee")
    
    def __repr__(self):
        return f"<FuelConsumption(asset_id={self.asset_id}, date='{self.date}', consumption={self.consumption_liters}L)>"

class FuelAlert(Base, TimestampMixin):
    __tablename__ = "fuel_alerts"
    
    # Información básica
    alert_type = Column(String(50), nullable=False)  # 'low_level', 'theft', 'leak', 'maintenance_due'
    tank_id = Column(Integer, ForeignKey("fuel_tanks.id"), nullable=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    
    # Detalles
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), nullable=False)  # 'low', 'medium', 'high', 'critical'
    
    # Estado
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    
    # Notificaciones
    notification_sent = Column(Boolean, default=False)
    notification_recipients = Column(Text, nullable=True)
    
    # Relaciones
    tank = relationship("FuelTank")
    asset = relationship("Asset")
    resolved_by = relationship("Employee")
    
    def __repr__(self):
        return f"<FuelAlert(id={self.id}, type='{self.alert_type}', severity='{self.severity}')>"
