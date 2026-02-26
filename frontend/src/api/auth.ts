import request from './request'

export const authApi = {
  /** C端用户注册 */
  register(data: { phone: string; password: string; sms_code: string }) {
    return request.post('/auth/register', data)
  },

  /** 登录（C端/B端通用） */
  login(data: { phone: string; password: string }) {
    return request.post('/auth/login', data)
  },

  /** 商家注册 */
  merchantRegister(data: {
    phone: string
    password: string
    sms_code: string
    company_name: string
    business_license: string
  }) {
    return request.post('/auth/merchant-register', data)
  },

  /** 刷新 token */
  refresh(refresh_token: string) {
    return request.post('/auth/refresh', { refresh_token })
  },

  /** 登出 */
  logout() {
    return request.post('/auth/logout')
  },

  /** 发送短信验证码 (mock) */
  sendSms(phone: string) {
    return request.post('/auth/send-sms', { phone })
  },

  /** 获取当前用户信息 */
  profile() {
    return request.get('/auth/profile')
  },
}
