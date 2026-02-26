# 08 · 开发规范

## 1. Python / 后端规范

### 1.1 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 文件名 | snake_case | `auth_service.py` |
| 类名 | PascalCase | `UserService`, `ProductModel` |
| 函数/方法 | snake_case | `get_product_detail()` |
| 变量 | snake_case | `user_id`, `points_balance` |
| 常量 | UPPER_SNAKE_CASE | `JWT_ALGORITHM = "HS256"` |
| 路由 path | kebab-case | `/api/v1/points-rules` |
| 数据库表名 | snake_case（复数） | `users`, `product_skus` |
| 数据库字段 | snake_case | `deleted_at`, `merchant_id` |

### 1.2 目录/代码组织

- **Router 只做以下事情**：参数解析、依赖注入、调用 Service、返回响应
- **Service 包含所有业务逻辑**：跨表查询、事务、Redis操作、积分计算
- **Model 只定义表结构**：字段、索引、软删除查询的静态方法

```python
# ✅ 正确的 Router
@router.post("/orders")
async def create_order(
    body: OrderCreateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = await order_service.create_order(db, current_user.id, body)
    return success(data=order)

# ❌ 错误：在 Router 写业务逻辑
@router.post("/orders")
async def create_order(body: OrderCreateSchema, db: Session = Depends(get_db)):
    # 不应该在这里写积分检查、库存扣减等
    user = db.execute(select(User).where(...)).scalar()
    if user.points_balance < body.total_points:
        raise ...
```

### 1.3 软删除规范

```python
# ✅ 所有查询必须加 deleted_at IS NULL
stmt = select(Product).where(
    Product.id == product_id,
    Product.deleted_at.is_(None)  # 必须！
)

# ✅ 删除操作使用软删除
def soft_delete(db: Session, model_instance):
    model_instance.deleted_at = datetime.utcnow()
    db.commit()

# ❌ 禁止物理删除
db.delete(product)  # 禁止
```

### 1.4 事务规范

```python
# 涉及多表写操作必须使用事务
def create_order(db: Session, user_id: int, body: OrderCreateSchema):
    try:
        # 1. 检查积分
        # 2. Redis 预占库存
        # 3. 写订单
        # 4. 写订单明细
        # 5. 扣减积分（写 points_records）
        # 6. 更新 users.points_balance
        db.commit()
    except Exception as e:
        db.rollback()
        # 释放 Redis 预占的库存
        raise
```

### 1.5 Pydantic Schema 规范

```python
# Request Schema（输入验证）
class OrderCreateSchema(BaseModel):
    address_id: int
    sku_id: int
    quantity: int = Field(ge=1, le=99)
    remark: Optional[str] = Field(None, max_length=500)

# Response Schema（输出格式化）
class OrderResponse(BaseModel):
    order_no: str
    total_points: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

### 1.6 异常处理

```python
# 自定义业务异常
class BusinessException(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

# 使用
raise BusinessException(42200, "积分余额不足")

# 全局处理器统一捕获，返回标准格式
```

---

## 2. Vue / 前端规范

### 2.1 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 组件文件名 | PascalCase | `ProductCard.vue`, `OrderList.vue` |
| 页面文件名 | PascalCase | `Home.vue`, `ProductDetail.vue` |
| Props | camelCase | `productId`, `isLoading` |
| Emit 事件 | kebab-case | `@update-status`, `@confirm-order` |
| 变量/函数 | camelCase | `userInfo`, `fetchProducts()` |
| CSS 类名 | kebab-case | `.product-card`, `.btn-primary` |
| Store | camelCase + use前缀 | `useAuthStore`, `useCartStore` |

### 2.2 组件规范

```vue
<!-- ✅ 使用 Composition API + TypeScript -->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

interface Props {
  productId: number
  isLoading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false
})

const emit = defineEmits<{
  addToCart: [skuId: number, quantity: number]
}>()

const authStore = useAuthStore()
// ...
</script>

<template>
  <!-- 单一根元素 -->
  <div class="product-card">
    <!-- ... -->
  </div>
</template>

<style scoped lang="scss">
.product-card {
  // 组件样式使用 scoped
}
</style>
```

### 2.3 API 请求规范

```typescript
// api/ 目录下按模块组织，统一使用封装的 request
// api/products.ts
import { request } from './request'

export const productApi = {
  getList: (params: ProductListParams) =>
    request.get('/public/products', { params }),

  getDetail: (id: number) =>
    request.get(`/public/products/${id}`),

  create: (data: ProductCreateData) =>
    request.post('/merchant/products', data),
}

// ✅ 在组件中使用
const { data } = await productApi.getList({ page: 1, category_id: 1 })
```

### 2.4 Pinia Store 规范

```typescript
// stores/auth.ts
export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const userInfo = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')
  const isMerchant = computed(() => userInfo.value?.role === 'merchant')

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('access_token', newToken)
  }

  function logout() {
    token.value = null
    userInfo.value = null
    localStorage.removeItem('access_token')
  }

  return { token, userInfo, isLoggedIn, isAdmin, isMerchant, setToken, logout }
})
```

---

## 3. Git 规范

### 3.1 分支策略

```
main          # 稳定主分支，只接受 merge
└── dev       # 开发集成分支
    ├── feature/user-auth         # 新功能
    ├── feature/product-module
    ├── fix/cart-quantity-bug     # Bug修复
    └── chore/update-deps         # 依赖/配置更新
```

### 3.2 Commit 信息格式

```
<type>(<scope>): <subject>

type:
  feat     - 新功能
  fix      - Bug修复
  docs     - 文档
  style    - 格式（不影响逻辑）
  refactor - 重构
  test     - 测试
  chore    - 构建/依赖/配置

scope:
  auth / user / product / order / points / merchant / admin / frontend

示例：
  feat(auth): 实现JWT登录与Token刷新
  fix(order): 修复并发下单时积分重复扣减bug
  feat(frontend): 完成商品详情页SKU选择交互
  docs: 更新数据库设计文档
```

---

## 4. 代码注释规范

### Python
```python
def create_order(db: Session, user_id: int, body: OrderCreateSchema) -> Order:
    """
    创建兑换订单

    原子操作流程：
    1. 检查用户积分余额是否足够
    2. Redis DECR 预占库存（防超卖）
    3. 写入 orders / order_items 记录
    4. 扣减积分（写 points_records + 更新 users.points_balance）

    Args:
        db: 数据库会话
        user_id: 下单用户ID
        body: 订单创建参数

    Raises:
        BusinessException(42200): 积分余额不足
        BusinessException(42201): 库存不足

    Returns:
        创建成功的 Order 对象
    """
```

### Vue/TypeScript
```typescript
/**
 * 加入购物车
 * 未登录时弹出登录提示，不直接跳转
 */
async function addToCart(skuId: number) {
  if (!authStore.isLoggedIn) {
    showLoginDialog.value = true
    return
  }
  // ...
}
```

---

## 5. 代码风格工具

### 后端
```
# requirements.txt 中包含
ruff         # Python linter + formatter（替代 flake8 + black）
```

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py311"
```

### 前端
```json
// .eslintrc 使用 @vue/eslint-config-typescript
// .prettierrc
{
  "semi": false,
  "singleQuote": true,
  "printWidth": 100,
  "trailingComma": "es5"
}
```

---

## 6. 环境变量规范

- `.env` 文件不提交 Git（已加入 `.gitignore`）
- 提供 `.env.example` 作为模板
- 后端用 Pydantic `BaseSettings` 读取并类型验证
- 前端用 `import.meta.env.VITE_*` 前缀

```env
# .env.example
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=中国移动积分商城
```
