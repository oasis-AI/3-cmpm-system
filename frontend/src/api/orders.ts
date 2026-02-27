import request from './request'

export const ordersApi = {
  /** C端：创建订单 */
  create(data: { sku_id: number; quantity: number; address_id: number }) {
    return request.post('/orders', data)
  },

  /** C端：我的订单列表 */
  list(params?: { page?: number; page_size?: number; status?: string }) {
    return request.get('/orders', { params })
  },

  /** C端：订单详情 */
  detail(id: number) {
    return request.get(`/orders/${id}`)
  },

  /** C端：取消订单 */
  cancel(id: number) {
    return request.post(`/orders/${id}/cancel`)
  },

  /** C端：确认收货 */
  confirm(id: number) {
    return request.post(`/orders/${id}/confirm`)
  },

  /** B端：商家订单列表 */
  merchantList(params?: { page?: number; page_size?: number; status?: string }) {
    return request.get('/merchant/orders', { params })
  },

  /** B端：发货 */
  ship(id: number, data: { express_company?: string; express_no?: string; company?: string; tracking_no?: string; [key: string]: any }) {
    return request.post(`/merchant/orders/${id}/ship`, data)
  },

  /** 管理端：所有订单 */
  adminList(params?: Record<string, any>) {
    return request.get('/admin/orders', { params })
  },

  /** C端：提交评价 */
  review(orderId: number, itemId: number, data: { rating: number; content?: string; is_anonymous?: boolean }) {
    return request.post(`/orders/${orderId}/items/${itemId}/review`, data)
  },

  /** C端：申请退款 */
  requestRefund(orderId: number, reason: string) {
    return request.post(`/orders/${orderId}/refund`, { reason })
  },
}
