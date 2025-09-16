# S.A.M.I. - Sistema Automático de Monitoreo Inteligente

## Descripción del Proyecto

SAMI es un sistema integral de monitoreo e interacción en tiempo real para empresas de movimiento de suelos y logística. Integra cámaras con IA, micrófonos, altavoces, sensores RFID y GPS satelital, todo gestionado desde un servidor local con comunicación hacia responsables vía WhatsApp.

## Estructura del Proyecto

```
sami-system/
├── backend/                 # API Backend (FastAPI)
│   ├── app/
│   │   ├── api/            # Endpoints de la API
│   │   ├── core/           # Configuración y utilidades core
│   │   ├── models/         # Modelos de base de datos
│   │   ├── services/       # Lógica de negocio
│   │   └── utils/          # Utilidades
│   └── tests/              # Tests unitarios
├── frontend/               # Dashboard Web (React/Next.js)
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   ├── pages/          # Páginas de la aplicación
│   │   ├── services/       # Servicios de API
│   │   └── utils/          # Utilidades frontend
│   └── public/             # Archivos estáticos
├── hardware/               # Código para hardware
│   ├── esp32/              # Firmware para nodos ESP32
│   └── raspberry_pi/       # Scripts para Raspberry Pi
├── docs/                   # Documentación
│   ├── api/                # Documentación de API
│   ├── deployment/         # Guías de despliegue
│   └── user_guide/         # Manual de usuario
├── scripts/                # Scripts de utilidad
│   ├── setup/              # Scripts de configuración
│   ├── deployment/         # Scripts de despliegue
│   └── maintenance/        # Scripts de mantenimiento
├── docker-compose.yml      # Configuración Docker
├── requirements.txt        # Dependencias Python
└── package.json           # Dependencias Node.js
```

## Módulos Principales

### 1. Control de Activos y Personal
- Identificación RFID y reconocimiento facial
- Registro de entrada/salida de herramientas y vehículos
- Control de combustible y activos

### 2. Monitoreo con IA
- Detección de eventos en tiempo real
- Reconocimiento facial de operarios
- Análisis de comportamiento y alertas

### 3. Interacción por Voz
- Reconocimiento de voz con Whisper
- Síntesis de voz (TTS) para respuestas
- IA conversacional local (SAMI)

### 4. Gestión de Proyectos
- Control de obras activas
- Registro de horas máquina y hombre
- Gestión de presupuestos y gastos

### 5. GPS y Comunicación
- Tracking satelital en tiempo real
- Comunicación bidireccional
- Integración con mapas

### 6. Sistema de Reportes
- Generación automática de reportes
- Múltiples formatos (PDF, Excel)
- Distribución automática vía WhatsApp/Email

## Tecnologías

- **Backend**: Python 3.11 + FastAPI
- **Base de Datos**: PostgreSQL + Redis
- **IA/ML**: TensorFlow Lite, OpenCV, Whisper
- **Frontend**: React 18 + Next.js 14
- **Hardware**: Raspberry Pi 5, ESP32, cámaras IP
- **Comunicación**: Twilio WhatsApp API, SMTP
- **Deployment**: Docker, Docker Compose

## Instalación y Configuración

### Requisitos Previos
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Docker y Docker Compose

### Instalación Rápida
```bash
# Clonar el repositorio
git clone <repository-url>
cd sami-system

# Configurar backend
cd backend
pip install -r requirements.txt

# Configurar frontend
cd ../frontend
npm install

# Configurar base de datos
docker-compose up -d postgres redis

# Ejecutar migraciones
cd ../backend
alembic upgrade head

# Iniciar servicios
docker-compose up -d
```

## Roadmap de Implementación

### Fase 1: Prototipo Base (4-6 semanas)
- [x] Arquitectura del sistema
- [ ] Estructura del proyecto
- [ ] Modelos de base de datos
- [ ] API básica con FastAPI
- [ ] Módulo de cámaras con IA básica
- [ ] Sistema de interacción por voz
- [ ] Dashboard web básico

### Fase 2: Módulos Core (6-8 semanas)
- [ ] Control RFID completo
- [ ] Sistema de reportes automáticos
- [ ] Integración GPS y comunicación
- [ ] Optimización para Raspberry Pi
- [ ] Tests y documentación

### Fase 3: Producción (4-6 semanas)
- [ ] Deployment en producción
- [ ] Monitoreo y alertas
- [ ] Optimizaciones de rendimiento
- [ ] Capacitación y soporte

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.
