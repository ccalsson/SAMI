# S.A.M.I. - Servicio RFID
import asyncio
import logging
import serial
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime
import threading
import queue
import json

from ..core.config import settings

logger = logging.getLogger(__name__)

class RFIDService:
    """Servicio para manejo de lectores RFID"""
    
    def __init__(self):
        self.readers = {}
        self.reader_threads = {}
        self.running = False
        self.transaction_callbacks = []
        self.alert_callbacks = []
        
    async def initialize(self):
        """Inicializar el servicio RFID"""
        try:
            # Cargar configuración de lectores
            await self.load_reader_configs()
            
            logger.info("Servicio RFID inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando servicio RFID: {e}")
            raise
    
    async def load_reader_configs(self):
        """Cargar configuraciones de lectores RFID"""
        # Configuración por defecto para desarrollo
        default_readers = [
            {
                "reader_id": "reader_1",
                "name": "Lector Principal",
                "port": "/dev/ttyUSB0",
                "baudrate": 9600,
                "location": "Entrada Principal",
                "enabled": True
            },
            {
                "reader_id": "reader_2", 
                "name": "Lector Surtidor",
                "port": "/dev/ttyUSB1",
                "baudrate": 9600,
                "location": "Surtidor de Combustible",
                "enabled": True
            },
            {
                "reader_id": "reader_3",
                "name": "Lector Taller",
                "port": "/dev/ttyUSB2", 
                "baudrate": 9600,
                "location": "Taller",
                "enabled": True
            }
        ]
        
        for config in default_readers:
            self.readers[config["reader_id"]] = config
    
    async def start_reader(self, reader_id: str) -> bool:
        """Iniciar lector RFID específico"""
        try:
            if reader_id not in self.readers:
                logger.error(f"Lector {reader_id} no encontrado")
                return False
            
            config = self.readers[reader_id]
            
            if reader_id in self.reader_threads:
                logger.warning(f"Lector {reader_id} ya está ejecutándose")
                return True
            
            # Crear thread para el lector
            thread = threading.Thread(
                target=self._reader_worker,
                args=(reader_id, config),
                daemon=True
            )
            
            self.reader_threads[reader_id] = thread
            thread.start()
            
            logger.info(f"Lector RFID {reader_id} iniciado")
            return True
            
        except Exception as e:
            logger.error(f"Error iniciando lector {reader_id}: {e}")
            return False
    
    async def stop_reader(self, reader_id: str) -> bool:
        """Detener lector RFID específico"""
        try:
            if reader_id in self.reader_threads:
                # Marcar para detener
                self.readers[reader_id]["enabled"] = False
                
                # Esperar a que termine el thread
                thread = self.reader_threads[reader_id]
                thread.join(timeout=5)
                
                del self.reader_threads[reader_id]
                logger.info(f"Lector RFID {reader_id} detenido")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deteniendo lector {reader_id}: {e}")
            return False
    
    async def start_all_readers(self) -> bool:
        """Iniciar todos los lectores RFID"""
        try:
            self.running = True
            success_count = 0
            
            for reader_id in self.readers:
                if await self.start_reader(reader_id):
                    success_count += 1
            
            logger.info(f"Iniciados {success_count}/{len(self.readers)} lectores RFID")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error iniciando lectores RFID: {e}")
            return False
    
    async def stop_all_readers(self) -> bool:
        """Detener todos los lectores RFID"""
        try:
            self.running = False
            success_count = 0
            
            for reader_id in list(self.reader_threads.keys()):
                if await self.stop_reader(reader_id):
                    success_count += 1
            
            logger.info(f"Detenidos {success_count} lectores RFID")
            return True
            
        except Exception as e:
            logger.error(f"Error deteniendo lectores RFID: {e}")
            return False
    
    def _reader_worker(self, reader_id: str, config: Dict):
        """Worker thread para procesar lector RFID"""
        ser = None
        
        try:
            # Abrir puerto serie
            ser = serial.Serial(
                port=config["port"],
                baudrate=config["baudrate"],
                timeout=1
            )
            
            logger.info(f"Procesando lector RFID {reader_id} - {config['name']}")
            
            while config["enabled"] and self.running:
                try:
                    # Leer datos del lector
                    if ser.in_waiting > 0:
                        data = ser.readline().decode('utf-8').strip()
                        
                        if data:
                            # Procesar tag RFID
                            await self._process_rfid_tag(reader_id, data, config)
                    
                    time.sleep(0.1)  # Pequeña pausa para no sobrecargar
                    
                except Exception as e:
                    logger.error(f"Error leyendo del lector {reader_id}: {e}")
                    time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error en worker de lector {reader_id}: {e}")
        finally:
            if ser:
                ser.close()
            logger.info(f"Worker de lector RFID {reader_id} terminado")
    
    async def _process_rfid_tag(self, reader_id: str, tag_data: str, config: Dict):
        """Procesar tag RFID leído"""
        try:
            # Parsear datos del tag
            tag_id = tag_data.strip()
            
            if not tag_id:
                return
            
            # Crear transacción
            transaction = {
                "reader_id": reader_id,
                "tag_id": tag_id,
                "timestamp": datetime.utcnow(),
                "location": config["location"],
                "raw_data": tag_data
            }
            
            # Buscar empleado o activo asociado
            employee_id, asset_id = await self._find_associated_entities(tag_id)
            
            transaction["employee_id"] = employee_id
            transaction["asset_id"] = asset_id
            
            # Determinar tipo de transacción
            transaction_type = await self._determine_transaction_type(
                reader_id, tag_id, employee_id, asset_id
            )
            
            transaction["transaction_type"] = transaction_type
            
            # Procesar transacción
            await self._process_transaction(transaction)
            
            logger.info(f"Tag RFID procesado: {tag_id} en lector {reader_id}")
            
        except Exception as e:
            logger.error(f"Error procesando tag RFID: {e}")
    
    async def _find_associated_entities(self, tag_id: str) -> tuple:
        """Buscar empleado o activo asociado al tag"""
        # Esta función debería consultar la base de datos
        # Por ahora retornamos valores de ejemplo
        employee_id = None
        asset_id = None
        
        # Simular búsqueda en base de datos
        # En implementación real, consultarías las tablas Employee y Asset
        
        return employee_id, asset_id
    
    async def _determine_transaction_type(self, reader_id: str, tag_id: str, 
                                        employee_id: Optional[int], 
                                        asset_id: Optional[int]) -> str:
        """Determinar tipo de transacción basado en contexto"""
        # Lógica para determinar el tipo de transacción
        # Por ejemplo, basado en la ubicación del lector y el tipo de entidad
        
        if employee_id:
            return "employee_check_in"
        elif asset_id:
            return "asset_checkout"
        else:
            return "unknown"
    
    async def _process_transaction(self, transaction: Dict):
        """Procesar transacción RFID"""
        try:
            # Guardar en base de datos
            await self._save_transaction(transaction)
            
            # Notificar callbacks
            for callback in self.transaction_callbacks:
                try:
                    await callback(transaction)
                except Exception as e:
                    logger.error(f"Error en callback de transacción: {e}")
            
            # Verificar alertas
            await self._check_alerts(transaction)
            
        except Exception as e:
            logger.error(f"Error procesando transacción: {e}")
    
    async def _save_transaction(self, transaction: Dict):
        """Guardar transacción en base de datos"""
        # Esta función debería guardar en la base de datos
        # Por ahora solo logueamos
        logger.info(f"Transacción guardada: {transaction}")
    
    async def _check_alerts(self, transaction: Dict):
        """Verificar alertas basadas en la transacción"""
        try:
            alerts = []
            
            # Verificar acceso no autorizado
            if transaction["employee_id"] is None and transaction["asset_id"] is None:
                alerts.append({
                    "type": "unauthorized_access",
                    "severity": "high",
                    "message": f"Acceso no autorizado con tag {transaction['tag_id']}",
                    "transaction": transaction
                })
            
            # Verificar duplicados recientes
            # (implementar lógica de detección de duplicados)
            
            # Procesar alertas
            for alert in alerts:
                for callback in self.alert_callbacks:
                    try:
                        await callback(alert)
                    except Exception as e:
                        logger.error(f"Error en callback de alerta: {e}")
            
        except Exception as e:
            logger.error(f"Error verificando alertas: {e}")
    
    def add_transaction_callback(self, callback: Callable):
        """Agregar callback para transacciones RFID"""
        self.transaction_callbacks.append(callback)
    
    def add_alert_callback(self, callback: Callable):
        """Agregar callback para alertas RFID"""
        self.alert_callbacks.append(callback)
    
    async def get_reader_status(self, reader_id: str) -> Dict:
        """Obtener estado de un lector RFID"""
        if reader_id not in self.readers:
            return {"error": "Lector no encontrado"}
        
        config = self.readers[reader_id]
        is_running = reader_id in self.reader_threads
        
        return {
            "reader_id": reader_id,
            "name": config["name"],
            "location": config["location"],
            "port": config["port"],
            "baudrate": config["baudrate"],
            "enabled": config["enabled"],
            "is_running": is_running
        }
    
    async def get_all_readers_status(self) -> Dict:
        """Obtener estado de todos los lectores RFID"""
        status = {}
        for reader_id in self.readers:
            status[reader_id] = await self.get_reader_status(reader_id)
        
        return {
            "total_readers": len(self.readers),
            "running_readers": len(self.reader_threads),
            "readers": status
        }
    
    async def update_reader_config(self, reader_id: str, config_updates: Dict) -> bool:
        """Actualizar configuración de lector RFID"""
        try:
            if reader_id not in self.readers:
                return False
            
            config = self.readers[reader_id]
            
            # Actualizar campos permitidos
            for key, value in config_updates.items():
                if key in config:
                    config[key] = value
            
            logger.info(f"Configuración de lector {reader_id} actualizada")
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando configuración de lector: {e}")
            return False
    
    async def test_reader(self, reader_id: str) -> Dict:
        """Probar lector RFID"""
        try:
            if reader_id not in self.readers:
                return {"error": "Lector no encontrado"}
            
            config = self.readers[reader_id]
            
            # Intentar conectar al lector
            try:
                ser = serial.Serial(
                    port=config["port"],
                    baudrate=config["baudrate"],
                    timeout=1
                )
                ser.close()
                
                return {
                    "success": True,
                    "message": f"Lector {reader_id} responde correctamente",
                    "config": config
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error conectando al lector: {e}",
                    "config": config
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_system_status(self) -> Dict:
        """Obtener estado del servicio RFID"""
        return {
            "running": self.running,
            "total_readers": len(self.readers),
            "active_readers": len(self.reader_threads),
            "transaction_callbacks": len(self.transaction_callbacks),
            "alert_callbacks": len(self.alert_callbacks),
            "last_updated": datetime.utcnow()
        }
