# S.A.M.I. - Modelos de Activos
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, SoftDeleteMixin
import enum

class AssetType(str, enum.Enum):
    VEHICLE = "vehicle"
    TOOL = "tool"
    EQUIPMENT = "equipment"
    MACHINERY = "machinery"
    FUEL_TANK = "fuel_tank"

class AssetStatus(str, enum.Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"
    LOST = "lost"

class Asset(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "assets"
    
    # Información básica
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    asset_code = Column(String(50), unique=True, nullable=False, index=True)
    asset_type = Column(Enum(AssetType), nullable=False)
    status = Column(Enum(AssetStatus), default=AssetStatus.AVAILABLE)
    
    # Identificación
    rfid_tag = Column(String(50), unique=True, nullable=True, index=True)
    serial_number = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    brand = Column(String(100), nullable=True)
    
    # Ubicación
    current_location_id = Column(Integer, ForeignKey("asset_locations.id"), nullable=True)
    location_description = Column(String(200), nullable=True)
    
    # Específico para vehículos
    license_plate = Column(String(20), nullable=True)
    year = Column(Integer, nullable=True)
    fuel_capacity = Column(Float, nullable=True)  # Capacidad en litros
    current_fuel_level = Column(Float, nullable=True)  # Nivel actual en litros
    
    # Específico para herramientas
    tool_category = Column(String(100), nullable=True)
    tool_condition = Column(String(50), nullable=True)  # 'excellent', 'good', 'fair', 'poor'
    
    # Costos y valor
    purchase_price = Column(Float, nullable=True)
    current_value = Column(Float, nullable=True)
    maintenance_cost = Column(Float, default=0.0)
    
    # Estado operacional
    last_maintenance = Column(DateTime, nullable=True)
    next_maintenance = Column(DateTime, nullable=True)
    total_usage_hours = Column(Float, default=0.0)
    
    # Relaciones
    current_location = relationship("AssetLocation", foreign_keys=[current_location_id])
    transactions = relationship("AssetTransaction", back_populates="asset")
    fuel_transactions = relationship("FuelTransaction", back_populates="asset")
    
    def __repr__(self):
        return f"<Asset(id={self.id}, name='{self.name}', code='{self.asset_code}', type='{self.asset_type}')>"

class AssetLocation(Base, TimestampMixin):
    __tablename__ = "asset_locations"
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    location_type = Column(String(50), nullable=False)  # 'warehouse', 'worksite', 'office', 'field'
    address = Column(String(200), nullable=True)
    gps_latitude = Column(Float, nullable=True)
    gps_longitude = Column(Float, nullable=True)
    
    # Relaciones
    assets = relationship("Asset", back_populates="current_location")
    
    def __repr__(self):
        return f"<AssetLocation(id={self.id}, name='{self.name}', type='{self.location_type}')>"

class AssetTransaction(Base, TimestampMixin):
    __tablename__ = "asset_transactions"
    
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # 'checkout', 'checkin', 'maintenance', 'transfer'
    location_from_id = Column(Integer, ForeignKey("asset_locations.id"), nullable=True)
    location_to_id = Column(Integer, ForeignKey("asset_locations.id"), nullable=True)
    
    # Detalles de la transacción
    notes = Column(Text, nullable=True)
    expected_return_date = Column(DateTime, nullable=True)
    actual_return_date = Column(DateTime, nullable=True)
    
    # Estado
    is_returned = Column(Boolean, default=False)
    is_overdue = Column(Boolean, default=False)
    
    # Relaciones
    asset = relationship("Asset", back_populates="transactions")
    employee = relationship("Employee", back_populates="asset_transactions")
    location_from = relationship("AssetLocation", foreign_keys=[location_from_id])
    location_to = relationship("AssetLocation", foreign_keys=[location_to_id])
    
    def __repr__(self):
        return f"<AssetTransaction(asset_id={self.asset_id}, employee_id={self.employee_id}, type='{self.transaction_type}')>"
