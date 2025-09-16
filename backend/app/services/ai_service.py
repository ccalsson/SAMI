# S.A.M.I. - Servicio de Inteligencia Artificial
import cv2
import numpy as np
import face_recognition
import pickle
import os
from typing import List, Dict, Optional, Tuple
import asyncio
import logging
from datetime import datetime

from ..core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    """Servicio principal de IA para reconocimiento facial y detección de eventos"""
    
    def __init__(self):
        self.face_encodings = {}
        self.face_names = {}
        self.model_loaded = False
        self.face_cascade = None
        self.known_faces = []
        self.known_names = []
        
    async def initialize(self):
        """Inicializar el servicio de IA"""
        try:
            # Cargar modelo de detección facial
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # Cargar encodings faciales existentes
            await self.load_face_encodings()
            
            self.model_loaded = True
            logger.info("Servicio de IA inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando servicio de IA: {e}")
            raise
    
    async def load_face_encodings(self):
        """Cargar encodings faciales de empleados"""
        try:
            encodings_file = os.path.join(settings.models_dir, "face_encodings.pkl")
            
            if os.path.exists(encodings_file):
                with open(encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.face_encodings = data.get('encodings', {})
                    self.face_names = data.get('names', {})
                    
                # Convertir a listas para face_recognition
                self.known_faces = list(self.face_encodings.values())
                self.known_names = list(self.face_names.values())
                
                logger.info(f"Cargados {len(self.known_faces)} encodings faciales")
            else:
                logger.info("No se encontraron encodings faciales existentes")
                
        except Exception as e:
            logger.error(f"Error cargando encodings faciales: {e}")
    
    async def save_face_encodings(self):
        """Guardar encodings faciales"""
        try:
            os.makedirs(settings.models_dir, exist_ok=True)
            encodings_file = os.path.join(settings.models_dir, "face_encodings.pkl")
            
            data = {
                'encodings': self.face_encodings,
                'names': self.face_names
            }
            
            with open(encodings_file, 'wb') as f:
                pickle.dump(data, f)
                
            logger.info("Encodings faciales guardados correctamente")
            
        except Exception as e:
            logger.error(f"Error guardando encodings faciales: {e}")
    
    async def add_employee_face(self, employee_id: int, employee_name: str, image_path: str) -> bool:
        """Agregar cara de empleado al sistema"""
        try:
            # Cargar imagen
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if not face_encodings:
                logger.warning(f"No se detectaron caras en la imagen: {image_path}")
                return False
            
            # Usar la primera cara detectada
            face_encoding = face_encodings[0]
            
            # Agregar al diccionario
            self.face_encodings[employee_id] = face_encoding
            self.face_names[employee_id] = employee_name
            
            # Actualizar listas
            self.known_faces = list(self.face_encodings.values())
            self.known_names = list(self.face_names.values())
            
            # Guardar
            await self.save_face_encodings()
            
            logger.info(f"Cara agregada para empleado {employee_name} (ID: {employee_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error agregando cara de empleado: {e}")
            return False
    
    async def recognize_faces_in_image(self, image_path: str) -> List[Dict]:
        """Reconocer caras en una imagen"""
        try:
            if not self.model_loaded:
                raise Exception("Modelo de IA no inicializado")
            
            # Cargar imagen
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            results = []
            
            for i, face_encoding in enumerate(face_encodings):
                # Comparar con caras conocidas
                matches = face_recognition.compare_faces(
                    self.known_faces, face_encoding, tolerance=0.6
                )
                
                face_distances = face_recognition.face_distance(
                    self.known_faces, face_encoding
                )
                
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index]:
                    confidence = 1 - face_distances[best_match_index]
                    employee_id = list(self.face_encodings.keys())[best_match_index]
                    employee_name = self.face_names[employee_id]
                    
                    results.append({
                        'employee_id': employee_id,
                        'employee_name': employee_name,
                        'confidence': float(confidence),
                        'face_location': face_locations[i],
                        'timestamp': datetime.utcnow()
                    })
                else:
                    results.append({
                        'employee_id': None,
                        'employee_name': 'Unknown',
                        'confidence': 0.0,
                        'face_location': face_locations[i],
                        'timestamp': datetime.utcnow()
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error reconociendo caras: {e}")
            return []
    
    async def detect_objects_in_image(self, image_path: str) -> List[Dict]:
        """Detectar objetos en una imagen (herramientas, vehículos, etc.)"""
        try:
            # Cargar imagen
            image = cv2.imread(image_path)
            if image is None:
                raise Exception("No se pudo cargar la imagen")
            
            # Convertir a RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detectar caras
            face_locations = face_recognition.face_locations(rgb_image)
            
            # Detectar objetos usando OpenCV (implementación básica)
            objects = []
            
            # Detectar contornos
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # Filtrar contornos pequeños
                    x, y, w, h = cv2.boundingRect(contour)
                    objects.append({
                        'type': 'object',
                        'confidence': 0.7,  # Valor fijo por ahora
                        'bbox': [x, y, w, h],
                        'area': float(area)
                    })
            
            return objects
            
        except Exception as e:
            logger.error(f"Error detectando objetos: {e}")
            return []
    
    async def detect_event(self, image_path: str, event_type: str) -> Dict:
        """Detectar eventos específicos en una imagen"""
        try:
            results = {
                'event_detected': False,
                'event_type': event_type,
                'confidence': 0.0,
                'details': {},
                'timestamp': datetime.utcnow()
            }
            
            if event_type == "tool_taken":
                # Detectar si alguien tomó una herramienta
                faces = await self.recognize_faces_in_image(image_path)
                objects = await self.detect_objects_in_image(image_path)
                
                if faces and objects:
                    results['event_detected'] = True
                    results['confidence'] = 0.8
                    results['details'] = {
                        'faces_detected': len(faces),
                        'objects_detected': len(objects),
                        'people': [f['employee_name'] for f in faces]
                    }
            
            elif event_type == "unauthorized_access":
                # Detectar acceso no autorizado
                faces = await self.recognize_faces_in_image(image_path)
                
                for face in faces:
                    if face['employee_id'] is None:
                        results['event_detected'] = True
                        results['confidence'] = 0.9
                        results['details'] = {
                            'unauthorized_person_detected': True,
                            'face_location': face['face_location']
                        }
                        break
            
            elif event_type == "fuel_theft":
                # Detectar posible robo de combustible
                objects = await self.detect_objects_in_image(image_path)
                
                # Lógica simple para detectar actividad sospechosa
                if len(objects) > 3:  # Muchos objetos detectados
                    results['event_detected'] = True
                    results['confidence'] = 0.7
                    results['details'] = {
                        'suspicious_activity': True,
                        'objects_count': len(objects)
                    }
            
            return results
            
        except Exception as e:
            logger.error(f"Error detectando evento: {e}")
            return {
                'event_detected': False,
                'event_type': event_type,
                'confidence': 0.0,
                'error': str(e),
                'timestamp': datetime.utcnow()
            }
    
    async def process_camera_frame(self, frame: np.ndarray, camera_id: str) -> Dict:
        """Procesar frame de cámara en tiempo real"""
        try:
            # Convertir frame a RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detectar caras
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            results = {
                'camera_id': camera_id,
                'timestamp': datetime.utcnow(),
                'faces_detected': len(face_locations),
                'recognitions': []
            }
            
            for i, face_encoding in enumerate(face_encodings):
                matches = face_recognition.compare_faces(
                    self.known_faces, face_encoding, tolerance=0.6
                )
                
                if True in matches:
                    best_match_index = matches.index(True)
                    employee_id = list(self.face_encodings.keys())[best_match_index]
                    employee_name = self.face_names[employee_id]
                    
                    results['recognitions'].append({
                        'employee_id': employee_id,
                        'employee_name': employee_name,
                        'confidence': 0.8,  # Valor fijo por simplicidad
                        'face_location': face_locations[i]
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error procesando frame de cámara: {e}")
            return {
                'camera_id': camera_id,
                'timestamp': datetime.utcnow(),
                'error': str(e)
            }
    
    async def get_system_status(self) -> Dict:
        """Obtener estado del servicio de IA"""
        return {
            'model_loaded': self.model_loaded,
            'known_faces_count': len(self.known_faces),
            'face_encodings_count': len(self.face_encodings),
            'last_updated': datetime.utcnow()
        }
