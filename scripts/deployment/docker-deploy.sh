#!/bin/bash

# S.A.M.I. - Docker Deployment Script
# Sistema Automático de Monitoreo Inteligente

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_message() {
    echo -e "${BLUE}[SAMI]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose no está instalado"
    exit 1
fi

print_message "Iniciando deployment de S.A.M.I. con Docker"

# Crear directorios necesarios
print_message "Creando directorios necesarios..."
mkdir -p data/{events,audio,videos,images}
mkdir -p logs
mkdir -p models
mkdir -p reports
mkdir -p ssl
print_success "Directorios creados"

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    print_message "Creando archivo .env..."
    cat > .env <<EOF
# S.A.M.I. Docker Configuration
APP_NAME=SAMI
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://sami_user:sami_password@postgres:5432/sami_db
REDIS_URL=redis://redis:6379

# API
SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# WhatsApp
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-number

# Hardware
RASPBERRY_PI_MODE=false
GPIO_ENABLED=false
I2C_ENABLED=false
SPI_ENABLED=false

# AI
AI_MODEL_PATH=/app/models
VOICE_MODEL_PATH=/app/models/whisper
TTS_MODEL_PATH=/app/models/tts

# Directories
UPLOAD_DIR=/app/uploads
DATA_DIR=/app/data
MODELS_DIR=/app/models
REPORTS_DIR=/app/reports
EOF
    print_success "Archivo .env creado"
else
    print_warning "Archivo .env ya existe"
fi

# Crear archivo de configuración de Nginx
print_message "Configurando Nginx..."
if [ ! -f "nginx.conf" ]; then
    print_error "Archivo nginx.conf no encontrado"
    exit 1
fi

# Crear certificados SSL autofirmados para desarrollo
print_message "Creando certificados SSL..."
if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
    mkdir -p ssl
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/key.pem \
        -out ssl/cert.pem \
        -subj "/C=AR/ST=BA/L=BA/CN=localhost"
    print_success "Certificados SSL creados"
else
    print_warning "Certificados SSL ya existen"
fi

# Construir imágenes Docker
print_message "Construyendo imágenes Docker..."
docker-compose build --no-cache
print_success "Imágenes construidas"

# Iniciar servicios
print_message "Iniciando servicios..."
docker-compose up -d postgres redis
print_message "Esperando a que la base de datos esté lista..."
sleep 30

# Ejecutar migraciones
print_message "Ejecutando migraciones de base de datos..."
docker-compose run --rm backend alembic upgrade head
print_success "Migraciones ejecutadas"

# Iniciar todos los servicios
print_message "Iniciando todos los servicios..."
docker-compose up -d
print_success "Servicios iniciados"

# Verificar estado de los servicios
print_message "Verificando estado de los servicios..."
sleep 10

# Verificar backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend está funcionando"
else
    print_error "Backend no está respondiendo"
fi

# Verificar frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_success "Frontend está funcionando"
else
    print_error "Frontend no está respondiendo"
fi

# Verificar base de datos
if docker-compose exec postgres pg_isready -U sami_user -d sami_db > /dev/null 2>&1; then
    print_success "Base de datos está funcionando"
else
    print_error "Base de datos no está respondiendo"
fi

# Verificar Redis
if docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
    print_success "Redis está funcionando"
else
    print_error "Redis no está respondiendo"
fi

# Mostrar información de acceso
print_success "Deployment completado exitosamente!"
echo ""
print_message "Información de acceso:"
echo "  Frontend: http://localhost"
echo "  API: http://localhost/api"
echo "  Documentación API: http://localhost/api/docs"
echo "  Adminer (DB): http://localhost:8080"
echo ""
print_message "Comandos útiles:"
echo "  Ver logs: docker-compose logs -f"
echo "  Detener: docker-compose down"
echo "  Reiniciar: docker-compose restart"
echo "  Actualizar: ./scripts/deployment/docker-deploy.sh"
echo ""
print_warning "Recuerda configurar las variables de entorno en .env para producción"
