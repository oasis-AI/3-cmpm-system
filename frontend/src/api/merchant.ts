import request from './request'

export const merchantApi = {
  /** 管理端：商家申请列表 */
  adminList(params?: Record<string, any>) {
    return request.get('/admin/merchants', { params })
  },

  /** 管理端：审批 */
  adminApprove(id: number, status: number, reason?: string) {
    return request.post(`/admin/merchants/${id}/approve`, { status, reason })
  },

  /** B端：商家概览数据 */
  dashboard() {
    return request.get('/merchant/dashboard')
  },

  /** B端：更新商家信息 */
  updateInfo(data: any) {
    return request.put('/merchant/info', data)
  },
}
