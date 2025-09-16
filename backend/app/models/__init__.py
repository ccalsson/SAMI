# S.A.M.I. - Modelos de Base de Datos
from .base import Base
from .employee import Employee
from .asset import Asset, AssetType, AssetLocation
from .project import Project, ProjectPhase, ProjectExpense
from .event import Event, EventType, EventStatus
from .fuel import FuelTransaction, FuelTank
from .gps import GPSLocation, Vehicle
from .voice import VoiceInteraction, VoiceCommand
from .report import Report, ReportTemplate
from .rfid import RFIDTag, RFIDTransaction

__all__ = [
    "Base",
    "Employee",
    "Asset",
    "AssetType", 
    "AssetLocation",
    "Project",
    "ProjectPhase",
    "ProjectExpense",
    "Event",
    "EventType",
    "EventStatus",
    "FuelTransaction",
    "FuelTank",
    "GPSLocation",
    "Vehicle",
    "VoiceInteraction",
    "VoiceCommand",
    "Report",
    "ReportTemplate",
    "RFIDTag",
    "RFIDTransaction"
]
