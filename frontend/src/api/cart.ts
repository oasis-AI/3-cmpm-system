import request from './request'

export const cartApi = {
  /** 获取购物车 */
  list() {
    return request.get('/cart')
  },

  /** 加入购物车 */
  add(data: { sku_id: number; quantity: number }) {
    return request.post('/cart', data)
  },

  /** 更新数量 */
  update(id: number, quantity: number) {
    return request.put(`/cart/${id}`, { quantity })
  },

  /** 删除 */
  remove(id: number) {
    return request.delete(`/cart/${id}`)
  },

  /** 清空 */
  clear() {
    return request.delete('/cart')
  },
}
