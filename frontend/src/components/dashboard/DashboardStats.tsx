import { useQuery } from 'react-query'
import { getEmployees, getAssets, getProjects, getEvents } from '../../services/api'
import StatCard from '../ui/StatCard'
import LoadingSpinner from '../ui/LoadingSpinner'

interface DashboardStatsProps {
  systemStatus?: any
  loading?: boolean
}

export default function DashboardStats({ systemStatus, loading }: DashboardStatsProps) {
  const { data: employees, isLoading: employeesLoading } = useQuery(
    'employees-stats',
    () => getEmployees({ limit: 1 }),
    {
      select: (data) => data.length,
    }
  )

  const { data: assets, isLoading: assetsLoading } = useQuery(
    'assets-stats',
    () => getAssets({ limit: 1 }),
    {
      select: (data) => data.length,
    }
  )

  const { data: projects, isLoading: projectsLoading } = useQuery(
    'projects-stats',
    () => getProjects({ limit: 1 }),
    {
      select: (data) => data.length,
    }
  )

  const { data: events, isLoading: eventsLoading } = useQuery(
    'events-stats',
    () => getEvents({ limit: 1 }),
    {
      select: (data) => data.length,
    }
  )

  if (loading || employeesLoading || assetsLoading || projectsLoading || eventsLoading) {
    return (
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <LoadingSpinner size="sm" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  const stats = [
    {
      name: 'Empleados',
      value: employees || 0,
      icon: '👥',
      color: 'blue',
      change: '+12%',
      changeType: 'positive',
    },
    {
      name: 'Activos',
      value: assets || 0,
      icon: '🔧',
      color: 'green',
      change: '+5%',
      changeType: 'positive',
    },
    {
      name: 'Proyectos',
      value: projects || 0,
      icon: '🏗️',
      change: '+2%',
      changeType: 'positive',
    },
    {
      name: 'Eventos Hoy',
      value: events || 0,
      icon: '⚠️',
      color: 'yellow',
      change: '-8%',
      changeType: 'negative',
    },
  ]

  return (
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat) => (
        <StatCard key={stat.name} {...stat} />
      ))}
    </div>
  )
}
