import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import Layout from '../components/layout/Layout'
import DashboardStats from '../components/dashboard/DashboardStats'
import RecentActivity from '../components/dashboard/RecentActivity'
import SystemStatus from '../components/dashboard/SystemStatus'
import QuickActions from '../components/dashboard/QuickActions'
import { useQuery } from 'react-query'
import { getSystemStatus } from '../services/api'

export default function Dashboard() {
  const { user } = useAuth()
  const [activeTab, setActiveTab] = useState('overview')

  const { data: systemStatus, isLoading: systemLoading } = useQuery(
    'system-status',
    getSystemStatus,
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  )

  const tabs = [
    { id: 'overview', name: 'Resumen', icon: '📊' },
    { id: 'employees', name: 'Personal', icon: '👥' },
    { id: 'assets', name: 'Activos', icon: '🔧' },
    { id: 'projects', name: 'Proyectos', icon: '🏗️' },
    { id: 'reports', name: 'Reportes', icon: '📋' },
  ]

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Bienvenido, {user?.first_name} {user?.last_name}
              </h1>
              <p className="text-gray-600">
                Panel de control del Sistema SAMI
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Última actualización</p>
              <p className="text-sm font-medium text-gray-900">
                {new Date().toLocaleString('es-ES')}
              </p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white shadow rounded-lg">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Stats Cards */}
                <DashboardStats systemStatus={systemStatus} loading={systemLoading} />

                {/* Quick Actions */}
                <QuickActions />

                {/* System Status */}
                <SystemStatus systemStatus={systemStatus} loading={systemLoading} />

                {/* Recent Activity */}
                <RecentActivity />
              </div>
            )}

            {activeTab === 'employees' && (
              <div className="text-center py-12">
                <p className="text-gray-500">Módulo de Personal en desarrollo</p>
              </div>
            )}

            {activeTab === 'assets' && (
              <div className="text-center py-12">
                <p className="text-gray-500">Módulo de Activos en desarrollo</p>
              </div>
            )}

            {activeTab === 'projects' && (
              <div className="text-center py-12">
                <p className="text-gray-500">Módulo de Proyectos en desarrollo</p>
              </div>
            )}

            {activeTab === 'reports' && (
              <div className="text-center py-12">
                <p className="text-gray-500">Módulo de Reportes en desarrollo</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  )
}
