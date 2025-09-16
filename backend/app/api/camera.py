# S.A.M.I. - API de Cámaras
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import cv2
import numpy as np
from datetime import datetime
import base64
import io
from PIL import Image

from ..core.database import get_db
from ..core.security import get_current_active_user, require_role, ROLE_MANAGER
from ..models.employee import Employee
from ..services.camera_service import CameraService, CameraConfig, DetectionEvent
from ..services.ai_service import AIService

router = APIRouter()

# Instancia global del servicio de cámaras
camera_service = CameraService()
ai_service = None

# Modelos Pydantic
class CameraStatusResponse(BaseModel):
    camera_id: str
    name: str
    enabled: bool
    ai_enabled: bool
    event_detection: bool
    is_running: bool
    resolution: tuple
    fps: int

class CameraConfigRequest(BaseModel):
    name: Optional[str] = None
    rtsp_url: Optional[str] = None
    usb_index: Optional[int] = None
    resolution: Optional[tuple] = None
    fps: Optional[int] = None
    enabled: Optional[bool] = None
    ai_enabled: Optional[bool] = None
    event_detection: Optional[bool] = None

class DetectionEventResponse(BaseModel):
    camera_id: str
    event_type: str
    confidence: float
    timestamp: datetime
    data: Dict
    image_path: Optional[str] = None

class ImageCaptureResponse(BaseModel):
    camera_id: str
    success: bool
    image_base64: Optional[str] = None
    timestamp: datetime
    error: Optional[str] = None

@router.on_event("startup")
async def startup_camera_service():
    """Inicializar servicio de cámaras al arrancar"""
    global ai_service
    try:
        # Inicializar servicio de IA
        ai_service = AIService()
        await ai_service.initialize()
        
        # Inicializar servicio de cámaras
        await camera_service.initialize(ai_service)
        
        # Iniciar todas las cámaras
        await camera_service.start_all_cameras()
        
    except Exception as e:
        print(f"Error inicializando servicio de cámaras: {e}")

@router.get("/status", response_model=Dict)
async def get_cameras_status(
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener estado de todas las cámaras"""
    return await camera_service.get_all_cameras_status()

@router.get("/{camera_id}/status", response_model=CameraStatusResponse)
async def get_camera_status(
    camera_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener estado de una cámara específica"""
    status = await camera_service.get_camera_status(camera_id)
    
    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])
    
    return status

@router.post("/{camera_id}/start")
async def start_camera(
    camera_id: str,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Iniciar una cámara específica"""
    success = await camera_service.start_camera(camera_id)
    
    if not success:
        raise HTTPException(
            status_code=400, 
            detail=f"No se pudo iniciar la cámara {camera_id}"
        )
    
    return {"message": f"Cámara {camera_id} iniciada correctamente"}

@router.post("/{camera_id}/stop")
async def stop_camera(
    camera_id: str,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Detener una cámara específica"""
    success = await camera_service.stop_camera(camera_id)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail=f"No se pudo detener la cámara {camera_id}"
        )
    
    return {"message": f"Cámara {camera_id} detenida correctamente"}

@router.post("/start-all")
async def start_all_cameras(
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Iniciar todas las cámaras"""
    success = await camera_service.start_all_cameras()
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="No se pudieron iniciar las cámaras"
        )
    
    return {"message": "Todas las cámaras iniciadas correctamente"}

@router.post("/stop-all")
async def stop_all_cameras(
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Detener todas las cámaras"""
    success = await camera_service.stop_all_cameras()
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="No se pudieron detener las cámaras"
        )
    
    return {"message": "Todas las cámaras detenidas correctamente"}

@router.put("/{camera_id}/config")
async def update_camera_config(
    camera_id: str,
    config: CameraConfigRequest,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Actualizar configuración de una cámara"""
    config_dict = config.dict(exclude_unset=True)
    success = await camera_service.update_camera_config(camera_id, config_dict)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail=f"No se pudo actualizar la configuración de la cámara {camera_id}"
        )
    
    return {"message": f"Configuración de la cámara {camera_id} actualizada correctamente"}

@router.post("/{camera_id}/capture", response_model=ImageCaptureResponse)
async def capture_image(
    camera_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """Capturar imagen de una cámara"""
    try:
        frame = await camera_service.capture_image(camera_id)
        
        if frame is None:
            return ImageCaptureResponse(
                camera_id=camera_id,
                success=False,
                timestamp=datetime.utcnow(),
                error="No se pudo capturar la imagen"
            )
        
        # Convertir frame a base64
        _, buffer = cv2.imencode('.jpg', frame)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return ImageCaptureResponse(
            camera_id=camera_id,
            success=True,
            image_base64=image_base64,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        return ImageCaptureResponse(
            camera_id=camera_id,
            success=False,
            timestamp=datetime.utcnow(),
            error=str(e)
        )

@router.post("/{camera_id}/add-face")
async def add_employee_face(
    camera_id: str,
    employee_id: int,
    employee_name: str,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Agregar cara de empleado usando captura de cámara"""
    try:
        # Capturar imagen
        frame = await camera_service.capture_image(camera_id)
        
        if frame is None:
            raise HTTPException(
                status_code=400,
                detail="No se pudo capturar imagen de la cámara"
            )
        
        # Guardar imagen temporalmente
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            cv2.imwrite(temp_file.name, frame)
            temp_path = temp_file.name
        
        try:
            # Agregar cara al sistema de IA
            success = await ai_service.add_employee_face(
                employee_id, employee_name, temp_path
            )
            
            if success:
                return {"message": f"Cara agregada para {employee_name}"}
            else:
                raise HTTPException(
                    status_code=400,
                    detail="No se pudo procesar la cara en la imagen"
                )
                
        finally:
            # Limpiar archivo temporal
            os.unlink(temp_path)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/events/recent")
async def get_recent_events(
    limit: int = 50,
    event_type: Optional[str] = None,
    camera_id: Optional[str] = None,
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener eventos recientes de detección"""
    # Esta función debería obtener eventos de la base de datos
    # Por ahora retornamos un ejemplo
    return {
        "events": [],
        "total": 0,
        "message": "Funcionalidad en desarrollo"
    }

@router.post("/test-detection")
async def test_detection(
    camera_id: str,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Probar detección de eventos en una cámara"""
    try:
        # Capturar imagen
        frame = await camera_service.capture_image(camera_id)
        
        if frame is None:
            raise HTTPException(
                status_code=400,
                detail="No se pudo capturar imagen"
            )
        
        # Procesar con IA
        if ai_service:
            # Detectar caras
            face_results = await ai_service.recognize_faces_in_image_from_frame(frame)
            
            # Detectar objetos
            object_results = await ai_service.detect_objects_in_image_from_frame(frame)
            
            return {
                "camera_id": camera_id,
                "faces_detected": len(face_results),
                "objects_detected": len(object_results),
                "face_results": face_results,
                "object_results": object_results,
                "timestamp": datetime.utcnow()
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Servicio de IA no disponible"
            )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/system/status")
async def get_system_status(
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener estado del sistema de cámaras"""
    camera_status = await camera_service.get_system_status()
    ai_status = await ai_service.get_system_status() if ai_service else {}
    
    return {
        "camera_service": camera_status,
        "ai_service": ai_status,
        "timestamp": datetime.utcnow()
    }
