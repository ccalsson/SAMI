# S.A.M.I. - Modelos de GPS y Vehículos
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float, Enum, JSON
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, SoftDeleteMixin
import enum

class VehicleStatus(str, enum.Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"
    LOST = "lost"

class GPSStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    LOW_SIGNAL = "low_signal"
    NO_SIGNAL = "no_signal"

class Vehicle(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "vehicles"
    
    # Información básica
    name = Column(String(100), nullable=False)
    license_plate = Column(String(20), unique=True, nullable=False, index=True)
    vehicle_type = Column(String(50), nullable=False)  # 'excavator', 'bulldozer', 'truck', 'car'
    make = Column(String(50), nullable=True)
    model = Column(String(50), nullable=True)
    year = Column(Integer, nullable=True)
    
    # Estado operacional
    status = Column(Enum(VehicleStatus), default=VehicleStatus.AVAILABLE)
    is_gps_enabled = Column(Boolean, default=True)
    gps_device_id = Column(String(50), unique=True, nullable=True, index=True)
    
    # Especificaciones
    fuel_capacity = Column(Float, nullable=True)  # Capacidad en litros
    current_fuel_level = Column(Float, nullable=True)
    max_speed = Column(Float, nullable=True)  # km/h
    engine_hours = Column(Float, default=0.0)
    
    # Asignación actual
    current_project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    current_operator_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    assigned_since = Column(DateTime, nullable=True)
    
    # Mantenimiento
    last_maintenance = Column(DateTime, nullable=True)
    next_maintenance = Column(DateTime, nullable=True)
    maintenance_hours = Column(Float, default=0.0)
    
    # Relaciones
    current_project = relationship("Project")
    current_operator = relationship("Employee")
    gps_locations = relationship("GPSLocation", back_populates="vehicle")
    fuel_transactions = relationship("FuelTransaction", back_populates="vehicle")
    
    def __repr__(self):
        return f"<Vehicle(id={self.id}, name='{self.name}', plate='{self.license_plate}', status='{self.status}')>"

class GPSLocation(Base, TimestampMixin):
    __tablename__ = "gps_locations"
    
    # Identificación
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    device_id = Column(String(50), nullable=True, index=True)
    
    # Coordenadas GPS
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)  # Precisión en metros
    
    # Información de movimiento
    speed = Column(Float, nullable=True)  # km/h
    heading = Column(Float, nullable=True)  # Grados (0-360)
    course = Column(Float, nullable=True)
    
    # Estado de la señal
    gps_status = Column(Enum(GPSStatus), default=GPSStatus.ONLINE)
    satellite_count = Column(Integer, nullable=True)
    signal_strength = Column(Float, nullable=True)
    
    # Contexto
    location_name = Column(String(200), nullable=True)
    address = Column(String(300), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    # Datos adicionales
    metadata = Column(JSON, nullable=True)
    battery_level = Column(Float, nullable=True)  # Nivel de batería del dispositivo
    temperature = Column(Float, nullable=True)  # Temperatura del dispositivo
    
    # Relaciones
    vehicle = relationship("Vehicle", back_populates="gps_locations")
    project = relationship("Project")
    
    def __repr__(self):
        return f"<GPSLocation(vehicle_id={self.vehicle_id}, lat={self.latitude}, lng={self.longitude}, speed={self.speed})>"

class Geofence(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "geofences"
    
    # Información básica
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    geofence_type = Column(String(50), nullable=False)  # 'worksite', 'warehouse', 'restricted', 'fuel_station'
    
    # Geometría
    center_latitude = Column(Float, nullable=False)
    center_longitude = Column(Float, nullable=False)
    radius_meters = Column(Float, nullable=True)
    polygon_coordinates = Column(JSON, nullable=True)  # Para geofences complejas
    
    # Configuración
    is_active = Column(Boolean, default=True)
    alert_on_enter = Column(Boolean, default=False)
    alert_on_exit = Column(Boolean, default=False)
    alert_recipients = Column(JSON, nullable=True)
    
    # Proyecto asociado
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    # Relaciones
    project = relationship("Project")
    violations = relationship("GeofenceViolation", back_populates="geofence")
    
    def __repr__(self):
        return f"<Geofence(id={self.id}, name='{self.name}', type='{self.geofence_type}')>"

class GeofenceViolation(Base, TimestampMixin):
    __tablename__ = "geofence_violations"
    
    # Información básica
    geofence_id = Column(Integer, ForeignKey("geofences.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    violation_type = Column(String(50), nullable=False)  # 'enter', 'exit', 'unauthorized'
    
    # Ubicación
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Detalles
    speed = Column(Float, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Estado
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    
    # Relaciones
    geofence = relationship("Geofence", back_populates="violations")
    vehicle = relationship("Vehicle")
    acknowledged_by = relationship("Employee")
    
    def __repr__(self):
        return f"<GeofenceViolation(geofence_id={self.geofence_id}, type='{self.violation_type}', timestamp='{self.timestamp}')>"

class Route(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "routes"
    
    # Información básica
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    route_type = Column(String(50), nullable=False)  # 'delivery', 'pickup', 'maintenance', 'patrol'
    
    # Puntos de la ruta
    waypoints = Column(JSON, nullable=False)  # Lista de coordenadas
    total_distance_km = Column(Float, nullable=True)
    estimated_duration_minutes = Column(Integer, nullable=True)
    
    # Configuración
    is_active = Column(Boolean, default=True)
    is_recurring = Column(Boolean, default=False)
    frequency_days = Column(Integer, nullable=True)
    
    # Proyecto asociado
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    # Relaciones
    project = relationship("Project")
    trips = relationship("RouteTrip", back_populates="route")
    
    def __repr__(self):
        return f"<Route(id={self.id}, name='{self.name}', type='{self.route_type}')>"

class RouteTrip(Base, TimestampMixin):
    __tablename__ = "route_trips"
    
    # Información básica
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Fechas
    planned_start = Column(DateTime, nullable=True)
    actual_start = Column(DateTime, nullable=True)
    planned_end = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    
    # Estado
    status = Column(String(20), nullable=False)  # 'planned', 'in_progress', 'completed', 'cancelled'
    progress_percentage = Column(Float, default=0.0)
    
    # Métricas
    distance_traveled_km = Column(Float, default=0.0)
    fuel_consumed_liters = Column(Float, default=0.0)
    duration_minutes = Column(Integer, nullable=True)
    
    # Notas
    notes = Column(Text, nullable=True)
    
    # Relaciones
    route = relationship("Route", back_populates="trips")
    vehicle = relationship("Vehicle")
    driver = relationship("Employee")
    
    def __repr__(self):
        return f"<RouteTrip(route_id={self.route_id}, vehicle_id={self.vehicle_id}, status='{self.status}')>"
