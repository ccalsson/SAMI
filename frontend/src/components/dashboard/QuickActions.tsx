import { useState } from 'react'
import { useRouter } from 'next/router'
import { 
  UserPlusIcon, 
  CogIcon, 
  DocumentTextIcon, 
  CameraIcon,
  MicrophoneIcon,
  MapIcon
} from '@heroicons/react/24/outline'

export default function QuickActions() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState<string | null>(null)

  const actions = [
    {
      name: 'Agregar Empleado',
      description: 'Registrar nuevo empleado en el sistema',
      icon: UserPlusIcon,
      color: 'blue',
      href: '/employees/new',
      action: () => router.push('/employees/new'),
    },
    {
      name: 'Generar Reporte',
      description: 'Crear reporte diario o personalizado',
      icon: DocumentTextIcon,
      color: 'green',
      href: '/reports/generate',
      action: () => router.push('/reports/generate'),
    },
    {
      name: 'Configurar Cámara',
      description: 'Ajustar configuración de cámaras',
      icon: CameraIcon,
      color: 'purple',
      href: '/cameras/settings',
      action: () => router.push('/cameras/settings'),
    },
    {
      name: 'Probar Voz',
      description: 'Probar sistema de interacción por voz',
      icon: MicrophoneIcon,
      color: 'indigo',
      href: '/voice/test',
      action: () => router.push('/voice/test'),
    },
    {
      name: 'Ver GPS',
      description: 'Monitorear ubicaciones en tiempo real',
      icon: MapIcon,
      color: 'yellow',
      href: '/gps/map',
      action: () => router.push('/gps/map'),
    },
    {
      name: 'Configuración',
      description: 'Ajustar configuración del sistema',
      icon: CogIcon,
      color: 'gray',
      href: '/settings',
      action: () => router.push('/settings'),
    },
  ]

  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600 hover:bg-blue-100',
    green: 'bg-green-50 text-green-600 hover:bg-green-100',
    purple: 'bg-purple-50 text-purple-600 hover:bg-purple-100',
    indigo: 'bg-indigo-50 text-indigo-600 hover:bg-indigo-100',
    yellow: 'bg-yellow-50 text-yellow-600 hover:bg-yellow-100',
    gray: 'bg-gray-50 text-gray-600 hover:bg-gray-100',
  }

  const handleAction = async (action: () => void, name: string) => {
    setIsLoading(name)
    try {
      // Simular delay para mostrar loading
      await new Promise(resolve => setTimeout(resolve, 500))
      action()
    } finally {
      setIsLoading(null)
    }
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Acciones Rápidas</h3>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {actions.map((action) => (
          <button
            key={action.name}
            onClick={() => handleAction(action.action, action.name)}
            disabled={isLoading === action.name}
            className={`relative group rounded-lg p-4 text-left transition-colors duration-200 ${
              colorClasses[action.color as keyof typeof colorClasses]
            } ${isLoading === action.name ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            <div className="flex items-center">
              <action.icon className="h-6 w-6 mr-3" />
              <div className="flex-1">
                <h4 className="text-sm font-medium">{action.name}</h4>
                <p className="text-xs opacity-75 mt-1">{action.description}</p>
              </div>
              {isLoading === action.name && (
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-current border-t-transparent"></div>
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
