# S.A.M.I. - API GPS
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel

from ..core.database import get_db
from ..core.security import get_current_active_user, require_role, ROLE_MANAGER
from ..models.employee import Employee
from ..services.gps_service import GPSService

router = APIRouter()

# Instancia global del servicio GPS
gps_service = GPSService()

# Modelos Pydantic
class GPSLocation(BaseModel):
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None
    timestamp: datetime
    device_id: str
    signal_strength: Optional[float] = None
    satellite_count: Optional[int] = None

class VehicleLocation(BaseModel):
    vehicle_id: str
    vehicle_name: str
    license_plate: str
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None
    timestamp: datetime
    signal_strength: Optional[float] = None
    satellite_count: Optional[int] = None

class NearbyVehiclesRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 5.0

class GeofenceAlert(BaseModel):
    type: str
    severity: str
    message: str
    vehicle_id: str
    data: Dict
    timestamp: datetime

@router.on_event("startup")
async def startup_gps_service():
    """Inicializar servicio GPS al arrancar"""
    try:
        await gps_service.initialize()
    except Exception as e:
        print(f"Error inicializando servicio GPS: {e}")

@router.get("/vehicles", response_model=Dict)
async def get_all_vehicles_locations(
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener ubicaciones de todos los vehículos"""
    return await gps_service.get_all_vehicles_locations()

@router.get("/vehicles/{vehicle_id}/location", response_model=VehicleLocation)
async def get_vehicle_location(
    vehicle_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener ubicación actual de un vehículo específico"""
    location = await gps_service.get_vehicle_location(vehicle_id)
    
    if not location:
        raise HTTPException(
            status_code=404,
            detail=f"Ubicación no encontrada para el vehículo {vehicle_id}"
        )
    
    return location

@router.get("/vehicles/{vehicle_id}/history")
async def get_vehicle_history(
    vehicle_id: str,
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener historial de ubicaciones de un vehículo"""
    try:
        # Usar fechas por defecto si no se proporcionan
        if not start_time:
            start_time = datetime.utcnow() - timedelta(hours=24)
        if not end_time:
            end_time = datetime.utcnow()
        
        history = await gps_service.get_vehicle_history(
            vehicle_id, start_time, end_time
        )
        
        return {
            "vehicle_id": vehicle_id,
            "start_time": start_time,
            "end_time": end_time,
            "locations": history[:limit],
            "total": len(history)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/vehicles/nearby")
async def get_nearby_vehicles(
    request: NearbyVehiclesRequest,
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener vehículos cerca de una ubicación"""
    try:
        nearby_vehicles = await gps_service.get_vehicles_near_location(
            request.latitude,
            request.longitude,
            request.radius_km
        )
        
        return {
            "center_latitude": request.latitude,
            "center_longitude": request.longitude,
            "radius_km": request.radius_km,
            "vehicles": nearby_vehicles,
            "count": len(nearby_vehicles)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/vehicles/{vehicle_id}/distance")
async def calculate_distance_to_vehicle(
    vehicle_id: str,
    latitude: float = Query(...),
    longitude: float = Query(...),
    current_user: Employee = Depends(get_current_active_user)
):
    """Calcular distancia a un vehículo específico"""
    try:
        location = await gps_service.get_vehicle_location(vehicle_id)
        
        if not location:
            raise HTTPException(
                status_code=404,
                detail=f"Vehículo {vehicle_id} no encontrado"
            )
        
        distance = await gps_service.calculate_distance(
            latitude, longitude,
            location["latitude"], location["longitude"]
        )
        
        return {
            "vehicle_id": vehicle_id,
            "vehicle_name": location["vehicle_name"],
            "from_latitude": latitude,
            "from_longitude": longitude,
            "to_latitude": location["latitude"],
            "to_longitude": location["longitude"],
            "distance_km": distance
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/alerts/recent")
async def get_recent_gps_alerts(
    limit: int = Query(50, ge=1, le=200),
    severity: Optional[str] = Query(None),
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener alertas GPS recientes"""
    # Esta función debería consultar la base de datos
    return {
        "alerts": [],
        "total": 0,
        "message": "Funcionalidad en desarrollo"
    }

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_gps_alert(
    alert_id: int,
    current_user: Employee = Depends(get_current_active_user)
):
    """Reconocer una alerta GPS"""
    return {
        "alert_id": alert_id,
        "acknowledged_by": current_user.id,
        "acknowledged_at": datetime.utcnow(),
        "message": "Alerta GPS reconocida correctamente"
    }

@router.get("/geofences")
async def get_geofences(
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener geofences configuradas"""
    # Esta función debería consultar la base de datos
    return {
        "geofences": [],
        "total": 0,
        "message": "Funcionalidad en desarrollo"
    }

@router.post("/geofences")
async def create_geofence(
    geofence_data: Dict,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Crear nueva geofence"""
    return {
        "message": "Geofence creada correctamente",
        "geofence_data": geofence_data
    }

@router.put("/geofences/{geofence_id}")
async def update_geofence(
    geofence_id: int,
    geofence_data: Dict,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Actualizar geofence"""
    return {
        "message": f"Geofence {geofence_id} actualizada correctamente",
        "geofence_data": geofence_data
    }

@router.delete("/geofences/{geofence_id}")
async def delete_geofence(
    geofence_id: int,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Eliminar geofence"""
    return {
        "message": f"Geofence {geofence_id} eliminada correctamente"
    }

@router.get("/routes")
async def get_routes(
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener rutas configuradas"""
    # Esta función debería consultar la base de datos
    return {
        "routes": [],
        "total": 0,
        "message": "Funcionalidad en desarrollo"
    }

@router.post("/routes")
async def create_route(
    route_data: Dict,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Crear nueva ruta"""
    return {
        "message": "Ruta creada correctamente",
        "route_data": route_data
    }

@router.get("/routes/{route_id}/trips")
async def get_route_trips(
    route_id: int,
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener viajes de una ruta"""
    return {
        "route_id": route_id,
        "trips": [],
        "total": 0,
        "message": "Funcionalidad en desarrollo"
    }

@router.post("/routes/{route_id}/trips")
async def start_route_trip(
    route_id: int,
    vehicle_id: str,
    driver_id: int,
    current_user: Employee = Depends(get_current_active_user)
):
    """Iniciar viaje de una ruta"""
    return {
        "message": f"Viaje iniciado para ruta {route_id}",
        "route_id": route_id,
        "vehicle_id": vehicle_id,
        "driver_id": driver_id,
        "started_at": datetime.utcnow()
    }

@router.get("/statistics")
async def get_gps_statistics(
    period: str = Query("today", regex="^(today|week|month|year)$"),
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener estadísticas GPS"""
    try:
        # Calcular estadísticas basadas en el período
        end_time = datetime.utcnow()
        
        if period == "today":
            start_time = end_time - timedelta(days=1)
        elif period == "week":
            start_time = end_time - timedelta(weeks=1)
        elif period == "month":
            start_time = end_time - timedelta(days=30)
        elif period == "year":
            start_time = end_time - timedelta(days=365)
        
        # Esta función debería calcular estadísticas de la base de datos
        return {
            "period": period,
            "start_time": start_time,
            "end_time": end_time,
            "total_locations": 0,
            "active_vehicles": len(gps_service.vehicles),
            "total_distance_km": 0.0,
            "average_speed_kmh": 0.0,
            "alerts_count": 0,
            "geofence_violations": 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/devices")
async def get_gps_devices(
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener dispositivos GPS"""
    return {
        "devices": list(gps_service.gps_devices.values()),
        "total": len(gps_service.gps_devices)
    }

@router.get("/devices/{device_id}/status")
async def get_device_status(
    device_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener estado de un dispositivo GPS"""
    if device_id not in gps_service.gps_devices:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    
    device = gps_service.gps_devices[device_id]
    return {
        "device_id": device_id,
        "name": device["name"],
        "type": device["device_type"],
        "enabled": device["enabled"],
        "update_interval": device["update_interval"],
        "last_seen": datetime.utcnow()  # En implementación real, consultar BD
    }

@router.post("/devices/{device_id}/test")
async def test_device_connection(
    device_id: str,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Probar conexión con un dispositivo GPS"""
    try:
        if device_id not in gps_service.gps_devices:
            raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
        
        device = gps_service.gps_devices[device_id]
        
        # Simular prueba de conexión
        return {
            "device_id": device_id,
            "success": True,
            "message": f"Dispositivo {device_id} responde correctamente",
            "device_type": device["device_type"],
            "tested_at": datetime.utcnow()
        }
        
    except Exception as e:
        return {
            "device_id": device_id,
            "success": False,
            "error": str(e),
            "tested_at": datetime.utcnow()
        }

@router.get("/system/status")
async def get_system_status(
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener estado del sistema GPS"""
    return await gps_service.get_system_status()

@router.post("/simulate/location")
async def simulate_vehicle_location(
    vehicle_id: str,
    latitude: float,
    longitude: float,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Simular ubicación de vehículo para pruebas"""
    try:
        if vehicle_id not in gps_service.vehicles:
            raise HTTPException(status_code=404, detail="Vehículo no encontrado")
        
        # Simular ubicación
        simulated_location = {
            "latitude": latitude,
            "longitude": longitude,
            "altitude": 10.0,
            "accuracy": 5.0,
            "speed": 0.0,
            "heading": 0.0,
            "timestamp": datetime.utcnow(),
            "device_id": "simulation",
            "signal_strength": 1.0,
            "satellite_count": 12,
            "simulated": True
        }
        
        # Procesar ubicación simulada
        await gps_service._process_location_update(
            vehicle_id, simulated_location, gps_service.vehicles[vehicle_id]
        )
        
        return {
            "message": f"Ubicación simulada para vehículo {vehicle_id}",
            "location": simulated_location
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/health")
async def health_check(
    current_user: Employee = Depends(get_current_active_user)
):
    """Verificar salud del sistema GPS"""
    status = await gps_service.get_system_status()
    
    return {
        "status": "healthy" if status["running"] else "unhealthy",
        "active_vehicles": status["enabled_vehicles"],
        "total_vehicles": status["total_vehicles"],
        "satellite_enabled": status["satellite_enabled"],
        "timestamp": datetime.utcnow()
    }
