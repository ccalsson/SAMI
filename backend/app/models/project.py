# S.A.M.I. - Modelos de Proyectos
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float, Enum, Date
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, SoftDeleteMixin
import enum

class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ProjectPhase(str, enum.Enum):
    PREPARATION = "preparation"
    EXCAVATION = "excavation"
    LEVELING = "leveling"
    COMPACTION = "compaction"
    FINISHING = "finishing"
    CLEANUP = "cleanup"

class Project(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "projects"
    
    # Información básica
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    project_code = Column(String(50), unique=True, nullable=False, index=True)
    client_name = Column(String(200), nullable=True)
    client_contact = Column(String(200), nullable=True)
    
    # Fechas
    start_date = Column(Date, nullable=True)
    planned_end_date = Column(Date, nullable=True)
    actual_end_date = Column(Date, nullable=True)
    
    # Estado y fase
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING)
    current_phase = Column(Enum(ProjectPhase), default=ProjectPhase.PREPARATION)
    
    # Presupuesto
    budget_total = Column(Float, nullable=True)
    budget_fuel = Column(Float, nullable=True)
    budget_equipment = Column(Float, nullable=True)
    budget_labor = Column(Float, nullable=True)
    
    # Costos reales
    actual_cost_fuel = Column(Float, default=0.0)
    actual_cost_equipment = Column(Float, default=0.0)
    actual_cost_labor = Column(Float, default=0.0)
    actual_cost_total = Column(Float, default=0.0)
    
    # Ubicación
    location_name = Column(String(200), nullable=True)
    address = Column(String(300), nullable=True)
    gps_latitude = Column(Float, nullable=True)
    gps_longitude = Column(Float, nullable=True)
    
    # Progreso
    progress_percentage = Column(Float, default=0.0)
    hours_planned = Column(Float, nullable=True)
    hours_actual = Column(Float, default=0.0)
    
    # Notas y observaciones
    notes = Column(Text, nullable=True)
    special_requirements = Column(Text, nullable=True)
    
    # Relaciones
    phases = relationship("ProjectPhase", back_populates="project")
    expenses = relationship("ProjectExpense", back_populates="project")
    assigned_assets = relationship("ProjectAsset", back_populates="project")
    assigned_employees = relationship("ProjectEmployee", back_populates="project")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', code='{self.project_code}', status='{self.status}')>"
    
    @property
    def budget_variance(self):
        if self.budget_total and self.actual_cost_total:
            return self.actual_cost_total - self.budget_total
        return 0.0
    
    @property
    def is_over_budget(self):
        return self.budget_variance > 0

class ProjectPhase(Base, TimestampMixin):
    __tablename__ = "project_phases"
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    phase_name = Column(Enum(ProjectPhase), nullable=False)
    phase_order = Column(Integer, nullable=False)
    
    # Fechas
    planned_start_date = Column(Date, nullable=True)
    planned_end_date = Column(Date, nullable=True)
    actual_start_date = Column(Date, nullable=True)
    actual_end_date = Column(Date, nullable=True)
    
    # Progreso
    progress_percentage = Column(Float, default=0.0)
    hours_planned = Column(Float, nullable=True)
    hours_actual = Column(Float, default=0.0)
    
    # Notas
    notes = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    
    # Relaciones
    project = relationship("Project", back_populates="phases")
    
    def __repr__(self):
        return f"<ProjectPhase(project_id={self.project_id}, phase='{self.phase_name}', progress={self.progress_percentage}%)>"

class ProjectExpense(Base, TimestampMixin):
    __tablename__ = "project_expenses"
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    expense_type = Column(String(50), nullable=False)  # 'fuel', 'equipment', 'labor', 'material', 'other'
    description = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    
    # Fecha y ubicación
    expense_date = Column(Date, nullable=False)
    location = Column(String(200), nullable=True)
    
    # Documentación
    receipt_number = Column(String(100), nullable=True)
    receipt_image_path = Column(String(300), nullable=True)
    
    # Aprobación
    is_approved = Column(Boolean, default=False)
    approved_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Notas
    notes = Column(Text, nullable=True)
    
    # Relaciones
    project = relationship("Project", back_populates="expenses")
    approved_by = relationship("Employee")
    
    def __repr__(self):
        return f"<ProjectExpense(project_id={self.project_id}, type='{self.expense_type}', amount={self.amount})>"

class ProjectAsset(Base, TimestampMixin):
    __tablename__ = "project_assets"
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    assigned_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=True)
    
    # Uso
    hours_used = Column(Float, default=0.0)
    fuel_consumed = Column(Float, default=0.0)
    
    # Relaciones
    project = relationship("Project", back_populates="assigned_assets")
    asset = relationship("Asset")
    
    def __repr__(self):
        return f"<ProjectAsset(project_id={self.project_id}, asset_id={self.asset_id})>"

class ProjectEmployee(Base, TimestampMixin):
    __tablename__ = "project_employees"
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    role = Column(String(50), nullable=False)  # 'supervisor', 'operator', 'helper'
    assigned_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    
    # Horas trabajadas
    hours_planned = Column(Float, nullable=True)
    hours_actual = Column(Float, default=0.0)
    hourly_rate = Column(Float, nullable=True)
    
    # Relaciones
    project = relationship("Project", back_populates="assigned_employees")
    employee = relationship("Employee")
    
    def __repr__(self):
        return f"<ProjectEmployee(project_id={self.project_id}, employee_id={self.employee_id}, role='{self.role}')>"
