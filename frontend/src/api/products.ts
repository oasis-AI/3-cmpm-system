import request from './request'

export const productsApi = {
  /** 商品列表（游客可用） */
  list(params?: {
    page?: number
    page_size?: number
    category_id?: number
    keyword?: string
    sort?: string
    min_points?: number
    max_points?: number
  }) {
    return request.get('/products', { params })
  },

  /** 商品详情 */
  detail(id: number) {
    return request.get(`/products/${id}`)
  },

  /** 商品分类列表 */
  categories() {
    return request.get('/products/categories')
  },

  /** B端：商家商品列表 */
  merchantList(params?: { page?: number; page_size?: number; status?: string }) {
    return request.get('/merchant/products', { params })
  },

  /** B端：创建商品 */
  create(data: any) {
    return request.post('/merchant/products', data)
  },

  /** B端：更新商品 */
  update(id: number, data: any) {
    return request.put(`/merchant/products/${id}`, data)
  },

  /** B端：删除商品（软删除） */
  delete(id: number) {
    return request.delete(`/merchant/products/${id}`)
  },

  /** B端：上/下架 */
  toggleStatus(id: number, status: string) {
    return request.patch(`/merchant/products/${id}/status`, { status })
  },
}
