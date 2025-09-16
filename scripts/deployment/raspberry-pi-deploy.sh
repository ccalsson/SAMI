#!/bin/bash

# S.A.M.I. - Raspberry Pi Deployment Script
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

# Verificar si estamos en Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    print_warning "Este script está optimizado para Raspberry Pi"
fi

print_message "Iniciando deployment de S.A.M.I. en Raspberry Pi"

# Actualizar sistema
print_message "Actualizando sistema..."
sudo apt-get update
sudo apt-get upgrade -y
print_success "Sistema actualizado"

# Instalar dependencias específicas para Raspberry Pi
print_message "Instalando dependencias específicas para Raspberry Pi..."
sudo apt-get install -y \
    python3-opencv \
    python3-numpy \
    python3-scipy \
    python3-picamera \
    python3-rpi.gpio \
    i2c-tools \
    python3-smbus \
    python3-dev \
    libatlas-base-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libqtgui4 \
    libqtwebkit4 \
    libqt4-test \
    python3-pyqt5 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libatlas-base-dev \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libhdf5-103 \
    libqtgui4 \
    libqtwebkit4 \
    libqt4-test \
    python3-pyqt5 \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libatlas-base-dev \
    gfortran \
    wget \
    curl \
    git

print_success "Dependencias instaladas"

# Habilitar interfaces necesarias
print_message "Habilitando interfaces necesarias..."
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_serial 0
sudo raspi-config nonint do_camera 0
print_success "Interfaces habilitadas"

# Configurar memoria GPU
print_message "Configurando memoria GPU..."
if ! grep -q "gpu_mem=128" /boot/config.txt; then
    echo "gpu_mem=128" | sudo tee -a /boot/config.txt
fi
print_success "Memoria GPU configurada"

# Instalar Docker para Raspberry Pi
print_message "Instalando Docker para Raspberry Pi..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker pi
sudo systemctl enable docker
sudo systemctl start docker
rm get-docker.sh
print_success "Docker instalado"

# Instalar Docker Compose
print_message "Instalando Docker Compose..."
sudo pip3 install docker-compose
print_success "Docker Compose instalado"

# Crear directorios
print_message "Creando directorios..."
sudo mkdir -p /opt/sami/{data,logs,models,reports,uploads,ssl}
sudo mkdir -p /opt/sami/data/{events,audio,videos,images}
sudo chown -R pi:pi /opt/sami
print_success "Directorios creados"

# Clonar repositorio
print_message "Clonando repositorio..."
if [ ! -d "/opt/sami/sami-system" ]; then
    git clone https://github.com/tu-usuario/sami-system.git /opt/sami/sami-system
else
    cd /opt/sami/sami-system
    git pull
fi
print_success "Repositorio clonado"

# Crear archivo de configuración para Raspberry Pi
print_message "Creando configuración para Raspberry Pi..."
cat > /opt/sami/.env <<EOF
# S.A.M.I. Raspberry Pi Configuration
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

# Hardware - Raspberry Pi específico
RASPBERRY_PI_MODE=true
GPIO_ENABLED=true
I2C_ENABLED=true
SPI_ENABLED=true

# Cámaras
CAMERA_RTSP_URLS=rtsp://192.168.1.100:554/stream,rtsp://192.168.1.101:554/stream
CAMERA_TIMEOUT=60
SENSOR_POLLING_INTERVAL=10

# AI optimizado para Raspberry Pi
AI_MODEL_PATH=/opt/sami/models
VOICE_MODEL_PATH=/opt/sami/models/whisper
TTS_MODEL_PATH=/opt/sami/models/tts

# Directories
UPLOAD_DIR=/opt/sami/uploads
DATA_DIR=/opt/sami/data
MODELS_DIR=/opt/sami/models
REPORTS_DIR=/opt/sami/reports

# Optimizaciones para Raspberry Pi
TENSORFLOW_OPTIMIZATION=true
OPENCV_OPTIMIZATION=true
WHISPER_OPTIMIZATION=true
EOF

print_success "Configuración creada"

# Crear script de optimización para Raspberry Pi
print_message "Creando script de optimización..."
cat > /opt/sami/optimize-raspberry-pi.sh <<'EOF'
#!/bin/bash

# S.A.M.I. - Optimización para Raspberry Pi

echo "Optimizando S.A.M.I. para Raspberry Pi..."

# Aumentar memoria compartida
echo "Configurando memoria compartida..."
echo "vm.swappiness=1" | sudo tee -a /etc/sysctl.conf
echo "vm.vfs_cache_pressure=50" | sudo tee -a /etc/sysctl.conf

# Optimizar SD card
echo "Optimizando SD card..."
echo "noatime" | sudo tee -a /etc/fstab

# Configurar CPU governor
echo "Configurando CPU governor..."
echo "performance" | sudo tee /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

# Configurar GPU memory split
echo "Configurando GPU memory split..."
if ! grep -q "gpu_mem=128" /boot/config.txt; then
    echo "gpu_mem=128" | sudo tee -a /boot/config.txt
fi

# Configurar overclocking (opcional)
echo "Configurando overclocking..."
if ! grep -q "arm_freq=1500" /boot/config.txt; then
    echo "arm_freq=1500" | sudo tee -a /boot/config.txt
    echo "over_voltage=2" | sudo tee -a /boot/config.txt
fi

# Configurar temperatura
echo "Configurando monitoreo de temperatura..."
if ! grep -q "temp_limit=80" /boot/config.txt; then
    echo "temp_limit=80" | sudo tee -a /boot/config.txt
fi

echo "Optimización completada. Reinicia el sistema para aplicar cambios."
EOF

chmod +x /opt/sami/optimize-raspberry-pi.sh
print_success "Script de optimización creado"

# Crear script de monitoreo de temperatura
print_message "Creando script de monitoreo de temperatura..."
cat > /opt/sami/monitor-temp.sh <<'EOF'
#!/bin/bash

# S.A.M.I. - Monitor de Temperatura para Raspberry Pi

while true; do
    temp=$(vcgencmd measure_temp | cut -d= -f2 | cut -d\' -f1)
    temp_int=${temp%.*}
    
    if [ $temp_int -gt 70 ]; then
        echo "ALERTA: Temperatura alta: ${temp}°C"
        # Aquí puedes agregar lógica para enviar alertas
    fi
    
    echo "$(date): Temperatura: ${temp}°C"
    sleep 30
done
EOF

chmod +x /opt/sami/monitor-temp.sh
print_success "Script de monitoreo creado"

# Crear servicio systemd para monitoreo de temperatura
print_message "Creando servicio de monitoreo de temperatura..."
sudo tee /etc/systemd/system/sami-temp-monitor.service > /dev/null <<EOF
[Unit]
Description=SAMI Temperature Monitor
After=network.target

[Service]
Type=simple
User=pi
ExecStart=/opt/sami/monitor-temp.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable sami-temp-monitor
print_success "Servicio de monitoreo creado"

# Configurar auto-start
print_message "Configurando auto-start..."
sudo tee /etc/systemd/system/sami.service > /dev/null <<EOF
[Unit]
Description=SAMI - Sistema Automático de Monitoreo Inteligente
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/sami/sami-system
ExecStart=/opt/sami/sami-system/scripts/deployment/raspberry-pi-start.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable sami
print_success "Auto-start configurado"

# Crear script de inicio específico para Raspberry Pi
print_message "Creando script de inicio para Raspberry Pi..."
cat > /opt/sami/sami-system/scripts/deployment/raspberry-pi-start.sh <<'EOF'
#!/bin/bash

# S.A.M.I. - Raspberry Pi Start Script

echo "Iniciando S.A.M.I. en Raspberry Pi..."

# Activar entorno virtual
source /opt/sami/venv/bin/activate

# Configurar variables de entorno
export PYTHONPATH=/opt/sami/sami-system/backend
export SAMI_CONFIG=/opt/sami/.env

# Iniciar servicios
cd /opt/sami/sami-system

# Iniciar base de datos
sudo systemctl start postgresql
sudo systemctl start redis

# Esperar a que los servicios estén listos
sleep 10

# Iniciar backend
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Iniciar frontend
cd ../frontend
npm start &
FRONTEND_PID=$!

# Guardar PIDs
echo $BACKEND_PID > /tmp/sami-backend.pid
echo $FRONTEND_PID > /tmp/sami-frontend.pid

echo "SAMI iniciado en Raspberry Pi"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Accede a: http://$(hostname -I | awk '{print $1}')"
EOF

chmod +x /opt/sami/sami-system/scripts/deployment/raspberry-pi-start.sh
print_success "Script de inicio creado"

# Crear script de parada
print_message "Creando script de parada..."
cat > /opt/sami/stop-sami.sh <<'EOF'
#!/bin/bash

# S.A.M.I. - Stop Script

echo "Deteniendo S.A.M.I. en Raspberry Pi..."

# Detener procesos
if [ -f /tmp/sami-backend.pid ]; then
    kill $(cat /tmp/sami-backend.pid) 2>/dev/null || true
    rm /tmp/sami-backend.pid
fi

if [ -f /tmp/sami-frontend.pid ]; then
    kill $(cat /tmp/sami-frontend.pid) 2>/dev/null || true
    rm /tmp/sami-frontend.pid
fi

# Detener servicios
sudo systemctl stop sami-temp-monitor
sudo systemctl stop sami

echo "SAMI detenido"
EOF

chmod +x /opt/sami/stop-sami.sh
print_success "Script de parada creado"

# Configurar swap para Raspberry Pi
print_message "Configurando swap..."
sudo dphys-swapfile swapoff
sudo sed -i 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=1024/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
print_success "Swap configurado"

# Crear backup inicial
print_message "Creando backup inicial..."
sudo -u postgres pg_dump sami_db > /opt/sami/backup_initial.sql
print_success "Backup inicial creado"

print_success "Deployment en Raspberry Pi completado exitosamente!"
print_message "Para iniciar SAMI: sudo systemctl start sami"
print_message "Para detener SAMI: /opt/sami/stop-sami.sh"
print_message "Para optimizar: /opt/sami/optimize-raspberry-pi.sh"
print_message "Accede a: http://$(hostname -I | awk '{print $1}')"
print_warning "Reinicia el sistema para aplicar todas las optimizaciones"
