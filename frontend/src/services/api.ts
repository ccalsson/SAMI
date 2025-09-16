import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('sami_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('sami_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const login = async (email: string, password: string) => {
  const formData = new FormData()
  formData.append('username', email)
  formData.append('password', password)
  
  const response = await api.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const getCurrentUser = async () => {
  const response = await api.get('/auth/me')
  return response.data
}

export const logout = async () => {
  const response = await api.post('/auth/logout')
  return response.data
}

// System API
export const getSystemStatus = async () => {
  const response = await api.get('/status')
  return response.data
}

export const getHealthCheck = async () => {
  const response = await api.get('/health')
  return response.data
}

// Employees API
export const getEmployees = async (params?: any) => {
  const response = await api.get('/employees', { params })
  return response.data
}

export const getEmployee = async (id: number) => {
  const response = await api.get(`/employees/${id}`)
  return response.data
}

export const createEmployee = async (data: any) => {
  const response = await api.post('/employees', data)
  return response.data
}

export const updateEmployee = async (id: number, data: any) => {
  const response = await api.put(`/employees/${id}`, data)
  return response.data
}

export const deleteEmployee = async (id: number) => {
  const response = await api.delete(`/employees/${id}`)
  return response.data
}

// Assets API
export const getAssets = async (params?: any) => {
  const response = await api.get('/assets', { params })
  return response.data
}

export const getAsset = async (id: number) => {
  const response = await api.get(`/assets/${id}`)
  return response.data
}

export const createAsset = async (data: any) => {
  const response = await api.post('/assets', data)
  return response.data
}

export const updateAsset = async (id: number, data: any) => {
  const response = await api.put(`/assets/${id}`, data)
  return response.data
}

export const deleteAsset = async (id: number) => {
  const response = await api.delete(`/assets/${id}`)
  return response.data
}

// Projects API
export const getProjects = async (params?: any) => {
  const response = await api.get('/projects', { params })
  return response.data
}

export const getProject = async (id: number) => {
  const response = await api.get(`/projects/${id}`)
  return response.data
}

export const createProject = async (data: any) => {
  const response = await api.post('/projects', data)
  return response.data
}

export const updateProject = async (id: number, data: any) => {
  const response = await api.put(`/projects/${id}`, data)
  return response.data
}

export const deleteProject = async (id: number) => {
  const response = await api.delete(`/projects/${id}`)
  return response.data
}

// Events API
export const getEvents = async (params?: any) => {
  const response = await api.get('/events', { params })
  return response.data
}

export const getEvent = async (id: number) => {
  const response = await api.get(`/events/${id}`)
  return response.data
}

export const acknowledgeEvent = async (id: number) => {
  const response = await api.post(`/events/${id}/acknowledge`)
  return response.data
}

// Fuel API
export const getFuelTransactions = async (params?: any) => {
  const response = await api.get('/fuel/transactions', { params })
  return response.data
}

export const getFuelTanks = async () => {
  const response = await api.get('/fuel/tanks')
  return response.data
}

export const getFuelConsumption = async (params?: any) => {
  const response = await api.get('/fuel/consumption', { params })
  return response.data
}

// GPS API
export const getVehicles = async () => {
  const response = await api.get('/gps/vehicles')
  return response.data
}

export const getVehicleLocation = async (vehicleId: string) => {
  const response = await api.get(`/gps/vehicles/${vehicleId}/location`)
  return response.data
}

export const getVehicleHistory = async (vehicleId: string, params?: any) => {
  const response = await api.get(`/gps/vehicles/${vehicleId}/history`, { params })
  return response.data
}

// Voice API
export const getVoiceStatus = async () => {
  const response = await api.get('/voice/status')
  return response.data
}

export const getVoiceCommands = async () => {
  const response = await api.get('/voice/commands')
  return response.data
}

export const recordVoice = async (duration: number = 5) => {
  const response = await api.post('/voice/record', { duration })
  return response.data
}

export const speakText = async (text: string) => {
  const response = await api.post('/voice/speak', { text })
  return response.data
}

// Camera API
export const getCameras = async () => {
  const response = await api.get('/camera/status')
  return response.data
}

export const getCameraStatus = async (cameraId: string) => {
  const response = await api.get(`/camera/${cameraId}/status`)
  return response.data
}

export const startCamera = async (cameraId: string) => {
  const response = await api.post(`/camera/${cameraId}/start`)
  return response.data
}

export const stopCamera = async (cameraId: string) => {
  const response = await api.post(`/camera/${cameraId}/stop`)
  return response.data
}

export const captureImage = async (cameraId: string) => {
  const response = await api.post(`/camera/${cameraId}/capture`)
  return response.data
}

// RFID API
export const getRFIDReaders = async () => {
  const response = await api.get('/rfid/readers/status')
  return response.data
}

export const getRFIDReaderStatus = async (readerId: string) => {
  const response = await api.get(`/rfid/readers/${readerId}/status`)
  return response.data
}

export const startRFIDReader = async (readerId: string) => {
  const response = await api.post(`/rfid/readers/${readerId}/start`)
  return response.data
}

export const stopRFIDReader = async (readerId: string) => {
  const response = await api.post(`/rfid/readers/${readerId}/stop`)
  return response.data
}

export const getRFIDTransactions = async (params?: any) => {
  const response = await api.get('/rfid/transactions/recent', { params })
  return response.data
}

// Reports API
export const getReportTemplates = async () => {
  const response = await api.get('/reports/templates')
  return response.data
}

export const generateReport = async (data: any) => {
  const response = await api.post('/reports/generate', data)
  return response.data
}

export const getReportHistory = async (params?: any) => {
  const response = await api.get('/reports/history', { params })
  return response.data
}

export const getReportStatistics = async (period: string = 'month') => {
  const response = await api.get('/reports/statistics', { params: { period } })
  return response.data
}

export default api
