# S.A.M.I. - API de Reportes
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime, date, timedelta
from pydantic import BaseModel

from ..core.database import get_db
from ..core.security import get_current_active_user, require_role, ROLE_MANAGER
from ..models.employee import Employee
from ..services.report_service import ReportService

router = APIRouter()

# Instancia global del servicio de reportes
report_service = ReportService()

# Modelos Pydantic
class ReportGenerationRequest(BaseModel):
    template_name: str
    report_date: Optional[date] = None
    recipients: Optional[List[str]] = None
    parameters: Optional[Dict] = None

class ReportGenerationResponse(BaseModel):
    success: bool
    template_name: str
    report_date: date
    file_path: Optional[str] = None
    recipients: List[str]
    generated_at: datetime
    error: Optional[str] = None

class ReportTemplate(BaseModel):
    name: str
    report_type: str
    category: str
    format: str
    is_auto_generated: bool
    generation_schedule: Optional[str] = None
    data_sources: List[str]
    default_recipients: List[str]

class ReportSchedule(BaseModel):
    name: str
    template_name: str
    cron_expression: str
    is_active: bool

@router.on_event("startup")
async def startup_report_service():
    """Inicializar servicio de reportes al arrancar"""
    try:
        await report_service.initialize()
    except Exception as e:
        print(f"Error inicializando servicio de reportes: {e}")

@router.get("/templates", response_model=List[ReportTemplate])
async def get_report_templates(
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener plantillas de reportes disponibles"""
    templates = await report_service.get_available_templates()
    return [ReportTemplate(**template) for template in templates]

@router.get("/templates/{template_name}")
async def get_report_template(
    template_name: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener plantilla de reporte específica"""
    templates = await report_service.get_available_templates()
    
    for template in templates:
        if template["name"] == template_name:
            return template
    
    raise HTTPException(status_code=404, detail="Plantilla no encontrada")

@router.post("/generate", response_model=ReportGenerationResponse)
async def generate_report(
    request: ReportGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Generar reporte específico"""
    try:
        # Usar fecha actual si no se especifica
        report_date = request.report_date or date.today()
        
        # Generar reporte
        result = await report_service.generate_report(
            template_name=request.template_name,
            report_date=report_date,
            recipients=request.recipients or []
        )
        
        return ReportGenerationResponse(**result)
        
    except Exception as e:
        return ReportGenerationResponse(
            success=False,
            template_name=request.template_name,
            report_date=request.report_date or date.today(),
            error=str(e),
            generated_at=datetime.utcnow()
        )

@router.post("/generate/daily")
async def generate_daily_report(
    report_date: Optional[date] = None,
    recipients: Optional[List[str]] = None,
    background_tasks: BackgroundTasks = None,
    current_user: Employee = Depends(get_current_active_user)
):
    """Generar reporte diario operativo"""
    try:
        report_date = report_date or date.today()
        
        result = await report_service.generate_report(
            template_name="Reporte Diario Operativo",
            report_date=report_date,
            recipients=recipients or []
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/generate/weekly")
async def generate_weekly_report(
    week_start: Optional[date] = None,
    recipients: Optional[List[str]] = None,
    background_tasks: BackgroundTasks = None,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Generar reporte semanal de proyectos"""
    try:
        # Calcular inicio de semana si no se especifica
        if not week_start:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
        
        result = await report_service.generate_report(
            template_name="Reporte Semanal de Proyectos",
            report_date=week_start,
            recipients=recipients or []
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/generate/monthly")
async def generate_monthly_report(
    month: Optional[int] = None,
    year: Optional[int] = None,
    recipients: Optional[List[str]] = None,
    background_tasks: BackgroundTasks = None,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Generar reporte mensual financiero"""
    try:
        # Usar mes y año actual si no se especifican
        if not month or not year:
            today = date.today()
            month = month or today.month
            year = year or today.year
        
        # Crear fecha del primer día del mes
        report_date = date(year, month, 1)
        
        result = await report_service.generate_report(
            template_name="Reporte Mensual Financiero",
            report_date=report_date,
            recipients=recipients or []
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/history")
async def get_report_history(
    limit: int = Query(50, ge=1, le=200),
    template_name: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener historial de reportes generados"""
    try:
        history = await report_service.get_report_history(limit)
        
        # Filtrar por plantilla si se especifica
        if template_name:
            history = [h for h in history if h.get("template_name") == template_name]
        
        # Filtrar por fechas si se especifican
        if start_date:
            history = [h for h in history if h.get("report_date") >= start_date]
        if end_date:
            history = [h for h in history if h.get("report_date") <= end_date]
        
        return {
            "reports": history,
            "total": len(history),
            "filters": {
                "template_name": template_name,
                "start_date": start_date,
                "end_date": end_date
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/schedules", response_model=List[ReportSchedule])
async def get_report_schedules(
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener programaciones de reportes"""
    schedules = []
    for schedule in report_service.schedules.values():
        schedules.append(ReportSchedule(**schedule))
    
    return schedules

@router.post("/schedules")
async def create_report_schedule(
    schedule: ReportSchedule,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Crear nueva programación de reporte"""
    try:
        # Verificar que la plantilla existe
        templates = await report_service.get_available_templates()
        template_names = [t["name"] for t in templates]
        
        if schedule.template_name not in template_names:
            raise HTTPException(
                status_code=400,
                detail=f"Plantilla no encontrada: {schedule.template_name}"
            )
        
        # Agregar programación
        report_service.schedules[schedule.name] = schedule.dict()
        
        return {
            "message": f"Programación '{schedule.name}' creada correctamente",
            "schedule": schedule
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/schedules/{schedule_name}")
async def update_report_schedule(
    schedule_name: str,
    schedule: ReportSchedule,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Actualizar programación de reporte"""
    try:
        if schedule_name not in report_service.schedules:
            raise HTTPException(status_code=404, detail="Programación no encontrada")
        
        # Actualizar programación
        report_service.schedules[schedule_name] = schedule.dict()
        
        return {
            "message": f"Programación '{schedule_name}' actualizada correctamente",
            "schedule": schedule
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/schedules/{schedule_name}")
async def delete_report_schedule(
    schedule_name: str,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Eliminar programación de reporte"""
    try:
        if schedule_name not in report_service.schedules:
            raise HTTPException(status_code=404, detail="Programación no encontrada")
        
        # Eliminar programación
        del report_service.schedules[schedule_name]
        
        return {
            "message": f"Programación '{schedule_name}' eliminada correctamente"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/schedules/{schedule_name}/activate")
async def activate_schedule(
    schedule_name: str,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Activar programación de reporte"""
    try:
        if schedule_name not in report_service.schedules:
            raise HTTPException(status_code=404, detail="Programación no encontrada")
        
        report_service.schedules[schedule_name]["is_active"] = True
        
        return {
            "message": f"Programación '{schedule_name}' activada correctamente"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/schedules/{schedule_name}/deactivate")
async def deactivate_schedule(
    schedule_name: str,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Desactivar programación de reporte"""
    try:
        if schedule_name not in report_service.schedules:
            raise HTTPException(status_code=404, detail="Programación no encontrada")
        
        report_service.schedules[schedule_name]["is_active"] = False
        
        return {
            "message": f"Programación '{schedule_name}' desactivada correctamente"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/statistics")
async def get_report_statistics(
    period: str = Query("month", regex="^(week|month|year)$"),
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener estadísticas de reportes"""
    try:
        # Calcular período
        end_date = date.today()
        
        if period == "week":
            start_date = end_date - timedelta(weeks=1)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        elif period == "year":
            start_date = end_date - timedelta(days=365)
        
        # Obtener historial
        history = await report_service.get_report_history(1000)
        
        # Filtrar por período
        period_reports = [
            h for h in history 
            if h.get("report_date") and start_date <= h["report_date"] <= end_date
        ]
        
        # Calcular estadísticas
        total_reports = len(period_reports)
        successful_reports = len([h for h in period_reports if h.get("success", False)])
        failed_reports = total_reports - successful_reports
        
        # Agrupar por plantilla
        template_counts = {}
        for report in period_reports:
            template = report.get("template_name", "Unknown")
            template_counts[template] = template_counts.get(template, 0) + 1
        
        return {
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "total_reports": total_reports,
            "successful_reports": successful_reports,
            "failed_reports": failed_reports,
            "success_rate": (successful_reports / total_reports * 100) if total_reports > 0 else 0,
            "template_breakdown": template_counts,
            "active_schedules": len([s for s in report_service.schedules.values() if s["is_active"]]),
            "total_templates": len(report_service.templates)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/system/status")
async def get_system_status(
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener estado del sistema de reportes"""
    return await report_service.get_system_status()

@router.post("/test/email")
async def test_email_configuration(
    recipients: List[str],
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Probar configuración de email"""
    try:
        # Crear reporte de prueba
        test_data = {
            "test": True,
            "message": "Este es un reporte de prueba para verificar la configuración de email",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Generar reporte de prueba
        result = await report_service.generate_report(
            template_name="Reporte Diario Operativo",
            report_date=date.today(),
            recipients=recipients
        )
        
        return {
            "success": result["success"],
            "message": "Email de prueba enviado correctamente" if result["success"] else "Error enviando email de prueba",
            "recipients": recipients,
            "error": result.get("error")
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": "Error en configuración de email",
            "error": str(e)
        }

@router.get("/health")
async def health_check(
    current_user: Employee = Depends(get_current_active_user)
):
    """Verificar salud del sistema de reportes"""
    status = await report_service.get_system_status()
    
    return {
        "status": "healthy" if status["running"] else "unhealthy",
        "templates_count": status["templates_count"],
        "active_schedules": status["active_schedules"],
        "timestamp": datetime.utcnow()
    }
