# S.A.M.I. - Servicio de Cámaras con IA
import cv2
import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Callable
from datetime import datetime
import threading
import queue
import time
from dataclasses import dataclass

from ..core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class CameraConfig:
    """Configuración de cámara"""
    camera_id: str
    name: str
    rtsp_url: Optional[str] = None
    usb_index: Optional[int] = None
    resolution: tuple = (640, 480)
    fps: int = 30
    enabled: bool = True
    ai_enabled: bool = True
    event_detection: bool = True

@dataclass
class DetectionEvent:
    """Evento de detección"""
    camera_id: str
    event_type: str
    confidence: float
    timestamp: datetime
    data: Dict
    image_path: Optional[str] = None

class CameraService:
    """Servicio de cámaras con detección de eventos por IA"""
    
    def __init__(self):
        self.cameras = {}
        self.camera_threads = {}
        self.running = False
        self.event_callbacks = []
        self.ai_service = None
        
    async def initialize(self, ai_service=None):
        """Inicializar el servicio de cámaras"""
        try:
            self.ai_service = ai_service
            
            # Cargar configuración de cámaras
            await self.load_camera_configs()
            
            logger.info("Servicio de cámaras inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando servicio de cámaras: {e}")
            raise
    
    async def load_camera_configs(self):
        """Cargar configuraciones de cámaras"""
        # Configuración por defecto
        default_cameras = [
            CameraConfig(
                camera_id="camera_1",
                name="Cámara Principal",
                rtsp_url="rtsp://192.168.1.100:554/stream",
                resolution=(1280, 720),
                fps=30
            ),
            CameraConfig(
                camera_id="camera_2", 
                name="Cámara Surtidor",
                rtsp_url="rtsp://192.168.1.101:554/stream",
                resolution=(640, 480),
                fps=15
            ),
            CameraConfig(
                camera_id="camera_3",
                name="Cámara Taller", 
                rtsp_url="rtsp://192.168.1.102:554/stream",
                resolution=(640, 480),
                fps=15
            )
        ]
        
        for config in default_cameras:
            self.cameras[config.camera_id] = config
    
    async def start_camera(self, camera_id: str) -> bool:
        """Iniciar cámara específica"""
        try:
            if camera_id not in self.cameras:
                logger.error(f"Cámara {camera_id} no encontrada")
                return False
            
            config = self.cameras[camera_id]
            
            if camera_id in self.camera_threads:
                logger.warning(f"Cámara {camera_id} ya está ejecutándose")
                return True
            
            # Crear thread para la cámara
            thread = threading.Thread(
                target=self._camera_worker,
                args=(camera_id, config),
                daemon=True
            )
            
            self.camera_threads[camera_id] = thread
            thread.start()
            
            logger.info(f"Cámara {camera_id} iniciada")
            return True
            
        except Exception as e:
            logger.error(f"Error iniciando cámara {camera_id}: {e}")
            return False
    
    async def stop_camera(self, camera_id: str) -> bool:
        """Detener cámara específica"""
        try:
            if camera_id in self.camera_threads:
                # Marcar para detener
                self.cameras[camera_id].enabled = False
                
                # Esperar a que termine el thread
                thread = self.camera_threads[camera_id]
                thread.join(timeout=5)
                
                del self.camera_threads[camera_id]
                logger.info(f"Cámara {camera_id} detenida")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deteniendo cámara {camera_id}: {e}")
            return False
    
    async def start_all_cameras(self) -> bool:
        """Iniciar todas las cámaras"""
        try:
            self.running = True
            success_count = 0
            
            for camera_id in self.cameras:
                if await self.start_camera(camera_id):
                    success_count += 1
            
            logger.info(f"Iniciadas {success_count}/{len(self.cameras)} cámaras")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error iniciando cámaras: {e}")
            return False
    
    async def stop_all_cameras(self) -> bool:
        """Detener todas las cámaras"""
        try:
            self.running = False
            success_count = 0
            
            for camera_id in list(self.camera_threads.keys()):
                if await self.stop_camera(camera_id):
                    success_count += 1
            
            logger.info(f"Detenidas {success_count} cámaras")
            return True
            
        except Exception as e:
            logger.error(f"Error deteniendo cámaras: {e}")
            return False
    
    def _camera_worker(self, camera_id: str, config: CameraConfig):
        """Worker thread para procesar cámara"""
        cap = None
        frame_count = 0
        last_detection = 0
        
        try:
            # Abrir cámara
            if config.rtsp_url:
                cap = cv2.VideoCapture(config.rtsp_url)
            elif config.usb_index is not None:
                cap = cv2.VideoCapture(config.usb_index)
            else:
                logger.error(f"No se especificó fuente para cámara {camera_id}")
                return
            
            if not cap.isOpened():
                logger.error(f"No se pudo abrir cámara {camera_id}")
                return
            
            # Configurar resolución y FPS
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.resolution[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.resolution[1])
            cap.set(cv2.CAP_PROP_FPS, config.fps)
            
            logger.info(f"Procesando cámara {camera_id} - {config.name}")
            
            while config.enabled and self.running:
                ret, frame = cap.read()
                if not ret:
                    logger.warning(f"Error leyendo frame de cámara {camera_id}")
                    time.sleep(0.1)
                    continue
                
                frame_count += 1
                
                # Procesar frame con IA si está habilitado
                if config.ai_enabled and self.ai_service:
                    # Procesar cada N frames para optimizar rendimiento
                    if frame_count % 10 == 0:  # Cada 10 frames
                        try:
                            # Detectar eventos
                            events = await self._detect_events_in_frame(
                                camera_id, frame, config
                            )
                            
                            # Procesar eventos detectados
                            for event in events:
                                await self._process_detection_event(event)
                                
                        except Exception as e:
                            logger.error(f"Error procesando frame con IA: {e}")
                
                # Control de FPS
                time.sleep(1.0 / config.fps)
            
        except Exception as e:
            logger.error(f"Error en worker de cámara {camera_id}: {e}")
        finally:
            if cap:
                cap.release()
            logger.info(f"Worker de cámara {camera_id} terminado")
    
    async def _detect_events_in_frame(self, camera_id: str, frame: np.ndarray, config: CameraConfig) -> List[DetectionEvent]:
        """Detectar eventos en un frame"""
        events = []
        
        try:
            if not self.ai_service:
                return events
            
            # Detectar caras
            if config.event_detection:
                face_results = await self.ai_service.recognize_faces_in_image_from_frame(frame)
                
                for result in face_results:
                    if result['employee_id'] is None:
                        # Persona no reconocida
                        event = DetectionEvent(
                            camera_id=camera_id,
                            event_type="unauthorized_person",
                            confidence=result['confidence'],
                            timestamp=datetime.utcnow(),
                            data={
                                'face_location': result['face_location'],
                                'employee_id': None,
                                'employee_name': 'Unknown'
                            }
                        )
                        events.append(event)
                    else:
                        # Empleado reconocido
                        event = DetectionEvent(
                            camera_id=camera_id,
                            event_type="employee_detected",
                            confidence=result['confidence'],
                            timestamp=datetime.utcnow(),
                            data={
                                'face_location': result['face_location'],
                                'employee_id': result['employee_id'],
                                'employee_name': result['employee_name']
                            }
                        )
                        events.append(event)
            
            # Detectar objetos (herramientas, vehículos, etc.)
            object_results = await self.ai_service.detect_objects_in_image_from_frame(frame)
            
            for result in object_results:
                if result['confidence'] > 0.7:
                    event = DetectionEvent(
                        camera_id=camera_id,
                        event_type="object_detected",
                        confidence=result['confidence'],
                        timestamp=datetime.utcnow(),
                        data={
                            'object_type': result['type'],
                            'bbox': result['bbox'],
                            'area': result['area']
                        }
                    )
                    events.append(event)
            
        except Exception as e:
            logger.error(f"Error detectando eventos en frame: {e}")
        
        return events
    
    async def _process_detection_event(self, event: DetectionEvent):
        """Procesar evento de detección"""
        try:
            # Guardar imagen si es necesario
            if event.event_type in ["unauthorized_person", "object_detected"]:
                event.image_path = await self._save_event_image(event)
            
            # Notificar callbacks
            for callback in self.event_callbacks:
                try:
                    await callback(event)
                except Exception as e:
                    logger.error(f"Error en callback de evento: {e}")
            
            logger.info(f"Evento detectado: {event.event_type} en cámara {event.camera_id}")
            
        except Exception as e:
            logger.error(f"Error procesando evento de detección: {e}")
    
    async def _save_event_image(self, event: DetectionEvent) -> str:
        """Guardar imagen del evento"""
        try:
            # Crear directorio si no existe
            events_dir = os.path.join(settings.data_dir, "events")
            os.makedirs(events_dir, exist_ok=True)
            
            # Generar nombre de archivo
            timestamp = event.timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"{event.camera_id}_{event.event_type}_{timestamp}.jpg"
            filepath = os.path.join(events_dir, filename)
            
            # Guardar imagen (implementar según sea necesario)
            # cv2.imwrite(filepath, frame)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error guardando imagen de evento: {e}")
            return None
    
    def add_event_callback(self, callback: Callable):
        """Agregar callback para eventos de detección"""
        self.event_callbacks.append(callback)
    
    async def get_camera_status(self, camera_id: str) -> Dict:
        """Obtener estado de una cámara"""
        if camera_id not in self.cameras:
            return {"error": "Cámara no encontrada"}
        
        config = self.cameras[camera_id]
        is_running = camera_id in self.camera_threads
        
        return {
            "camera_id": camera_id,
            "name": config.name,
            "enabled": config.enabled,
            "ai_enabled": config.ai_enabled,
            "event_detection": config.event_detection,
            "is_running": is_running,
            "resolution": config.resolution,
            "fps": config.fps
        }
    
    async def get_all_cameras_status(self) -> Dict:
        """Obtener estado de todas las cámaras"""
        status = {}
        for camera_id in self.cameras:
            status[camera_id] = await self.get_camera_status(camera_id)
        
        return {
            "total_cameras": len(self.cameras),
            "running_cameras": len(self.camera_threads),
            "cameras": status
        }
    
    async def update_camera_config(self, camera_id: str, config_updates: Dict) -> bool:
        """Actualizar configuración de cámara"""
        try:
            if camera_id not in self.cameras:
                return False
            
            config = self.cameras[camera_id]
            
            # Actualizar campos permitidos
            for key, value in config_updates.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            logger.info(f"Configuración de cámara {camera_id} actualizada")
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando configuración de cámara: {e}")
            return False
    
    async def capture_image(self, camera_id: str) -> Optional[np.ndarray]:
        """Capturar imagen de una cámara"""
        try:
            if camera_id not in self.cameras:
                return None
            
            config = self.cameras[camera_id]
            
            # Abrir cámara temporalmente
            if config.rtsp_url:
                cap = cv2.VideoCapture(config.rtsp_url)
            elif config.usb_index is not None:
                cap = cv2.VideoCapture(config.usb_index)
            else:
                return None
            
            if not cap.isOpened():
                return None
            
            ret, frame = cap.read()
            cap.release()
            
            return frame if ret else None
            
        except Exception as e:
            logger.error(f"Error capturando imagen: {e}")
            return None
    
    async def get_system_status(self) -> Dict:
        """Obtener estado del servicio de cámaras"""
        return {
            "running": self.running,
            "total_cameras": len(self.cameras),
            "active_cameras": len(self.camera_threads),
            "ai_enabled": self.ai_service is not None,
            "event_callbacks": len(self.event_callbacks),
            "last_updated": datetime.utcnow()
        }
