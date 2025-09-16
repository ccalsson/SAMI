import { useQuery } from 'react-query'
import { getEvents } from '../../services/api'
import LoadingSpinner from '../ui/LoadingSpinner'

export default function RecentActivity() {
  const { data: events, isLoading } = useQuery(
    'recent-events',
    () => getEvents({ limit: 5 }),
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  )

  if (isLoading) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Actividad Reciente</h3>
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                <LoadingSpinner size="sm" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2 mt-1 animate-pulse"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // Datos de ejemplo para desarrollo
  const activities = [
    {
      id: 1,
      type: 'employee_check_in',
      title: 'Juan Pérez registró entrada',
      description: 'Empleado registró entrada a las 08:30',
      timestamp: 'Hace 5 minutos',
      icon: '👤',
      color: 'green',
    },
    {
      id: 2,
      type: 'asset_checkout',
      title: 'Herramienta retirada',
      description: 'Martillo neumático retirado por María García',
      timestamp: 'Hace 15 minutos',
      icon: '🔧',
      color: 'blue',
    },
    {
      id: 3,
      type: 'fuel_refill',
      title: 'Combustible repostado',
      description: 'Tanque principal repostado con 500 litros',
      timestamp: 'Hace 1 hora',
      icon: '⛽',
      color: 'yellow',
    },
    {
      id: 4,
      type: 'camera_alert',
      title: 'Alerta de cámara',
      description: 'Movimiento detectado en zona restringida',
      timestamp: 'Hace 2 horas',
      icon: '📹',
      color: 'red',
    },
    {
      id: 5,
      type: 'voice_command',
      title: 'Comando de voz ejecutado',
      description: 'SAMI respondió consulta sobre nivel de combustible',
      timestamp: 'Hace 3 horas',
      icon: '🎤',
      color: 'purple',
    },
  ]

  const getColorClasses = (color: string) => {
    const colorMap = {
      green: 'bg-green-100 text-green-800',
      blue: 'bg-blue-100 text-blue-800',
      yellow: 'bg-yellow-100 text-yellow-800',
      red: 'bg-red-100 text-red-800',
      purple: 'bg-purple-100 text-purple-800',
    }
    return colorMap[color as keyof typeof colorMap] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Actividad Reciente</h3>
      <div className="flow-root">
        <ul className="-mb-8">
          {activities.map((activity, activityIdx) => (
            <li key={activity.id}>
              <div className="relative pb-8">
                {activityIdx !== activities.length - 1 ? (
                  <span
                    className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                    aria-hidden="true"
                  />
                ) : null}
                <div className="relative flex space-x-3">
                  <div>
                    <span className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white ${getColorClasses(activity.color)}`}>
                      <span className="text-sm">{activity.icon}</span>
                    </span>
                  </div>
                  <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                    <div>
                      <p className="text-sm text-gray-900">{activity.title}</p>
                      <p className="text-sm text-gray-500">{activity.description}</p>
                    </div>
                    <div className="text-right text-sm whitespace-nowrap text-gray-500">
                      {activity.timestamp}
                    </div>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
      
      <div className="mt-4">
        <a
          href="/events"
          className="text-sm font-medium text-primary-600 hover:text-primary-500"
        >
          Ver todos los eventos
          <span className="ml-1">→</span>
        </a>
      </div>
    </div>
  )
}
