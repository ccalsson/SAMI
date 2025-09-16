# S.A.M.I. - API de Empleados
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from ..core.database import get_db
from ..core.security import get_current_active_user, require_role, ROLE_ADMIN, ROLE_MANAGER
from ..models.employee import Employee, CheckIn, EmployeeRole

router = APIRouter()

# Modelos Pydantic
class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    employee_id: str
    role: str = "operator"
    department: Optional[str] = None
    rfid_tag: Optional[str] = None

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    rfid_tag: Optional[str] = None

class EmployeeResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    employee_id: str
    role: str
    department: Optional[str]
    rfid_tag: Optional[str]
    is_present: bool
    last_check_in: Optional[datetime]
    last_check_out: Optional[datetime]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class CheckInCreate(BaseModel):
    employee_id: int
    location: Optional[str] = None
    method: str = "manual"  # 'rfid', 'facial', 'manual'

class CheckInResponse(BaseModel):
    id: int
    employee_id: int
    check_in_time: datetime
    check_out_time: Optional[datetime]
    location: Optional[str]
    method: str
    employee: EmployeeResponse
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[EmployeeResponse])
async def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    role: Optional[str] = None,
    department: Optional[str] = None,
    is_present: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener lista de empleados con filtros"""
    query = db.query(Employee).filter(Employee.is_deleted == False)
    
    # Filtros
    if search:
        query = query.filter(
            or_(
                Employee.first_name.ilike(f"%{search}%"),
                Employee.last_name.ilike(f"%{search}%"),
                Employee.employee_id.ilike(f"%{search}%"),
                Employee.email.ilike(f"%{search}%")
            )
        )
    
    if role:
        query = query.filter(Employee.role == role)
    
    if department:
        query = query.filter(Employee.department == department)
    
    if is_present is not None:
        query = query.filter(Employee.is_present == is_present)
    
    employees = query.offset(skip).limit(limit).all()
    return employees

@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener empleado por ID"""
    employee = db.query(Employee).filter(
        and_(Employee.id == employee_id, Employee.is_deleted == False)
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return employee

@router.post("/", response_model=EmployeeResponse)
async def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(ROLE_ADMIN))
):
    """Crear nuevo empleado"""
    # Verificar si el email ya existe
    existing_employee = db.query(Employee).filter(Employee.email == employee.email).first()
    if existing_employee:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Verificar si el employee_id ya existe
    existing_id = db.query(Employee).filter(Employee.employee_id == employee.employee_id).first()
    if existing_id:
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    
    # Verificar si el RFID tag ya existe
    if employee.rfid_tag:
        existing_rfid = db.query(Employee).filter(Employee.rfid_tag == employee.rfid_tag).first()
        if existing_rfid:
            raise HTTPException(status_code=400, detail="RFID tag already assigned")
    
    db_employee = Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    
    return db_employee

@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee_update: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Actualizar empleado"""
    db_employee = db.query(Employee).filter(
        and_(Employee.id == employee_id, Employee.is_deleted == False)
    ).first()
    
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Verificar email único
    if employee_update.email and employee_update.email != db_employee.email:
        existing = db.query(Employee).filter(Employee.email == employee_update.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Verificar RFID único
    if employee_update.rfid_tag and employee_update.rfid_tag != db_employee.rfid_tag:
        existing = db.query(Employee).filter(Employee.rfid_tag == employee_update.rfid_tag).first()
        if existing:
            raise HTTPException(status_code=400, detail="RFID tag already assigned")
    
    # Actualizar campos
    update_data = employee_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_employee, field, value)
    
    db.commit()
    db.refresh(db_employee)
    
    return db_employee

@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(ROLE_ADMIN))
):
    """Eliminar empleado (soft delete)"""
    db_employee = db.query(Employee).filter(
        and_(Employee.id == employee_id, Employee.is_deleted == False)
    ).first()
    
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Soft delete
    db_employee.is_deleted = True
    db_employee.deleted_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Employee deleted successfully"}

@router.post("/check-in", response_model=CheckInResponse)
async def check_in_employee(
    check_in: CheckInCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_user)
):
    """Registrar entrada de empleado"""
    # Verificar que el empleado existe
    employee = db.query(Employee).filter(
        and_(Employee.id == check_in.employee_id, Employee.is_deleted == False)
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Verificar que no esté ya presente
    if employee.is_present:
        raise HTTPException(status_code=400, detail="Employee is already checked in")
    
    # Crear registro de check-in
    db_check_in = CheckIn(
        employee_id=check_in.employee_id,
        check_in_time=datetime.utcnow(),
        location=check_in.location,
        method=check_in.method
    )
    
    # Actualizar estado del empleado
    employee.is_present = True
    employee.last_check_in = datetime.utcnow()
    
    db.add(db_check_in)
    db.commit()
    db.refresh(db_check_in)
    
    return db_check_in

@router.post("/check-out", response_model=CheckInResponse)
async def check_out_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_user)
):
    """Registrar salida de empleado"""
    # Verificar que el empleado existe
    employee = db.query(Employee).filter(
        and_(Employee.id == employee_id, Employee.is_deleted == False)
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Verificar que esté presente
    if not employee.is_present:
        raise HTTPException(status_code=400, detail="Employee is not checked in")
    
    # Obtener el último check-in
    last_check_in = db.query(CheckIn).filter(
        and_(
            CheckIn.employee_id == employee_id,
            CheckIn.check_out_time.is_(None)
        )
    ).first()
    
    if not last_check_in:
        raise HTTPException(status_code=400, detail="No active check-in found")
    
    # Actualizar check-in
    last_check_in.check_out_time = datetime.utcnow()
    
    # Actualizar estado del empleado
    employee.is_present = False
    employee.last_check_out = datetime.utcnow()
    
    db.commit()
    db.refresh(last_check_in)
    
    return last_check_in

@router.get("/{employee_id}/check-ins", response_model=List[CheckInResponse])
async def get_employee_check_ins(
    employee_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener historial de check-ins de un empleado"""
    check_ins = db.query(CheckIn).filter(CheckIn.employee_id == employee_id)\
        .order_by(CheckIn.check_in_time.desc())\
        .offset(skip).limit(limit).all()
    
    return check_ins

@router.get("/present/count")
async def get_present_employees_count(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener conteo de empleados presentes"""
    total_present = db.query(Employee).filter(
        and_(Employee.is_present == True, Employee.is_deleted == False)
    ).count()
    
    total_employees = db.query(Employee).filter(Employee.is_deleted == False).count()
    
    return {
        "present": total_present,
        "total": total_employees,
        "absent": total_employees - total_present
    }
