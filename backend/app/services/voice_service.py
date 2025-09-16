# S.A.M.I. - Servicio de Interacción por Voz
import whisper
import pyttsx3
import sounddevice as sd
import numpy as np
import asyncio
import logging
import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import wave
import tempfile

from ..core.config import settings

logger = logging.getLogger(__name__)

class VoiceService:
    """Servicio de interacción por voz con Whisper y TTS"""
    
    def __init__(self):
        self.whisper_model = None
        self.tts_engine = None
        self.voice_commands = {}
        self.is_initialized = False
        
    async def initialize(self):
        """Inicializar el servicio de voz"""
        try:
            # Inicializar Whisper
            model_path = os.path.join(settings.voice_model_path, "base.pt")
            if os.path.exists(model_path):
                self.whisper_model = whisper.load_model(model_path)
            else:
                self.whisper_model = whisper.load_model("base")
            
            # Inicializar TTS
            self.tts_engine = pyttsx3.init()
            self._configure_tts()
            
            # Cargar comandos de voz
            await self.load_voice_commands()
            
            self.is_initialized = True
            logger.info("Servicio de voz inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando servicio de voz: {e}")
            raise
    
    def _configure_tts(self):
        """Configurar el motor de TTS"""
        try:
            # Configurar voz en español
            voices = self.tts_engine.getProperty('voices')
            spanish_voice = None
            
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
                    spanish_voice = voice
                    break
            
            if spanish_voice:
                self.tts_engine.setProperty('voice', spanish_voice.id)
            
            # Configurar velocidad y volumen
            self.tts_engine.setProperty('rate', 150)  # Palabras por minuto
            self.tts_engine.setProperty('volume', 0.8)  # Volumen 0-1
            
        except Exception as e:
            logger.warning(f"Error configurando TTS: {e}")
    
    async def load_voice_commands(self):
        """Cargar comandos de voz predefinidos"""
        self.voice_commands = {
            # Comandos de información
            "cuanto combustible queda": {
                "intent": "fuel_level",
                "response": "Consultando nivel de combustible...",
                "action": "get_fuel_level"
            },
            "cuantos empleados hay": {
                "intent": "employee_count",
                "response": "Consultando empleados presentes...",
                "action": "get_employee_count"
            },
            "donde esta": {
                "intent": "asset_location",
                "response": "Consultando ubicación de activos...",
                "action": "get_asset_location"
            },
            "estado del proyecto": {
                "intent": "project_status",
                "response": "Consultando estado del proyecto...",
                "action": "get_project_status"
            },
            
            # Comandos de control
            "registrar entrada": {
                "intent": "check_in",
                "response": "Registrando entrada...",
                "action": "check_in_employee"
            },
            "registrar salida": {
                "intent": "check_out",
                "response": "Registrando salida...",
                "action": "check_out_employee"
            },
            "reportar problema": {
                "intent": "report_issue",
                "response": "¿Qué problema quieres reportar?",
                "action": "report_issue"
            },
            
            # Comandos de sistema
            "estado del sistema": {
                "intent": "system_status",
                "response": "Consultando estado del sistema...",
                "action": "get_system_status"
            },
            "ayuda": {
                "intent": "help",
                "response": "Puedo ayudarte con información sobre combustible, empleados, activos y proyectos.",
                "action": "show_help"
            }
        }
    
    async def record_audio(self, duration: float = 5.0, sample_rate: int = 16000) -> np.ndarray:
        """Grabar audio del micrófono"""
        try:
            logger.info(f"Grabando audio por {duration} segundos...")
            
            # Grabar audio
            audio_data = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype=np.float32
            )
            sd.wait()  # Esperar a que termine la grabación
            
            return audio_data.flatten()
            
        except Exception as e:
            logger.error(f"Error grabando audio: {e}")
            raise
    
    async def transcribe_audio(self, audio_data: np.ndarray, sample_rate: int = 16000) -> Dict:
        """Transcribir audio usando Whisper"""
        try:
            if not self.whisper_model:
                raise Exception("Modelo Whisper no inicializado")
            
            # Guardar audio temporalmente
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                # Convertir a formato WAV
                audio_int16 = (audio_data * 32767).astype(np.int16)
                
                with wave.open(temp_file.name, 'w') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(audio_int16.tobytes())
                
                # Transcribir con Whisper
                result = self.whisper_model.transcribe(temp_file.name, language="es")
                
                # Limpiar archivo temporal
                os.unlink(temp_file.name)
            
            return {
                'text': result['text'].strip(),
                'language': result.get('language', 'es'),
                'confidence': 0.8,  # Whisper no proporciona confianza directamente
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error transcribiendo audio: {e}")
            return {
                'text': '',
                'language': 'es',
                'confidence': 0.0,
                'error': str(e),
                'timestamp': datetime.utcnow()
            }
    
    async def process_voice_command(self, text: str) -> Dict:
        """Procesar comando de voz"""
        try:
            text_lower = text.lower().strip()
            
            # Buscar comando coincidente
            best_match = None
            best_score = 0
            
            for command, config in self.voice_commands.items():
                # Calcular similitud simple
                score = self._calculate_similarity(text_lower, command)
                if score > best_score and score > 0.6:  # Umbral de similitud
                    best_score = score
                    best_match = config
            
            if best_match:
                return {
                    'intent': best_match['intent'],
                    'action': best_match['action'],
                    'response': best_match['response'],
                    'confidence': best_score,
                    'original_text': text,
                    'timestamp': datetime.utcnow()
                }
            else:
                return {
                    'intent': 'unknown',
                    'action': 'unknown',
                    'response': 'No entendí el comando. ¿Puedes repetirlo?',
                    'confidence': 0.0,
                    'original_text': text,
                    'timestamp': datetime.utcnow()
                }
                
        except Exception as e:
            logger.error(f"Error procesando comando de voz: {e}")
            return {
                'intent': 'error',
                'action': 'error',
                'response': 'Hubo un error procesando tu comando.',
                'confidence': 0.0,
                'error': str(e),
                'timestamp': datetime.utcnow()
            }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcular similitud entre dos textos"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    async def speak(self, text: str) -> bool:
        """Sintetizar y reproducir texto"""
        try:
            if not self.tts_engine:
                raise Exception("Motor TTS no inicializado")
            
            logger.info(f"SAMI dice: {text}")
            
            # Reproducir texto
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
            return True
            
        except Exception as e:
            logger.error(f"Error reproduciendo audio: {e}")
            return False
    
    async def voice_interaction_loop(self, duration: float = 5.0) -> Dict:
        """Ciclo completo de interacción por voz"""
        try:
            # Grabar audio
            audio_data = await self.record_audio(duration)
            
            # Transcribir
            transcription = await self.transcribe_audio(audio_data)
            
            if not transcription['text']:
                return {
                    'success': False,
                    'error': 'No se detectó audio',
                    'timestamp': datetime.utcnow()
                }
            
            # Procesar comando
            command = await self.process_voice_command(transcription['text'])
            
            # Responder
            if command['intent'] != 'unknown':
                await self.speak(command['response'])
            
            return {
                'success': True,
                'transcription': transcription,
                'command': command,
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error en interacción de voz: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow()
            }
    
    async def add_voice_command(self, phrase: str, intent: str, response: str, action: str):
        """Agregar nuevo comando de voz"""
        self.voice_commands[phrase.lower()] = {
            'intent': intent,
            'response': response,
            'action': action
        }
        
        logger.info(f"Comando de voz agregado: '{phrase}' -> {intent}")
    
    async def get_available_commands(self) -> List[Dict]:
        """Obtener lista de comandos disponibles"""
        commands = []
        for phrase, config in self.voice_commands.items():
            commands.append({
                'phrase': phrase,
                'intent': config['intent'],
                'response': config['response'],
                'action': config['action']
            })
        
        return commands
    
    async def get_system_status(self) -> Dict:
        """Obtener estado del servicio de voz"""
        return {
            'is_initialized': self.is_initialized,
            'whisper_loaded': self.whisper_model is not None,
            'tts_available': self.tts_engine is not None,
            'commands_count': len(self.voice_commands),
            'last_updated': datetime.utcnow()
        }
