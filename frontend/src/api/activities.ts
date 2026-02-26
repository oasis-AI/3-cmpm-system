import request from './request'

export const activitiesApi = {
  /** 活动列表（C端） */
  list(params?: { page?: number; page_size?: number }) {
    return request.get('/activities', { params })
  },

  /** 活动详情（C端） */
  detail(id: number) {
    return request.get(`/activities/${id}`)
  },

  /** 参与活动（C端） */
  participate(id: number) {
    return request.post(`/activities/${id}/participate`)
  },

  /** 公告列表（C端） */
  announcements(params?: { page?: number; page_size?: number }) {
    return request.get('/announcements', { params })
  },

  /** 管理端：创建活动 */
  adminCreate(data: any) {
    return request.post('/admin/activities', data)
  },

  /** 管理端：更新活动 */
  adminUpdate(id: number, data: any) {
    return request.put(`/admin/activities/${id}`, data)
  },

  /** 管理端：公告管理 */
  adminAnnouncements: {
    list: (params?: any) => request.get('/admin/announcements', { params }),
    create: (data: any) => request.post('/admin/announcements', data),
    update: (id: number, data: any) => request.put(`/admin/announcements/${id}`, data),
    delete: (id: number) => request.delete(`/admin/announcements/${id}`),
  },
}
