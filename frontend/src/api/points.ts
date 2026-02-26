import request from './request'

export const pointsApi = {
  /** 我的积分 + 余额 */
  balance() {
    return request.get('/points/balance')
  },

  /** 积分明细 */
  records(params?: { page?: number; page_size?: number; type?: number }) {
    return request.get('/points/records', { params })
  },

  /** 快速充值（话费/流量 mock） */
  quickRecharge(data: { phone: string; amount: number; type: 'phone' | 'data' }) {
    return request.post('/points/quick-recharge', data)
  },

  /** 充值历史 */
  rechargeHistory(params?: { page?: number; page_size?: number }) {
    return request.get('/points/recharge-history', { params })
  },

  /** 管理端：积分规则列表 */
  adminRules() {
    return request.get('/admin/points-rules')
  },

  /** 管理端：创建/更新积分规则 */
  adminSaveRule(idOrData: number | null | undefined | any, data?: any) {
    const payload = data ?? idOrData
    const id = data != null ? idOrData : payload?.id
    return id
      ? request.put(`/admin/points-rules/${id}`, payload)
      : request.post('/admin/points-rules', payload)
  },
}
