import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface UserInfo {
  id: number
  phone: string
  nickname: string
  avatar: string
  role: 'user' | 'merchant' | 'admin'
  points_balance: number
  merchant_id?: number
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem('access_token') || '')
  const refreshToken = ref<string>(localStorage.getItem('refresh_token') || '')
  const userInfo = ref<UserInfo | null>(
    JSON.parse(localStorage.getItem('user_info') || 'null')
  )

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')
  const isMerchant = computed(() => userInfo.value?.role === 'merchant')
  const isUser = computed(() => userInfo.value?.role === 'user')

  function setTokens(access: string, refresh: string) {
    token.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  function setUserInfo(info: UserInfo) {
    userInfo.value = info
    localStorage.setItem('user_info', JSON.stringify(info))
  }

  function updatePoints(balance: number) {
    if (userInfo.value) {
      userInfo.value.points_balance = balance
      localStorage.setItem('user_info', JSON.stringify(userInfo.value))
    }
  }

  function logout() {
    token.value = ''
    refreshToken.value = ''
    userInfo.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_info')
  }

  return {
    token,
    refreshToken,
    userInfo,
    isLoggedIn,
    isAdmin,
    isMerchant,
    isUser,
    setTokens,
    setUserInfo,
    updatePoints,
    logout,
  }
})
