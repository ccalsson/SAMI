#!/bin/bash

# S.A.M.I. - Script de Instalación
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

# Verificar si es root
if [[ $EUID -eq 0 ]]; then
   print_error "Este script no debe ejecutarse como root"
   exit 1
fi

print_message "Iniciando instalación de S.A.M.I."

# Detectar sistema operativo
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        print_error "No se pudo detectar la distribución de Linux"
        exit 1
    fi
else
    print_error "Sistema operativo no soportado: $OSTYPE"
    exit 1
fi

print_message "Sistema detectado: $OS $VER"

# Instalar dependencias del sistema
print_message "Instalando dependencias del sistema..."

if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    sudo apt-get update
    sudo apt-get install -y \
        curl \
        wget \
        git \
        python3 \
        python3-pip \
        python3-venv \
        postgresql \
        postgresql-contrib \
        redis-server \
        nginx \
        docker.io \
        docker-compose \
        build-essential \
        libpq-dev \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgomp1 \
        portaudio19-dev \
        alsa-utils \
        espeak \
        festival \
        nodejs \
        npm
elif [[ "$OS" == *"Raspbian"* ]] || [[ "$OS" == *"Raspberry Pi OS"* ]]; then
    sudo apt-get update
    sudo apt-get install -y \
        curl \
        wget \
        git \
        python3 \
        python3-pip \
        python3-venv \
        postgresql \
        postgresql-contrib \
        redis-server \
        nginx \
        docker.io \
        docker-compose \
        build-essential \
        libpq-dev \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgomp1 \
        portaudio19-dev \
        alsa-utils \
        espeak \
        festival \
        nodejs \
        npm \
        python3-opencv \
        python3-numpy \
        python3-scipy
else
    print_error "Distribución no soportada: $OS"
    exit 1
fi

print_success "Dependencias del sistema instaladas"

# Crear usuario sami si no existe
if ! id "sami" &>/dev/null; then
    print_message "Creando usuario sami..."
    sudo useradd -m -s /bin/bash sami
    sudo usermod -aG docker sami
    print_success "Usuario sami creado"
else
    print_warning "Usuario sami ya existe"
fi

# Crear directorios
print_message "Creando directorios del sistema..."
sudo mkdir -p /opt/sami/{data,logs,models,reports,uploads,ssl}
sudo mkdir -p /opt/sami/data/{events,audio,videos,images}
sudo chown -R sami:sami /opt/sami
print_success "Directorios creados"

# Configurar PostgreSQL
print_message "Configurando PostgreSQL..."
sudo -u postgres psql -c "CREATE USER sami_user WITH PASSWORD 'sami_password';"
sudo -u postgres psql -c "CREATE DATABASE sami_db OWNER sami_user;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE sami_db TO sami_user;"
print_success "PostgreSQL configurado"

# Configurar Redis
print_message "Configurando Redis..."
sudo systemctl enable redis-server
sudo systemctl start redis-server
print_success "Redis configurado"

# Configurar Nginx
print_message "Configurando Nginx..."
sudo cp nginx.conf /etc/nginx/nginx.conf
sudo systemctl enable nginx
sudo systemctl restart nginx
print_success "Nginx configurado"

# Configurar Docker
print_message "Configurando Docker..."
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
print_success "Docker configurado"

# Clonar repositorio si no existe
if [ ! -d "/opt/sami/sami-system" ]; then
    print_message "Clonando repositorio..."
    sudo -u sami git clone https://github.com/tu-usuario/sami-system.git /opt/sami/sami-system
else
    print_warning "Repositorio ya existe, actualizando..."
    sudo -u sami git -C /opt/sami/sami-system pull
fi

# Configurar entorno Python
print_message "Configurando entorno Python..."
sudo -u sami python3 -m venv /opt/sami/venv
sudo -u sami /opt/sami/venv/bin/pip install --upgrade pip
sudo -u sami /opt/sami/venv/bin/pip install -r /opt/sami/sami-system/backend/requirements.txt
print_success "Entorno Python configurado"

# Configurar entorno Node.js
print_message "Configurando entorno Node.js..."
cd /opt/sami/sami-system/frontend
sudo -u sami npm install
sudo -u sami npm run build
print_success "Entorno Node.js configurado"

# Crear archivo de configuración
print_message "Creando archivo de configuración..."
sudo -u sami tee /opt/sami/.env > /dev/null <<EOF
# S.A.M.I. Configuration
APP_NAME=SAMI
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://sami_user:sami_password@localhost:5432/sami_db
REDIS_URL=redis://localhost:6379

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
RASPBERRY_PI_MODE=true
GPIO_ENABLED=true
I2C_ENABLED=true
SPI_ENABLED=true

# AI
AI_MODEL_PATH=/opt/sami/models
VOICE_MODEL_PATH=/opt/sami/models/whisper
TTS_MODEL_PATH=/opt/sami/models/tts

# Directories
UPLOAD_DIR=/opt/sami/uploads
DATA_DIR=/opt/sami/data
MODELS_DIR=/opt/sami/models
REPORTS_DIR=/opt/sami/reports
EOF

print_success "Archivo de configuración creado"

# Crear servicios systemd
print_message "Creando servicios systemd..."

# Servicio backend
sudo tee /etc/systemd/system/sami-backend.service > /dev/null <<EOF
[Unit]
Description=SAMI Backend Service
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=sami
WorkingDirectory=/opt/sami/sami-system/backend
Environment=PATH=/opt/sami/venv/bin
ExecStart=/opt/sami/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Servicio frontend
sudo tee /etc/systemd/system/sami-frontend.service > /dev/null <<EOF
[Unit]
Description=SAMI Frontend Service
After=network.target

[Service]
Type=simple
User=sami
WorkingDirectory=/opt/sami/sami-system/frontend
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Habilitar servicios
sudo systemctl daemon-reload
sudo systemctl enable sami-backend
sudo systemctl enable sami-frontend

print_success "Servicios systemd creados"

# Crear script de inicio
print_message "Creando script de inicio..."
sudo tee /opt/sami/start.sh > /dev/null <<EOF
#!/bin/bash
# S.A.M.I. Start Script

echo "Iniciando S.A.M.I. - Sistema Automático de Monitoreo Inteligente"

# Iniciar servicios
sudo systemctl start sami-backend
sudo systemctl start sami-frontend

echo "SAMI iniciado correctamente"
echo "Frontend: http://localhost"
echo "API: http://localhost/api"
echo "Documentación: http://localhost/api/docs"
EOF

sudo chmod +x /opt/sami/start.sh
print_success "Script de inicio creado"

# Crear script de parada
print_message "Creando script de parada..."
sudo tee /opt/sami/stop.sh > /dev/null <<EOF
#!/bin/bash
# S.A.M.I. Stop Script

echo "Deteniendo S.A.M.I. - Sistema Automático de Monitoreo Inteligente"

# Detener servicios
sudo systemctl stop sami-frontend
sudo systemctl stop sami-backend

echo "SAMI detenido correctamente"
EOF

sudo chmod +x /opt/sami/stop.sh
print_success "Script de parada creado"

# Crear script de actualización
print_message "Creando script de actualización..."
sudo tee /opt/sami/update.sh > /dev/null <<EOF
#!/bin/bash
# S.A.M.I. Update Script

echo "Actualizando S.A.M.I. - Sistema Automático de Monitoreo Inteligente"

# Detener servicios
sudo systemctl stop sami-frontend
sudo systemctl stop sami-backend

# Actualizar código
cd /opt/sami/sami-system
sudo -u sami git pull

# Actualizar dependencias
sudo -u sami /opt/sami/venv/bin/pip install -r backend/requirements.txt
cd frontend
sudo -u sami npm install
sudo -u sami npm run build

# Iniciar servicios
sudo systemctl start sami-backend
sudo systemctl start sami-frontend

echo "SAMI actualizado correctamente"
EOF

sudo chmod +x /opt/sami/update.sh
print_success "Script de actualización creado"

# Configurar firewall (si está disponible)
if command -v ufw &> /dev/null; then
    print_message "Configurando firewall..."
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw allow 8000/tcp
    print_success "Firewall configurado"
fi

# Crear backup inicial
print_message "Creando backup inicial..."
sudo -u postgres pg_dump sami_db > /opt/sami/backup_initial.sql
print_success "Backup inicial creado"

print_success "Instalación completada exitosamente!"
print_message "Para iniciar SAMI, ejecuta: /opt/sami/start.sh"
print_message "Para detener SAMI, ejecuta: /opt/sami/stop.sh"
print_message "Para actualizar SAMI, ejecuta: /opt/sami/update.sh"
print_message "Accede a la aplicación en: http://localhost"
print_warning "Recuerda configurar las variables de entorno en /opt/sami/.env"
