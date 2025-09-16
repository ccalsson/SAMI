# S.A.M.I. - Sistema Automático de Monitoreo Inteligente

## Arquitectura del Sistema

### Visión General
SAMI es un sistema integral de monitoreo e interacción en tiempo real para empresas de movimiento de suelos y logística, que integra múltiples tecnologías para automatizar el control de activos, personal y operaciones.

### Componentes Principales

#### 1. Capa de Hardware
- **Cámaras IP**: Detección visual con IA
- **Sensores RFID**: Control de activos y personal
- **Micrófonos/Altavoces**: Interacción por voz
- **Sensores IoT**: Caudalímetros, proximidad, GPS
- **Dispositivos ESP32**: Nodos de sensores distribuidos

#### 2. Capa de Procesamiento
- **Servidor Principal**: Raspberry Pi 5 o mini PC
- **IA Local**: TensorFlow/PyTorch optimizado
- **Procesamiento de Voz**: Whisper + TTS local
- **Motor de Reglas**: Lógica de negocio y alertas

#### 3. Capa de Datos
- **Base de Datos Local**: PostgreSQL
- **Sincronización Cloud**: Firebase/Drive backups
- **Cache Redis**: Datos en tiempo real
- **Almacenamiento**: Videos, audios, logs

#### 4. Capa de Aplicación
- **API REST**: FastAPI backend
- **Web Dashboard**: React/Next.js
- **Servicios de Comunicación**: WhatsApp, Email
- **Sistema de Reportes**: PDF/Excel automático

### Flujo de Datos

```
Hardware Sensors → ESP32 Nodes → Local Network → Raspberry Pi → AI Processing → Database → API → Web Dashboard
                                                                                ↓
                                                                        WhatsApp/Email Alerts
```

### Módulos del Sistema

1. **Control de Activos y Personal**
   - Identificación RFID y facial
   - Registro entrada/salida
   - Gestión de herramientas

2. **Monitoreo con IA**
   - Detección de eventos
   - Reconocimiento facial
   - Análisis de comportamiento

3. **Interacción por Voz**
   - Reconocimiento de voz (Whisper)
   - Síntesis de voz (TTS)
   - IA conversacional local

4. **Gestión de Proyectos**
   - Control de obras
   - Registro de horas
   - Gestión de presupuestos

5. **GPS y Comunicación**
   - Tracking satelital
   - Comunicación bidireccional
   - Integración con mapas

6. **Sistema de Reportes**
   - Generación automática
   - Múltiples formatos
   - Distribución automática

### Tecnologías Utilizadas

- **Backend**: Python 3.11 + FastAPI
- **Base de Datos**: PostgreSQL + Redis
- **IA/ML**: TensorFlow Lite, OpenCV, Whisper
- **Frontend**: React 18 + Next.js 14
- **Hardware**: Raspberry Pi 5, ESP32, cámaras IP
- **Comunicación**: Twilio WhatsApp API, SMTP
- **Deployment**: Docker, Docker Compose
