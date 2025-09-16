# S.A.M.I. - Documentación de API

## Sistema Automático de Monitoreo Inteligente

### Información General

- **Base URL**: `http://localhost:8000/api/v1`
- **Versión**: 1.0.0
- **Formato**: JSON
- **Autenticación**: Bearer Token (JWT)

### Autenticación

#### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=tu@email.com&password=tu_password
```

**Respuesta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### Obtener Usuario Actual
```http
GET /auth/me
Authorization: Bearer <token>
```

**Respuesta:**
```json
{
  "id": 1,
  "first_name": "Juan",
  "last_name": "Pérez",
  "email": "juan@empresa.com",
  "role": "admin",
  "department": "IT",
  "is_active": true
}
```

### Empleados

#### Listar Empleados
```http
GET /employees?skip=0&limit=100&search=juan&role=operator
Authorization: Bearer <token>
```

#### Crear Empleado
```http
POST /employees
Authorization: Bearer <token>
Content-Type: application/json

{
  "first_name": "María",
  "last_name": "García",
  "email": "maria@empresa.com",
  "employee_id": "EMP001",
  "role": "operator",
  "department": "Operaciones",
  "rfid_tag": "RFID123456"
}
```

#### Registrar Entrada
```http
POST /employees/check-in
Authorization: Bearer <token>
Content-Type: application/json

{
  "employee_id": 1,
  "location": "Oficina Principal",
  "method": "rfid"
}
```

### Activos

#### Listar Activos
```http
GET /assets?skip=0&limit=100&asset_type=vehicle&status=available
Authorization: Bearer <token>
```

#### Crear Activo
```http
POST /assets
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Excavadora CAT 320",
  "description": "Excavadora de 20 toneladas",
  "asset_code": "EXC001",
  "asset_type": "machinery",
  "serial_number": "CAT320-2023-001",
  "brand": "Caterpillar",
  "model": "320",
  "rfid_tag": "RFID789012"
}
```

### Proyectos

#### Listar Proyectos
```http
GET /projects?skip=0&limit=100&status=active
Authorization: Bearer <token>
```

#### Crear Proyecto
```http
POST /projects
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Construcción Edificio A",
  "description": "Construcción de edificio de oficinas",
  "project_code": "PROJ001",
  "client_name": "Constructora ABC",
  "start_date": "2024-01-01",
  "planned_end_date": "2024-12-31",
  "budget_total": 1000000.00,
  "location_name": "Av. Principal 123"
}
```

### Eventos

#### Listar Eventos
```http
GET /events?skip=0&limit=50&event_type=employee_check_in&status=pending
Authorization: Bearer <token>
```

#### Reconocer Evento
```http
POST /events/{event_id}/acknowledge
Authorization: Bearer <token>
```

### Combustible

#### Listar Transacciones de Combustible
```http
GET /fuel/transactions?skip=0&limit=100&transaction_type=refill&start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <token>
```

#### Obtener Nivel de Combustible
```http
GET /fuel/tanks
Authorization: Bearer <token>
```

### GPS

#### Obtener Ubicaciones de Vehículos
```http
GET /gps/vehicles
Authorization: Bearer <token>
```

#### Obtener Ubicación de Vehículo
```http
GET /gps/vehicles/{vehicle_id}/location
Authorization: Bearer <token>
```

#### Obtener Historial de Vehículo
```http
GET /gps/vehicles/{vehicle_id}/history?start_time=2024-01-01T00:00:00&end_time=2024-01-31T23:59:59
Authorization: Bearer <token>
```

### Cámaras

#### Obtener Estado de Cámaras
```http
GET /camera/status
Authorization: Bearer <token>
```

#### Iniciar Cámara
```http
POST /camera/{camera_id}/start
Authorization: Bearer <token>
```

#### Capturar Imagen
```http
POST /camera/{camera_id}/capture
Authorization: Bearer <token>
```

### RFID

#### Obtener Estado de Lectores
```http
GET /rfid/readers/status
Authorization: Bearer <token>
```

#### Iniciar Lector
```http
POST /rfid/readers/{reader_id}/start
Authorization: Bearer <token>
```

#### Obtener Transacciones Recientes
```http
GET /rfid/transactions/recent?limit=50&reader_id=reader_1
Authorization: Bearer <token>
```

### Voz

#### Obtener Estado del Sistema de Voz
```http
GET /voice/status
Authorization: Bearer <token>
```

#### Grabar y Procesar Voz
```http
POST /voice/record?duration=5&location=surtidor
Authorization: Bearer <token>
```

#### Sintetizar Voz
```http
POST /voice/speak
Authorization: Bearer <token>
Content-Type: application/json

{
  "text": "Hola, soy SAMI. ¿En qué puedo ayudarte?"
}
```

### Reportes

#### Generar Reporte
```http
POST /reports/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "template_name": "Reporte Diario Operativo",
  "report_date": "2024-01-15",
  "recipients": ["admin@empresa.com", "supervisor@empresa.com"]
}
```

#### Obtener Plantillas de Reportes
```http
GET /reports/templates
Authorization: Bearer <token>
```

#### Obtener Historial de Reportes
```http
GET /reports/history?limit=50&template_name=Reporte Diario Operativo
Authorization: Bearer <token>
```

### Sistema

#### Estado del Sistema
```http
GET /status
Authorization: Bearer <token>
```

#### Health Check
```http
GET /health
```

### Códigos de Error

| Código | Descripción |
|--------|-------------|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

### Ejemplos de Respuestas de Error

#### Error de Validación
```json
{
  "error": "Validation Error",
  "status_code": 422,
  "details": {
    "email": ["Email inválido"],
    "password": ["La contraseña debe tener al menos 8 caracteres"]
  }
}
```

#### Error de Autenticación
```json
{
  "error": "Could not validate credentials",
  "status_code": 401
}
```

### Rate Limiting

- **API General**: 10 requests/segundo
- **Login**: 5 requests/minuto
- **Uploads**: 1 request/segundo

### Paginación

Todos los endpoints que devuelven listas soportan paginación:

- `skip`: Número de registros a omitir (default: 0)
- `limit`: Número máximo de registros a devolver (default: 100, max: 1000)

**Ejemplo:**
```http
GET /employees?skip=20&limit=10
```

### Filtros

Muchos endpoints soportan filtros:

- `search`: Búsqueda de texto
- `status`: Filtro por estado
- `date_from` / `date_to`: Filtro por rango de fechas
- `sort_by`: Campo para ordenar
- `sort_order`: `asc` o `desc`

**Ejemplo:**
```http
GET /events?search=entrada&status=pending&date_from=2024-01-01&sort_by=created_at&sort_order=desc
```

### Webhooks

El sistema puede enviar webhooks para eventos importantes:

#### Configurar Webhook
```http
POST /webhooks
Authorization: Bearer <token>
Content-Type: application/json

{
  "url": "https://tu-servidor.com/webhook",
  "events": ["employee_check_in", "asset_checkout", "fuel_low_level"],
  "secret": "tu-secreto-webhook"
}
```

#### Payload del Webhook
```json
{
  "event_type": "employee_check_in",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "employee_id": 1,
    "employee_name": "Juan Pérez",
    "location": "Oficina Principal",
    "method": "rfid"
  }
}
```

### SDKs y Librerías

#### Python
```python
import requests

# Configurar cliente
base_url = "http://localhost:8000/api/v1"
headers = {"Authorization": "Bearer tu_token"}

# Ejemplo de uso
response = requests.get(f"{base_url}/employees", headers=headers)
employees = response.json()
```

#### JavaScript
```javascript
// Configurar cliente
const baseURL = 'http://localhost:8000/api/v1';
const token = 'tu_token';

// Ejemplo de uso
fetch(`${baseURL}/employees`, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

### Testing

#### Postman Collection
Descarga la colección de Postman desde: `/docs/postman-collection.json`

#### cURL Examples
```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=tu@email.com&password=tu_password"

# Obtener empleados
curl -X GET "http://localhost:8000/api/v1/employees" \
  -H "Authorization: Bearer tu_token"
```

### Changelog

#### v1.0.0 (2024-01-15)
- Lanzamiento inicial
- API completa para todos los módulos
- Autenticación JWT
- Documentación completa

---

*Para más información, visita la documentación interactiva en `/docs` o contacta al equipo de desarrollo.*
