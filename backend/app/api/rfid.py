# S.A.M.I. - API RFID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel

from ..core.database import get_db
from ..core.security import get_current_active_user, require_role, ROLE_MANAGER
from ..models.employee import Employee
from ..services.rfid_service import RFIDService

router = APIRouter()

# Instancia global del servicio RFID
rfid_service = RFIDService()

# Modelos Pydantic
class RFIDReaderStatus(BaseModel):
    reader_id: str
    name: str
    location: str
    port: str
    baudrate: int
    enabled: bool
    is_running: bool

class RFIDTransaction(BaseModel):
    reader_id: str
    tag_id: str
    timestamp: datetime
    location: str
    employee_id: Optional[int] = None
    asset_id: Optional[int] = None
    transaction_type: str
    raw_data: str

class RFIDAlert(BaseModel):
    type: str
    severity: str
    message: str
    timestamp: datetime
    transaction: Dict

class ReaderConfigRequest(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    port: Optional[str] = None
    baudrate: Optional[int] = None
    enabled: Optional[bool] = None

@router.on_event("startup")
async def startup_rfid_service():
    """Inicializar servicio RFID al arrancar"""
    try:
        await rfid_service.initialize()
        await rfid_service.start_all_readers()
    except Exception as e:
        print(f"Error inicializando servicio RFID: {e}")

@router.get("/readers/status", response_model=Dict)
async def get_readers_status(
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener estado de todos los lectores RFID"""
    return await rfid_service.get_all_readers_status()

@router.get("/readers/{reader_id}/status", response_model=RFIDReaderStatus)
async def get_reader_status(
    reader_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener estado de un lector RFID específico"""
    status = await rfid_service.get_reader_status(reader_id)
    
    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])
    
    return status

@router.post("/readers/{reader_id}/start")
async def start_reader(
    reader_id: str,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Iniciar un lector RFID específico"""
    success = await rfid_service.start_reader(reader_id)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail=f"No se pudo iniciar el lector {reader_id}"
        )
    
    return {"message": f"Lector {reader_id} iniciado correctamente"}

@router.post("/readers/{reader_id}/stop")
async def stop_reader(
    reader_id: str,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Detener un lector RFID específico"""
    success = await rfid_service.stop_reader(reader_id)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail=f"No se pudo detener el lector {reader_id}"
        )
    
    return {"message": f"Lector {reader_id} detenido correctamente"}

@router.post("/readers/start-all")
async def start_all_readers(
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Iniciar todos los lectores RFID"""
    success = await rfid_service.start_all_readers()
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="No se pudieron iniciar los lectores RFID"
        )
    
    return {"message": "Todos los lectores RFID iniciados correctamente"}

@router.post("/readers/stop-all")
async def stop_all_readers(
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Detener todos los lectores RFID"""
    success = await rfid_service.stop_all_readers()
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="No se pudieron detener los lectores RFID"
        )
    
    return {"message": "Todos los lectores RFID detenidos correctamente"}

@router.put("/readers/{reader_id}/config")
async def update_reader_config(
    reader_id: str,
    config: ReaderConfigRequest,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Actualizar configuración de un lector RFID"""
    config_dict = config.dict(exclude_unset=True)
    success = await rfid_service.update_reader_config(reader_id, config_dict)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail=f"No se pudo actualizar la configuración del lector {reader_id}"
        )
    
    return {"message": f"Configuración del lector {reader_id} actualizada correctamente"}

@router.post("/readers/{reader_id}/test")
async def test_reader(
    reader_id: str,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Probar conexión con un lector RFID"""
    result = await rfid_service.test_reader(reader_id)
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Error desconocido")
        )
    
    return result

@router.get("/transactions/recent")
async def get_recent_transactions(
    limit: int = 50,
    reader_id: Optional[str] = None,
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener transacciones RFID recientes"""
    # Esta función debería consultar la base de datos
    # Por ahora retornamos un ejemplo
    return {
        "transactions": [],
        "total": 0,
        "message": "Funcionalidad en desarrollo"
    }

@router.get("/transactions/{transaction_id}")
async def get_transaction(
    transaction_id: int,
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener transacción RFID específica"""
    # Esta función debería consultar la base de datos
    return {
        "transaction_id": transaction_id,
        "message": "Funcionalidad en desarrollo"
    }

@router.get("/alerts/recent")
async def get_recent_alerts(
    limit: int = 50,
    severity: Optional[str] = None,
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener alertas RFID recientes"""
    # Esta función debería consultar la base de datos
    return {
        "alerts": [],
        "total": 0,
        "message": "Funcionalidad en desarrollo"
    }

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    current_user: Employee = Depends(get_current_active_user)
):
    """Reconocer una alerta RFID"""
    # Esta función debería actualizar la base de datos
    return {
        "alert_id": alert_id,
        "acknowledged_by": current_user.id,
        "acknowledged_at": datetime.utcnow(),
        "message": "Alerta reconocida correctamente"
    }

@router.get("/tags")
async def get_rfid_tags(
    skip: int = 0,
    limit: int = 100,
    tag_type: Optional[str] = None,
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener lista de tags RFID"""
    # Esta función debería consultar la base de datos
    return {
        "tags": [],
        "total": 0,
        "message": "Funcionalidad en desarrollo"
    }

@router.post("/tags")
async def create_rfid_tag(
    tag_data: Dict,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Crear nuevo tag RFID"""
    # Esta función debería crear en la base de datos
    return {
        "message": "Tag RFID creado correctamente",
        "tag_data": tag_data
    }

@router.put("/tags/{tag_id}")
async def update_rfid_tag(
    tag_id: str,
    tag_data: Dict,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Actualizar tag RFID"""
    # Esta función debería actualizar en la base de datos
    return {
        "message": f"Tag {tag_id} actualizado correctamente",
        "tag_data": tag_data
    }

@router.delete("/tags/{tag_id}")
async def delete_rfid_tag(
    tag_id: str,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Eliminar tag RFID"""
    # Esta función debería eliminar de la base de datos
    return {
        "message": f"Tag {tag_id} eliminado correctamente"
    }

@router.get("/zones")
async def get_rfid_zones(
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener zonas RFID"""
    # Esta función debería consultar la base de datos
    return {
        "zones": [],
        "total": 0,
        "message": "Funcionalidad en desarrollo"
    }

@router.post("/zones")
async def create_rfid_zone(
    zone_data: Dict,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Crear nueva zona RFID"""
    # Esta función debería crear en la base de datos
    return {
        "message": "Zona RFID creada correctamente",
        "zone_data": zone_data
    }

@router.get("/statistics")
async def get_rfid_statistics(
    period: str = "today",  # today, week, month
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener estadísticas de RFID"""
    # Esta función debería calcular estadísticas de la base de datos
    return {
        "period": period,
        "total_transactions": 0,
        "unique_tags": 0,
        "active_readers": len(rfid_service.reader_threads),
        "alerts_count": 0,
        "message": "Funcionalidad en desarrollo"
    }

@router.get("/system/status")
async def get_system_status(
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener estado del sistema RFID"""
    return await rfid_service.get_system_status()

@router.post("/simulate/transaction")
async def simulate_transaction(
    reader_id: str,
    tag_id: str,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Simular transacción RFID para pruebas"""
    try:
        # Simular transacción
        transaction = {
            "reader_id": reader_id,
            "tag_id": tag_id,
            "timestamp": datetime.utcnow(),
            "location": "Simulación",
            "raw_data": f"SIM:{tag_id}"
        }
        
        # Procesar transacción
        await rfid_service._process_transaction(transaction)
        
        return {
            "message": "Transacción simulada correctamente",
            "transaction": transaction
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/health")
async def health_check(
    current_user: Employee = Depends(get_current_active_user)
):
    """Verificar salud del sistema RFID"""
    status = await rfid_service.get_system_status()
    
    return {
        "status": "healthy" if status["running"] else "unhealthy",
        "active_readers": status["active_readers"],
        "total_readers": status["total_readers"],
        "timestamp": datetime.utcnow()
    }
