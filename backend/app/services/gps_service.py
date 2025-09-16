# S.A.M.I. - Servicio GPS y Comunicación Satelital
import asyncio
import logging
import requests
import json
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import threading
import time
import math

from ..core.config import settings

logger = logging.getLogger(__name__)

class GPSService:
    """Servicio para tracking GPS y comunicación satelital"""
    
    def __init__(self):
        self.vehicles = {}
        self.gps_devices = {}
        self.running = False
        self.location_callbacks = []
        self.alert_callbacks = []
        self.satellite_enabled = settings.satellite_communication_enabled
        
    async def initialize(self):
        """Inicializar el servicio GPS"""
        try:
            # Cargar configuración de vehículos y dispositivos GPS
            await self.load_vehicle_configs()
            await self.load_gps_device_configs()
            
            # Iniciar monitoreo GPS
            if settings.gps_update_interval > 0:
                await self.start_gps_monitoring()
            
            logger.info("Servicio GPS inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando servicio GPS: {e}")
            raise
    
    async def load_vehicle_configs(self):
        """Cargar configuraciones de vehículos"""
        # Configuración por defecto
        default_vehicles = [
            {
                "vehicle_id": "vehicle_1",
                "name": "Excavadora CAT 320",
                "license_plate": "ABC-123",
                "gps_device_id": "gps_1",
                "project_id": None,
                "operator_id": None,
                "enabled": True
            },
            {
                "vehicle_id": "vehicle_2",
                "name": "Bulldozer D6T",
                "license_plate": "DEF-456", 
                "gps_device_id": "gps_2",
                "project_id": None,
                "operator_id": None,
                "enabled": True
            },
            {
                "vehicle_id": "vehicle_3",
                "name": "Camión Volvo FH16",
                "license_plate": "GHI-789",
                "gps_device_id": "gps_3",
                "project_id": None,
                "operator_id": None,
                "enabled": True
            }
        ]
        
        for config in default_vehicles:
            self.vehicles[config["vehicle_id"]] = config
    
    async def load_gps_device_configs(self):
        """Cargar configuraciones de dispositivos GPS"""
        # Configuración por defecto
        default_devices = [
            {
                "device_id": "gps_1",
                "name": "GPS Principal",
                "device_type": "satellite",
                "api_endpoint": "https://api.satellite-provider.com/v1",
                "api_key": settings.satellite_api_key,
                "update_interval": 30,
                "enabled": True
            },
            {
                "device_id": "gps_2",
                "name": "GPS Secundario",
                "device_type": "cellular",
                "api_endpoint": "https://api.cellular-provider.com/v1",
                "api_key": "cellular_key",
                "update_interval": 60,
                "enabled": True
            }
        ]
        
        for config in default_devices:
            self.gps_devices[config["device_id"]] = config
    
    async def start_gps_monitoring(self):
        """Iniciar monitoreo GPS"""
        try:
            self.running = True
            
            # Crear thread para monitoreo
            thread = threading.Thread(
                target=self._gps_monitoring_worker,
                daemon=True
            )
            thread.start()
            
            logger.info("Monitoreo GPS iniciado")
            
        except Exception as e:
            logger.error(f"Error iniciando monitoreo GPS: {e}")
            raise
    
    async def stop_gps_monitoring(self):
        """Detener monitoreo GPS"""
        self.running = False
        logger.info("Monitoreo GPS detenido")
    
    def _gps_monitoring_worker(self):
        """Worker thread para monitoreo GPS"""
        while self.running:
            try:
                # Procesar cada vehículo
                for vehicle_id, vehicle_config in self.vehicles.items():
                    if vehicle_config["enabled"]:
                        asyncio.create_task(
                            self._update_vehicle_location(vehicle_id, vehicle_config)
                        )
                
                # Esperar intervalo de actualización
                time.sleep(settings.gps_update_interval)
                
            except Exception as e:
                logger.error(f"Error en worker de monitoreo GPS: {e}")
                time.sleep(10)  # Esperar antes de reintentar
    
    async def _update_vehicle_location(self, vehicle_id: str, vehicle_config: Dict):
        """Actualizar ubicación de un vehículo"""
        try:
            gps_device_id = vehicle_config.get("gps_device_id")
            if not gps_device_id or gps_device_id not in self.gps_devices:
                return
            
            device_config = self.gps_devices[gps_device_id]
            
            # Obtener ubicación del dispositivo GPS
            location = await self._get_device_location(gps_device_id, device_config)
            
            if location:
                # Procesar ubicación
                await self._process_location_update(vehicle_id, location, vehicle_config)
            
        except Exception as e:
            logger.error(f"Error actualizando ubicación de vehículo {vehicle_id}: {e}")
    
    async def _get_device_location(self, device_id: str, device_config: Dict) -> Optional[Dict]:
        """Obtener ubicación de un dispositivo GPS"""
        try:
            if device_config["device_type"] == "satellite":
                return await self._get_satellite_location(device_id, device_config)
            elif device_config["device_type"] == "cellular":
                return await self._get_cellular_location(device_id, device_config)
            else:
                # Simular ubicación para desarrollo
                return await self._simulate_location(device_id)
                
        except Exception as e:
            logger.error(f"Error obteniendo ubicación del dispositivo {device_id}: {e}")
            return None
    
    async def _get_satellite_location(self, device_id: str, device_config: Dict) -> Optional[Dict]:
        """Obtener ubicación vía satélite"""
        try:
            if not self.satellite_enabled or not device_config.get("api_key"):
                return await self._simulate_location(device_id)
            
            # Llamada a API satelital
            headers = {
                "Authorization": f"Bearer {device_config['api_key']}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{device_config['api_endpoint']}/devices/{device_id}/location",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "latitude": data.get("latitude"),
                    "longitude": data.get("longitude"),
                    "altitude": data.get("altitude"),
                    "accuracy": data.get("accuracy"),
                    "speed": data.get("speed"),
                    "heading": data.get("heading"),
                    "timestamp": datetime.utcnow(),
                    "device_id": device_id,
                    "signal_strength": data.get("signal_strength"),
                    "satellite_count": data.get("satellite_count")
                }
            else:
                logger.warning(f"Error en API satelital: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error en comunicación satelital: {e}")
            return None
    
    async def _get_cellular_location(self, device_id: str, device_config: Dict) -> Optional[Dict]:
        """Obtener ubicación vía celular"""
        try:
            # Simular ubicación celular
            return await self._simulate_location(device_id)
            
        except Exception as e:
            logger.error(f"Error en comunicación celular: {e}")
            return None
    
    async def _simulate_location(self, device_id: str) -> Dict:
        """Simular ubicación para desarrollo"""
        import random
        
        # Coordenadas de ejemplo (Buenos Aires, Argentina)
        base_lat = -34.6037
        base_lng = -58.3816
        
        # Agregar variación aleatoria
        lat_offset = random.uniform(-0.01, 0.01)
        lng_offset = random.uniform(-0.01, 0.01)
        
        return {
            "latitude": base_lat + lat_offset,
            "longitude": base_lng + lng_offset,
            "altitude": random.uniform(10, 50),
            "accuracy": random.uniform(5, 15),
            "speed": random.uniform(0, 30),
            "heading": random.uniform(0, 360),
            "timestamp": datetime.utcnow(),
            "device_id": device_id,
            "signal_strength": random.uniform(0.7, 1.0),
            "satellite_count": random.randint(8, 12),
            "simulated": True
        }
    
    async def _process_location_update(self, vehicle_id: str, location: Dict, vehicle_config: Dict):
        """Procesar actualización de ubicación"""
        try:
            # Guardar en base de datos
            await self._save_location_to_db(vehicle_id, location)
            
            # Verificar geofences
            await self._check_geofences(vehicle_id, location)
            
            # Notificar callbacks
            for callback in self.location_callbacks:
                try:
                    await callback(vehicle_id, location)
                except Exception as e:
                    logger.error(f"Error en callback de ubicación: {e}")
            
            # Verificar alertas
            await self._check_location_alerts(vehicle_id, location)
            
        except Exception as e:
            logger.error(f"Error procesando actualización de ubicación: {e}")
    
    async def _save_location_to_db(self, vehicle_id: str, location: Dict):
        """Guardar ubicación en base de datos"""
        # Esta función debería guardar en la base de datos
        logger.debug(f"Ubicación guardada: {vehicle_id} - {location}")
    
    async def _check_geofences(self, vehicle_id: str, location: Dict):
        """Verificar geofences"""
        try:
            # Esta función debería verificar geofences en la base de datos
            # Por ahora solo logueamos
            logger.debug(f"Verificando geofences para vehículo {vehicle_id}")
            
        except Exception as e:
            logger.error(f"Error verificando geofences: {e}")
    
    async def _check_location_alerts(self, vehicle_id: str, location: Dict):
        """Verificar alertas de ubicación"""
        try:
            alerts = []
            
            # Verificar velocidad excesiva
            if location.get("speed", 0) > 80:  # km/h
                alerts.append({
                    "type": "excessive_speed",
                    "severity": "medium",
                    "message": f"Vehículo {vehicle_id} excede velocidad límite",
                    "data": {"speed": location["speed"]}
                })
            
            # Verificar señal GPS débil
            if location.get("signal_strength", 1.0) < 0.5:
                alerts.append({
                    "type": "weak_gps_signal",
                    "severity": "low",
                    "message": f"Señal GPS débil en vehículo {vehicle_id}",
                    "data": {"signal_strength": location["signal_strength"]}
                })
            
            # Procesar alertas
            for alert in alerts:
                for callback in self.alert_callbacks:
                    try:
                        await callback(vehicle_id, alert)
                    except Exception as e:
                        logger.error(f"Error en callback de alerta: {e}")
            
        except Exception as e:
            logger.error(f"Error verificando alertas de ubicación: {e}")
    
    def add_location_callback(self, callback: Callable):
        """Agregar callback para actualizaciones de ubicación"""
        self.location_callbacks.append(callback)
    
    def add_alert_callback(self, callback: Callable):
        """Agregar callback para alertas GPS"""
        self.alert_callbacks.append(callback)
    
    async def get_vehicle_location(self, vehicle_id: str) -> Optional[Dict]:
        """Obtener ubicación actual de un vehículo"""
        try:
            if vehicle_id not in self.vehicles:
                return None
            
            vehicle_config = self.vehicles[vehicle_id]
            gps_device_id = vehicle_config.get("gps_device_id")
            
            if not gps_device_id or gps_device_id not in self.gps_devices:
                return None
            
            device_config = self.gps_devices[gps_device_id]
            location = await self._get_device_location(gps_device_id, device_config)
            
            if location:
                location["vehicle_id"] = vehicle_id
                location["vehicle_name"] = vehicle_config["name"]
                location["license_plate"] = vehicle_config["license_plate"]
            
            return location
            
        except Exception as e:
            logger.error(f"Error obteniendo ubicación del vehículo {vehicle_id}: {e}")
            return None
    
    async def get_all_vehicles_locations(self) -> Dict:
        """Obtener ubicaciones de todos los vehículos"""
        locations = {}
        
        for vehicle_id in self.vehicles:
            location = await self.get_vehicle_location(vehicle_id)
            if location:
                locations[vehicle_id] = location
        
        return locations
    
    async def calculate_distance(self, lat1: float, lng1: float, 
                               lat2: float, lng2: float) -> float:
        """Calcular distancia entre dos puntos GPS (en km)"""
        try:
            # Fórmula de Haversine
            R = 6371  # Radio de la Tierra en km
            
            dlat = math.radians(lat2 - lat1)
            dlng = math.radians(lng2 - lng1)
            
            a = (math.sin(dlat/2) * math.sin(dlat/2) +
                 math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
                 math.sin(dlng/2) * math.sin(dlng/2))
            
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            distance = R * c
            
            return distance
            
        except Exception as e:
            logger.error(f"Error calculando distancia: {e}")
            return 0.0
    
    async def get_vehicles_near_location(self, latitude: float, longitude: float, 
                                       radius_km: float = 5.0) -> List[Dict]:
        """Obtener vehículos cerca de una ubicación"""
        try:
            nearby_vehicles = []
            
            for vehicle_id in self.vehicles:
                location = await self.get_vehicle_location(vehicle_id)
                
                if location:
                    distance = await self.calculate_distance(
                        latitude, longitude,
                        location["latitude"], location["longitude"]
                    )
                    
                    if distance <= radius_km:
                        location["distance_km"] = distance
                        nearby_vehicles.append(location)
            
            # Ordenar por distancia
            nearby_vehicles.sort(key=lambda x: x["distance_km"])
            
            return nearby_vehicles
            
        except Exception as e:
            logger.error(f"Error obteniendo vehículos cercanos: {e}")
            return []
    
    async def get_vehicle_history(self, vehicle_id: str, 
                                start_time: datetime, 
                                end_time: datetime) -> List[Dict]:
        """Obtener historial de ubicaciones de un vehículo"""
        try:
            # Esta función debería consultar la base de datos
            # Por ahora retornamos un ejemplo
            return []
            
        except Exception as e:
            logger.error(f"Error obteniendo historial del vehículo {vehicle_id}: {e}")
            return []
    
    async def get_system_status(self) -> Dict:
        """Obtener estado del servicio GPS"""
        return {
            "running": self.running,
            "total_vehicles": len(self.vehicles),
            "enabled_vehicles": len([v for v in self.vehicles.values() if v["enabled"]]),
            "total_devices": len(self.gps_devices),
            "enabled_devices": len([d for d in self.gps_devices.values() if d["enabled"]]),
            "satellite_enabled": self.satellite_enabled,
            "update_interval": settings.gps_update_interval,
            "location_callbacks": len(self.location_callbacks),
            "alert_callbacks": len(self.alert_callbacks),
            "last_updated": datetime.utcnow()
        }
