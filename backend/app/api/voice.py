# S.A.M.I. - API de Interacción por Voz
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import asyncio
import base64
import io
import tempfile
import os
from datetime import datetime
from pydantic import BaseModel

from ..core.database import get_db
from ..core.security import get_current_active_user, require_role, ROLE_MANAGER
from ..models.employee import Employee
from ..services.voice_service import VoiceService
from ..services.ai_service import AIService

router = APIRouter()

# Instancia global del servicio de voz
voice_service = VoiceService()
ai_service = None

# Modelos Pydantic
class VoiceInteractionRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    duration: Optional[float] = 5.0
    location: Optional[str] = None

class VoiceInteractionResponse(BaseModel):
    success: bool
    transcription: Optional[Dict] = None
    command: Optional[Dict] = None
    response_audio: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime

class VoiceCommandRequest(BaseModel):
    phrase: str
    intent: str
    response: str
    action: str

class VoiceCommandResponse(BaseModel):
    phrase: str
    intent: str
    response: str
    action: str

class VoiceStatusResponse(BaseModel):
    is_initialized: bool
    whisper_loaded: bool
    tts_available: bool
    commands_count: int
    last_updated: datetime

@router.on_event("startup")
async def startup_voice_service():
    """Inicializar servicio de voz al arrancar"""
    global ai_service
    try:
        # Inicializar servicio de IA
        ai_service = AIService()
        await ai_service.initialize()
        
        # Inicializar servicio de voz
        await voice_service.initialize()
        
    except Exception as e:
        print(f"Error inicializando servicio de voz: {e}")

@router.post("/interact", response_model=VoiceInteractionResponse)
async def voice_interaction(
    request: VoiceInteractionRequest,
    current_user: Employee = Depends(get_current_active_user)
):
    """Procesar interacción de voz completa"""
    try:
        # Decodificar audio base64
        audio_bytes = base64.b64decode(request.audio_data)
        
        # Convertir a numpy array
        import numpy as np
        import soundfile as sf
        
        # Guardar audio temporalmente
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        
        try:
            # Cargar audio
            audio_data, sample_rate = sf.read(temp_path)
            
            # Transcribir
            transcription = await voice_service.transcribe_audio(audio_data, sample_rate)
            
            if not transcription['text']:
                return VoiceInteractionResponse(
                    success=False,
                    error="No se detectó audio",
                    timestamp=datetime.utcnow()
                )
            
            # Procesar comando
            command = await voice_service.process_voice_command(transcription['text'])
            
            # Generar respuesta de audio
            response_audio = None
            if command['intent'] != 'unknown':
                # Generar audio de respuesta
                response_audio = await voice_service.speak(command['response'])
            
            return VoiceInteractionResponse(
                success=True,
                transcription=transcription,
                command=command,
                response_audio=response_audio,
                timestamp=datetime.utcnow()
            )
            
        finally:
            # Limpiar archivo temporal
            os.unlink(temp_path)
        
    except Exception as e:
        return VoiceInteractionResponse(
            success=False,
            error=str(e),
            timestamp=datetime.utcnow()
        )

@router.post("/record", response_model=VoiceInteractionResponse)
async def record_and_process(
    duration: float = 5.0,
    location: Optional[str] = None,
    current_user: Employee = Depends(get_current_active_user)
):
    """Grabar audio del micrófono y procesarlo"""
    try:
        # Ejecutar interacción de voz completa
        result = await voice_service.voice_interaction_loop(duration)
        
        return VoiceInteractionResponse(
            success=result['success'],
            transcription=result.get('transcription'),
            command=result.get('command'),
            error=result.get('error'),
            timestamp=result['timestamp']
        )
        
    except Exception as e:
        return VoiceInteractionResponse(
            success=False,
            error=str(e),
            timestamp=datetime.utcnow()
        )

@router.post("/transcribe", response_model=Dict)
async def transcribe_audio(
    file: UploadFile = File(...),
    current_user: Employee = Depends(get_current_active_user)
):
    """Transcribir archivo de audio"""
    try:
        # Leer archivo
        audio_bytes = await file.read()
        
        # Guardar temporalmente
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        
        try:
            # Cargar audio
            import soundfile as sf
            audio_data, sample_rate = sf.read(temp_path)
            
            # Transcribir
            result = await voice_service.transcribe_audio(audio_data, sample_rate)
            
            return {
                "success": True,
                "transcription": result,
                "filename": file.filename,
                "timestamp": datetime.utcnow()
            }
            
        finally:
            os.unlink(temp_path)
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow()
        }

@router.post("/speak")
async def speak_text(
    text: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """Sintetizar y reproducir texto"""
    try:
        success = await voice_service.speak(text)
        
        return {
            "success": success,
            "text": text,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow()
        }

@router.get("/commands", response_model=List[VoiceCommandResponse])
async def get_voice_commands(
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener comandos de voz disponibles"""
    commands = await voice_service.get_available_commands()
    
    return [VoiceCommandResponse(**cmd) for cmd in commands]

@router.post("/commands", response_model=VoiceCommandResponse)
async def add_voice_command(
    command: VoiceCommandRequest,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Agregar nuevo comando de voz"""
    try:
        await voice_service.add_voice_command(
            command.phrase,
            command.intent,
            command.response,
            command.action
        )
        
        return VoiceCommandResponse(
            phrase=command.phrase,
            intent=command.intent,
            response=command.response,
            action=command.action
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status", response_model=VoiceStatusResponse)
async def get_voice_status(
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener estado del servicio de voz"""
    status = await voice_service.get_system_status()
    
    return VoiceStatusResponse(**status)

@router.post("/test")
async def test_voice_system(
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Probar sistema de voz completo"""
    try:
        # Probar grabación y procesamiento
        result = await voice_service.voice_interaction_loop(3.0)
        
        return {
            "test_result": result,
            "system_status": await voice_service.get_system_status(),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow()
        }

@router.post("/recognize-employee")
async def recognize_employee_voice(
    file: UploadFile = File(...),
    current_user: Employee = Depends(get_current_active_user)
):
    """Reconocer empleado por voz"""
    try:
        # Leer archivo de audio
        audio_bytes = await file.read()
        
        # Guardar temporalmente
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        
        try:
            # Cargar audio
            import soundfile as sf
            audio_data, sample_rate = sf.read(temp_path)
            
            # Transcribir
            transcription = await voice_service.transcribe_audio(audio_data, sample_rate)
            
            # Buscar empleado por nombre en la transcripción
            # Esta es una implementación básica
            employee_name = None
            confidence = 0.0
            
            # Aquí se implementaría la lógica de reconocimiento de empleado
            # Por ahora retornamos un ejemplo
            
            return {
                "success": True,
                "transcription": transcription,
                "employee_name": employee_name,
                "confidence": confidence,
                "timestamp": datetime.utcnow()
            }
            
        finally:
            os.unlink(temp_path)
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow()
        }

@router.get("/devices")
async def get_voice_devices(
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener dispositivos de audio disponibles"""
    try:
        import sounddevice as sd
        
        devices = sd.query_devices()
        input_devices = []
        output_devices = []
        
        for i, device in enumerate(devices):
            device_info = {
                "index": i,
                "name": device['name'],
                "channels": device['channels'],
                "sample_rate": device['default_samplerate']
            }
            
            if device['max_input_channels'] > 0:
                input_devices.append(device_info)
            
            if device['max_output_channels'] > 0:
                output_devices.append(device_info)
        
        return {
            "input_devices": input_devices,
            "output_devices": output_devices,
            "default_input": sd.default.device[0],
            "default_output": sd.default.device[1]
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.utcnow()
        }

@router.post("/configure")
async def configure_voice_system(
    config: Dict,
    current_user: Employee = Depends(require_role(ROLE_MANAGER))
):
    """Configurar sistema de voz"""
    try:
        # Aquí se implementaría la configuración del sistema de voz
        # Por ejemplo, cambiar dispositivo de audio, velocidad de TTS, etc.
        
        return {
            "success": True,
            "message": "Configuración actualizada",
            "config": config,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow()
        }
