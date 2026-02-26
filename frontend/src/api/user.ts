import request from './request'

export const userApi = {
  /** 收货地址列表 */
  addresses() {
    return request.get('/user/addresses')
  },

  /** 新增地址 */
  addAddress(data: any) {
    return request.post('/user/addresses', data)
  },

  /** 更新地址 */
  updateAddress(id: number, data: any) {
    return request.put(`/user/addresses/${id}`, data)
  },

  /** 删除地址 */
  deleteAddress(id: number) {
    return request.delete(`/user/addresses/${id}`)
  },

  /** 修改密码 */
  changePassword(data: { old_password: string; new_password: string }) {
    return request.post('/user/change-password', data)
  },

  /** 更新个人信息 */
  updateProfile(data: { nickname?: string; avatar?: string }) {
    return request.put('/user/profile', data)
  },

  /** 管理端：用户列表 */
  adminList(params?: Record<string, any>) {
    return request.get('/admin/users', { params })
  },
}
