# S.A.M.I. - Modelo de Empleado
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, SoftDeleteMixin
from enum import Enum

class EmployeeRole(str, Enum):
    OPERATOR = "operator"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"
    MANAGER = "manager"

class Employee(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "employees"
    
    # Información personal
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Información laboral
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    role = Column(String(20), nullable=False, default=EmployeeRole.OPERATOR)
    department = Column(String(100), nullable=True)
    hire_date = Column(DateTime, nullable=True)
    
    # Identificación
    rfid_tag = Column(String(50), unique=True, nullable=True, index=True)
    face_encoding = Column(Text, nullable=True)  # Encoding facial para reconocimiento
    
    # Estado
    is_present = Column(Boolean, default=False)
    last_check_in = Column(DateTime, nullable=True)
    last_check_out = Column(DateTime, nullable=True)
    
    # Relaciones
    check_ins = relationship("CheckIn", back_populates="employee")
    asset_transactions = relationship("AssetTransaction", back_populates="employee")
    voice_interactions = relationship("VoiceInteraction", back_populates="employee")
    
    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.first_name} {self.last_name}', employee_id='{self.employee_id}')>"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_checked_in(self):
        return self.is_present and self.last_check_in and (
            not self.last_check_out or self.last_check_in > self.last_check_out
        )

class CheckIn(Base, TimestampMixin):
    __tablename__ = "check_ins"
    
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    check_in_time = Column(DateTime, nullable=False)
    check_out_time = Column(DateTime, nullable=True)
    location = Column(String(100), nullable=True)
    method = Column(String(20), nullable=False)  # 'rfid', 'facial', 'manual'
    
    # Relaciones
    employee = relationship("Employee", back_populates="check_ins")
    
    def __repr__(self):
        return f"<CheckIn(employee_id={self.employee_id}, check_in='{self.check_in_time}')>"
