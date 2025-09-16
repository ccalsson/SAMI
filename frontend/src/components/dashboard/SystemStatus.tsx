import { CheckCircleIcon, ExclamationTriangleIcon, XCircleIcon } from '@heroicons/react/24/outline'

interface SystemStatusProps {
  systemStatus?: any
  loading?: boolean
}

export default function SystemStatus({ systemStatus, loading }: SystemStatusProps) {
  if (loading) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Estado del Sistema</h3>
        <div className="animate-pulse space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex items-center space-x-3">
              <div className="h-4 w-4 bg-gray-200 rounded-full"></div>
              <div className="h-4 bg-gray-200 rounded w-1/3"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  const services = [
    {
      name: 'Base de Datos',
      status: systemStatus?.database === 'connected' ? 'online' : 'offline',
      description: 'Conexión a PostgreSQL',
    },
    {
      name: 'Redis Cache',
      status: systemStatus?.redis === 'connected' ? 'online' : 'offline',
      description: 'Cache en memoria',
    },
    {
      name: 'Servicio de IA',
      status: systemStatus?.ai_service?.is_initialized ? 'online' : 'offline',
      description: 'Reconocimiento facial y detección',
    },
    {
      name: 'Servicio de Voz',
      status: systemStatus?.voice_service?.is_initialized ? 'online' : 'offline',
      description: 'Interacción por voz',
    },
    {
      name: 'Cámaras',
      status: systemStatus?.camera_service?.running ? 'online' : 'offline',
      description: `${systemStatus?.camera_service?.active_cameras || 0} cámaras activas`,
    },
    {
      name: 'RFID',
      status: systemStatus?.rfid_service?.running ? 'online' : 'offline',
      description: `${systemStatus?.rfid_service?.active_readers || 0} lectores activos`,
    },
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'offline':
        return <XCircleIcon className="h-5 w-5 text-red-500" />
      default:
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'text-green-600'
      case 'offline':
        return 'text-red-600'
      default:
        return 'text-yellow-600'
    }
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Estado del Sistema</h3>
      <div className="space-y-3">
        {services.map((service) => (
          <div key={service.name} className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {getStatusIcon(service.status)}
              <div>
                <p className="text-sm font-medium text-gray-900">{service.name}</p>
                <p className="text-xs text-gray-500">{service.description}</p>
              </div>
            </div>
            <span className={`text-sm font-medium ${getStatusColor(service.status)}`}>
              {service.status === 'online' ? 'En línea' : 'Desconectado'}
            </span>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500">Última actualización</span>
          <span className="text-gray-900">
            {new Date().toLocaleTimeString('es-ES')}
          </span>
        </div>
      </div>
    </div>
  )
}
