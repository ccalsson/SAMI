# S.A.M.I. - Guía de Usuario

## Sistema Automático de Monitoreo Inteligente

### Tabla de Contenidos

1. [Introducción](#introducción)
2. [Acceso al Sistema](#acceso-al-sistema)
3. [Dashboard Principal](#dashboard-principal)
4. [Gestión de Personal](#gestión-de-personal)
5. [Control de Activos](#control-de-activos)
6. [Monitoreo de Proyectos](#monitoreo-de-proyectos)
7. [Sistema de Cámaras](#sistema-de-cámaras)
8. [Interacción por Voz](#interacción-por-voz)
9. [Reportes y Análisis](#reportes-y-análisis)
10. [Configuración](#configuración)
11. [Solución de Problemas](#solución-de-problemas)

---

## Introducción

S.A.M.I. (Sistema Automático de Monitoreo Inteligente) es una solución integral diseñada para empresas de movimiento de suelos y logística. El sistema integra múltiples tecnologías para automatizar el control de activos, personal y operaciones.

### Características Principales

- **Control de Personal**: Registro automático de entrada/salida con RFID y reconocimiento facial
- **Gestión de Activos**: Control completo de herramientas, vehículos y equipos
- **Monitoreo con IA**: Cámaras inteligentes que detectan eventos automáticamente
- **Interacción por Voz**: Comunicación natural con el sistema mediante comandos de voz
- **GPS y Tracking**: Monitoreo en tiempo real de vehículos y equipos
- **Reportes Automáticos**: Generación y distribución automática de reportes

---

## Acceso al Sistema

### Primera Configuración

1. **Acceder al Sistema**
   - Abrir navegador web
   - Ir a `http://tu-servidor-sami` o `http://localhost`
   - La página de login se abrirá automáticamente

2. **Credenciales Iniciales**
   - **Email**: `admin@sami.local`
   - **Contraseña**: `sami123` (cambiar en primera sesión)

3. **Cambiar Contraseña**
   - Ir a Configuración > Mi Perfil
   - Hacer clic en "Cambiar Contraseña"
   - Ingresar contraseña actual y nueva
   - Confirmar cambios

### Roles de Usuario

| Rol | Permisos |
|-----|----------|
| **Administrador** | Acceso completo al sistema |
| **Supervisor** | Gestión de personal y activos |
| **Operador** | Consultas y operaciones básicas |
| **Manager** | Reportes y análisis |

---

## Dashboard Principal

El dashboard es la pantalla principal del sistema y muestra información clave en tiempo real.

### Elementos del Dashboard

#### 1. Tarjetas de Estadísticas
- **Empleados**: Total, presentes, ausentes
- **Activos**: Total, en uso, disponibles
- **Proyectos**: Activos, completados, en pausa
- **Eventos**: Total del día, pendientes, críticos

#### 2. Estado del Sistema
- **Base de Datos**: Estado de conexión
- **Cámaras**: Cámaras activas/inactivas
- **RFID**: Lectores funcionando
- **GPS**: Dispositivos conectados

#### 3. Actividad Reciente
- Últimos eventos del sistema
- Alertas y notificaciones
- Acciones realizadas por usuarios

#### 4. Acciones Rápidas
- Agregar empleado
- Generar reporte
- Configurar cámara
- Probar sistema de voz

---

## Gestión de Personal

### Registrar Nuevo Empleado

1. **Acceder al Módulo**
   - Ir a Personal > Empleados
   - Hacer clic en "Agregar Empleado"

2. **Completar Información**
   - **Datos Personales**: Nombre, apellido, email
   - **Datos Laborales**: ID empleado, rol, departamento
   - **Identificación**: Código RFID (opcional)
   - **Foto**: Subir foto para reconocimiento facial

3. **Guardar y Activar**
   - Revisar información
   - Hacer clic en "Guardar"
   - El empleado quedará activo automáticamente

### Control de Asistencia

#### Registro Automático (RFID)
1. El empleado pasa su tarjeta RFID por el lector
2. El sistema registra automáticamente la entrada/salida
3. Se muestra confirmación en pantalla

#### Registro Manual
1. Ir a Personal > Control de Asistencia
2. Seleccionar empleado
3. Hacer clic en "Registrar Entrada" o "Registrar Salida"
4. Confirmar acción

### Consultar Asistencia

1. **Por Empleado**
   - Ir a Personal > Empleados
   - Hacer clic en el nombre del empleado
   - Ver historial de asistencia

2. **Por Fecha**
   - Ir a Personal > Reportes de Asistencia
   - Seleccionar rango de fechas
   - Filtrar por departamento o rol

---

## Control de Activos

### Registrar Nuevo Activo

1. **Acceder al Módulo**
   - Ir a Activos > Inventario
   - Hacer clic en "Agregar Activo"

2. **Completar Información**
   - **Básica**: Nombre, descripción, código
   - **Tipo**: Vehículo, herramienta, equipo
   - **Especificaciones**: Marca, modelo, año
   - **Identificación**: Código RFID, número de serie
   - **Ubicación**: Ubicación actual

3. **Configurar Estado**
   - Estado inicial (Disponible, En Uso, Mantenimiento)
   - Fecha de próxima mantención
   - Costo y valor

### Control de Entrada/Salida

#### Retirar Activo
1. Ir a Activos > Control de Activos
2. Buscar activo por código o nombre
3. Hacer clic en "Retirar"
4. Seleccionar empleado responsable
5. Establecer fecha de devolución estimada
6. Confirmar retiro

#### Devolver Activo
1. Ir a Activos > Activos en Uso
2. Seleccionar activo a devolver
3. Hacer clic en "Devolver"
4. Verificar estado del activo
5. Agregar observaciones si es necesario
6. Confirmar devolución

### Mantenimiento de Activos

1. **Programar Mantenimiento**
   - Ir a Activos > Mantenimiento
   - Seleccionar activo
   - Hacer clic en "Programar Mantenimiento"
   - Establecer fecha y tipo de mantenimiento

2. **Registrar Mantenimiento Realizado**
   - Ir a Activos > Mantenimiento
   - Seleccionar mantenimiento programado
   - Hacer clic en "Marcar como Completado"
   - Agregar observaciones y costo

---

## Monitoreo de Proyectos

### Crear Nuevo Proyecto

1. **Acceder al Módulo**
   - Ir a Proyectos > Gestión de Proyectos
   - Hacer clic en "Nuevo Proyecto"

2. **Información Básica**
   - **Nombre**: Nombre del proyecto
   - **Cliente**: Empresa cliente
   - **Ubicación**: Dirección del proyecto
   - **Fechas**: Inicio y fin planificado

3. **Presupuesto**
   - Presupuesto total
   - Desglose por categorías
   - Moneda

4. **Recursos Asignados**
   - Empleados asignados
   - Activos necesarios
   - Equipos requeridos

### Seguimiento de Proyecto

#### Actualizar Progreso
1. Ir a Proyectos > [Nombre del Proyecto]
2. Hacer clic en "Actualizar Progreso"
3. Establecer porcentaje completado
4. Agregar observaciones
5. Guardar cambios

#### Registrar Gastos
1. Ir a Proyectos > [Nombre del Proyecto] > Gastos
2. Hacer clic en "Agregar Gasto"
3. Seleccionar categoría (Combustible, Materiales, etc.)
4. Ingresar monto y descripción
5. Adjuntar comprobante si es necesario

#### Asignar Recursos
1. Ir a Proyectos > [Nombre del Proyecto] > Recursos
2. Hacer clic en "Asignar Empleado" o "Asignar Activo"
3. Seleccionar recurso disponible
4. Establecer fechas de asignación
5. Confirmar asignación

---

## Sistema de Cámaras

### Configurar Cámaras

1. **Acceder al Módulo**
   - Ir a Cámaras > Configuración
   - Hacer clic en "Agregar Cámara"

2. **Configuración Básica**
   - **Nombre**: Identificación de la cámara
   - **Ubicación**: Lugar donde está instalada
   - **URL**: Dirección IP o RTSP de la cámara
   - **Resolución**: Calidad de video

3. **Configuración de IA**
   - Habilitar reconocimiento facial
   - Configurar detección de eventos
   - Establecer sensibilidad

### Monitoreo en Tiempo Real

1. **Ver Cámaras**
   - Ir a Cámaras > Vista en Vivo
   - Seleccionar cámara a visualizar
   - La imagen se actualiza automáticamente

2. **Capturar Imagen**
   - Hacer clic en "Capturar" durante la visualización
   - La imagen se guarda automáticamente
   - Se puede descargar o compartir

3. **Ver Eventos Detectados**
   - Ir a Cámaras > Eventos
   - Filtrar por cámara, fecha o tipo de evento
   - Hacer clic en evento para ver detalles

### Entrenar Reconocimiento Facial

1. **Acceder a Entrenamiento**
   - Ir a Cámaras > Reconocimiento Facial
   - Hacer clic en "Entrenar Nuevo Empleado"

2. **Capturar Fotos**
   - Seleccionar empleado de la lista
   - Capturar 3-5 fotos desde diferentes ángulos
   - Asegurar buena iluminación y claridad

3. **Procesar y Guardar**
   - El sistema procesará las imágenes automáticamente
   - Se mostrará confirmación de éxito
   - El empleado quedará registrado para reconocimiento

---

## Interacción por Voz

### Configurar Sistema de Voz

1. **Acceder a Configuración**
   - Ir a Voz > Configuración
   - Verificar que el micrófono esté conectado

2. **Probar Micrófono**
   - Hacer clic en "Probar Micrófono"
   - Hablar por 3-5 segundos
   - Verificar que se detecte el audio

3. **Configurar Altavoces**
   - Seleccionar dispositivo de audio
   - Ajustar volumen
   - Probar síntesis de voz

### Comandos de Voz Disponibles

#### Consultas de Información
- **"¿Cuánto combustible queda?"** - Nivel de combustible
- **"¿Cuántos empleados hay?"** - Conteo de empleados
- **"¿Dónde está [nombre]?"** - Ubicación de empleado
- **"¿Estado del proyecto?"** - Estado de proyectos activos

#### Control de Activos
- **"Registrar entrada"** - Check-in de empleado
- **"Registrar salida"** - Check-out de empleado
- **"Reportar problema"** - Crear reporte de incidente

#### Sistema
- **"Estado del sistema"** - Estado general
- **"Ayuda"** - Lista de comandos disponibles

### Usar el Sistema de Voz

1. **Activar Grabación**
   - Hacer clic en el ícono de micrófono
   - O decir "SAMI" para activar por voz

2. **Hablar Comando**
   - Esperar el tono de confirmación
   - Hablar claramente el comando
   - Esperar respuesta del sistema

3. **Verificar Respuesta**
   - El sistema responderá por voz
   - Se mostrará transcripción en pantalla
   - Se registrará la interacción

---

## Reportes y Análisis

### Generar Reportes

#### Reporte Diario
1. Ir a Reportes > Generar Reporte
2. Seleccionar "Reporte Diario Operativo"
3. Elegir fecha
4. Seleccionar destinatarios
5. Hacer clic en "Generar"

#### Reporte Personalizado
1. Ir a Reportes > Reporte Personalizado
2. Seleccionar tipo de datos
3. Establecer filtros y fechas
4. Elegir formato (PDF, Excel)
5. Configurar destinatarios
6. Generar reporte

### Programar Reportes Automáticos

1. **Acceder a Programación**
   - Ir a Reportes > Programación
   - Hacer clic en "Nueva Programación"

2. **Configurar Frecuencia**
   - Seleccionar tipo (Diario, Semanal, Mensual)
   - Establecer hora de envío
   - Elegir días de la semana (si aplica)

3. **Configurar Contenido**
   - Seleccionar plantilla de reporte
   - Establecer filtros automáticos
   - Configurar destinatarios

4. **Activar Programación**
   - Revisar configuración
   - Hacer clic en "Activar"
   - El sistema enviará reportes automáticamente

### Ver Historial de Reportes

1. Ir a Reportes > Historial
2. Filtrar por:
   - Tipo de reporte
   - Fecha de generación
   - Estado (Completado, Error)
3. Hacer clic en reporte para ver detalles
4. Descargar reporte si es necesario

---

## Configuración

### Configuración del Sistema

1. **Acceder a Configuración**
   - Ir a Configuración > Sistema
   - Solo disponible para administradores

2. **Configuración General**
   - Nombre de la empresa
   - Zona horaria
   - Idioma del sistema
   - Formato de fechas

3. **Configuración de Comunicación**
   - Servidor de email
   - Configuración de WhatsApp
   - Números de teléfono para alertas

4. **Configuración de Hardware**
   - Dispositivos RFID
   - Cámaras IP
   - Sensores GPS
   - Configuración de red

### Gestión de Usuarios

#### Crear Usuario
1. Ir a Configuración > Usuarios
2. Hacer clic en "Agregar Usuario"
3. Completar información personal
4. Asignar rol y permisos
5. Enviar invitación por email

#### Modificar Permisos
1. Seleccionar usuario de la lista
2. Hacer clic en "Editar Permisos"
3. Modificar roles y accesos
4. Guardar cambios

### Configuración de Alertas

1. **Acceder a Alertas**
   - Ir a Configuración > Alertas
   - Hacer clic en "Nueva Regla de Alerta"

2. **Configurar Condición**
   - Seleccionar tipo de evento
   - Establecer condiciones
   - Configurar severidad

3. **Configurar Notificación**
   - Seleccionar método (Email, WhatsApp, SMS)
   - Agregar destinatarios
   - Establecer horarios de envío

4. **Activar Alerta**
   - Revisar configuración
   - Hacer clic en "Activar"
   - La alerta quedará activa

---

## Solución de Problemas

### Problemas Comunes

#### No Puedo Iniciar Sesión
1. Verificar credenciales
2. Verificar conexión a internet
3. Limpiar caché del navegador
4. Contactar administrador

#### Las Cámaras No Funcionan
1. Verificar conexión de red
2. Verificar URL de la cámara
3. Revisar configuración de firewall
4. Reiniciar servicio de cámaras

#### El Sistema de Voz No Responde
1. Verificar micrófono conectado
2. Verificar permisos de audio
3. Probar con otro micrófono
4. Reiniciar servicio de voz

#### Los Reportes No Se Generan
1. Verificar permisos de escritura
2. Verificar espacio en disco
3. Revisar logs del sistema
4. Contactar soporte técnico

### Logs del Sistema

1. **Acceder a Logs**
   - Ir a Configuración > Logs del Sistema
   - Seleccionar tipo de log
   - Filtrar por fecha y nivel

2. **Interpretar Logs**
   - **INFO**: Información general
   - **WARNING**: Advertencias
   - **ERROR**: Errores que requieren atención
   - **CRITICAL**: Errores críticos

### Contacto de Soporte

- **Email**: soporte@sami.local
- **Teléfono**: +54 11 1234-5678
- **Horario**: Lunes a Viernes 9:00-18:00
- **Chat**: Disponible en el sistema

### Actualizaciones del Sistema

1. **Verificar Actualizaciones**
   - Ir a Configuración > Actualizaciones
   - Hacer clic en "Verificar Actualizaciones"

2. **Instalar Actualización**
   - Descargar actualización
   - Hacer backup del sistema
   - Instalar actualización
   - Verificar funcionamiento

---

## Glosario

- **Activo**: Cualquier herramienta, vehículo o equipo de la empresa
- **Check-in/Check-out**: Registro de entrada y salida de empleados
- **Evento**: Cualquier acción detectada por el sistema
- **Geofence**: Zona virtual definida para monitoreo GPS
- **RFID**: Tecnología de identificación por radiofrecuencia
- **TTS**: Text-to-Speech, síntesis de voz
- **Webhook**: Notificación automática a sistemas externos

---

*Esta guía se actualiza regularmente. Para la versión más reciente, consulta la documentación en línea del sistema.*
