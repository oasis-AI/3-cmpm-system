import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

// --------- Request interceptor ---------
request.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

// --------- Response interceptor ---------
let isRefreshing = false
let pendingQueue: Array<(token: string) => void> = []

request.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const auth = useAuthStore()
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (!auth.refreshToken) {
        auth.logout()
        router.push('/login')
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve) => {
          pendingQueue.push((newToken: string) => {
            originalRequest.headers.Authorization = `Bearer ${newToken}`
            resolve(request(originalRequest))
          })
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const res: any = await axios.post('/api/v1/auth/refresh', {
          refresh_token: auth.refreshToken,
        })
        const newToken = res.data.access_token
        auth.setTokens(newToken, auth.refreshToken)
        pendingQueue.forEach((cb) => cb(newToken))
        pendingQueue = []
        originalRequest.headers.Authorization = `Bearer ${newToken}`
        return request(originalRequest)
      } catch {
        auth.logout()
        router.push('/login')
        return Promise.reject(error)
      } finally {
        isRefreshing = false
      }
    }

    const message =
      error.response?.data?.message || error.response?.data?.detail || '请求失败，请稍后重试'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default request
