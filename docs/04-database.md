# 04 · 数据库设计

> 所有表均含 `id`、`created_at`、`updated_at`、`deleted_at` 字段。  
> 软删除：`deleted_at IS NULL` 表示有效记录。  
> 禁止使用 SQLAlchemy `relationship()`，跨表关联通过 Service 层手动处理。

---

## 表总览

| 表名 | 说明 |
|------|------|
| `users` | 三角色统一用户表 |
| `merchants` | 商户详情与审核状态 |
| `addresses` | 用户收货地址 |
| `categories` | 商品分类（两级） |
| `products` | 商品 |
| `product_skus` | 商品规格（SKU） |
| `product_images` | 商品图片 |
| `inventory` | 库存（与 sku 1:1） |
| `cart_items` | 购物车 |
| `orders` | 订单 |
| `order_items` | 订单行项目 |
| `points_rules` | 积分规则配置 |
| `points_records` | 积分流水 |
| `reviews` | 商品评价 |
| `activities` | 活动 |
| `activity_products` | 活动-商品 |
| `activity_participants` | 活动参与记录 |
| `phone_recharge_orders` | 话费/流量快捷兑换记录 |
| `announcements` | 商城公告 |

---

## 详细表结构

### users（用户表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT UNSIGNED | PK, AUTO_INCREMENT | |
| phone | VARCHAR(11) | UNIQUE, NOT NULL | 手机号（账号） |
| email | VARCHAR(100) | UNIQUE, NULL | 邮箱（可选） |
| nickname | VARCHAR(50) | NOT NULL | 昵称 |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt 哈希 |
| role | ENUM('user','merchant','admin') | NOT NULL, DEFAULT 'user' | 角色 |
| points_balance | INT UNSIGNED | NOT NULL, DEFAULT 0 | 积分余额（冗余字段，以 points_records 流水为准） |
| avatar_url | VARCHAR(500) | NULL | 头像 |
| is_banned | TINYINT(1) | NOT NULL, DEFAULT 0 | 是否封禁 |
| created_at | DATETIME | NOT NULL, DEFAULT NOW() | |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW() ON UPDATE NOW() | |
| deleted_at | DATETIME | NULL | 软删除时间 |

---

### merchants（商户信息表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT UNSIGNED | PK | |
| user_id | BIGINT UNSIGNED | NOT NULL | 关联 users.id |
| merchant_name | VARCHAR(100) | NOT NULL | 商户名称 |
| contact_name | VARCHAR(50) | NOT NULL | 联系人姓名 |
| contact_phone | VARCHAR(11) | NOT NULL | 联系电话 |
| business_license | VARCHAR(500) | NULL | 营业执照图片URL |
| status | ENUM('pending','approved','rejected') | NOT NULL, DEFAULT 'pending' | 审核状态 |
| reject_reason | VARCHAR(500) | NULL | 拒绝原因 |
| approved_at | DATETIME | NULL | 审核通过时间 |
| reviewed_by | BIGINT UNSIGNED | NULL | 审核管理员 user_id |
| created_at | DATETIME | NOT NULL | |
| updated_at | DATETIME | NOT NULL | |
| deleted_at | DATETIME | NULL | |

---

### addresses（收货地址表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT UNSIGNED | PK | |
| user_id | BIGINT UNSIGNED | NOT NULL | 关联 users.id |
| receiver_name | VARCHAR(50) | NOT NULL | 收件人姓名 |
| receiver_phone | VARCHAR(11) | NOT NULL | 收件人电话 |
| province | VARCHAR(20) | NOT NULL | 省 |
| city | VARCHAR(20) | NOT NULL | 市 |
| district | VARCHAR(20) | NOT NULL | 区/县 |
| detail | VARCHAR(200) | NOT NULL | 详细地址 |
| is_default | TINYINT(1) | NOT NULL, DEFAULT 0 | 是否默认地址 |
| created_at | DATETIME | NOT NULL | |
| updated_at | DATETIME | NOT NULL | |
| deleted_at | DATETIME | NULL | |

---

### categories（商品分类表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT UNSIGNED | PK | |
| parent_id | INT UNSIGNED | NULL | 父分类ID，NULL表示一级 |
| name | VARCHAR(50) | NOT NULL | 分类名称 |
| icon_url | VARCHAR(500) | NULL | 分类图标 |
| sort_order | INT | NOT NULL, DEFAULT 0 | 排序权重 |
| created_at | DATETIME | NOT NULL | |
| updated_at | DATETIME | NOT NULL | |
| deleted_at | DATETIME | NULL | |

---

### products（商品表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT UNSIGNED | PK | |
| merchant_id | BIGINT UNSIGNED | NOT NULL | 关联 merchants.id |
| category_id | INT UNSIGNED | NOT NULL | 关联 categories.id |
| name | VARCHAR(200) | NOT NULL | 商品名称 |
| description | TEXT | NULL | 商品详情（富文本/图文） |
| cover_image | VARCHAR(500) | NOT NULL | 主图URL |
| min_points | INT UNSIGNED | NOT NULL | 最低积分（用于列表展示） |
| cash_supplement | DECIMAL(10,2) | NOT NULL, DEFAULT 0.00 | 需补差额现金（0则纯积分兑） |
| tags | VARCHAR(200) | NULL | 标签，逗号分隔（精选,爆品,新品） |
| brand | VARCHAR(100) | NULL | 品牌 |
| status | ENUM('on_sale','off_shelf','pending') | NOT NULL, DEFAULT 'pending' | 上架状态 |
| total_sales | INT UNSIGNED | NOT NULL, DEFAULT 0 | 总销量（冗余） |
| review_count | INT UNSIGNED | NOT NULL, DEFAULT 0 | 评价数（冗余） |
| good_review_rate | DECIMAL(5,2) | NOT NULL, DEFAULT 100.00 | 好评率（冗余） |
| is_self_operated | TINYINT(1) | NOT NULL, DEFAULT 0 | 是否自营（甄选标签） |
| created_at | DATETIME | NOT NULL | |
| updated_at | DATETIME | NOT NULL | |
| deleted_at | DATETIME | NULL | |

---

### product_skus（商品规格/SKU表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT UNSIGNED | PK | |
| product_id | BIGINT UNSIGNED | NOT NULL | 关联 products.id |
| sku_name | VARCHAR(200) | NOT NULL | 规格描述（如"红色/XL"） |
| points_price | INT UNSIGNED | NOT NULL | 该规格所需积分 |
| cash_supplement | DECIMAL(10,2) | NOT NULL, DEFAULT 0.00 | 该规格补差现金 |
| created_at | DATETIME | NOT NULL | |
| updated_at | DATETIME | NOT NULL | |
| deleted_at | DATETIME | NULL | |

---

### product_images（商品图片表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT UNSIGNED | PK | |
| product_id | BIGINT UNSIGNED | NOT NULL | 关联 products.id |
| image_url | VARCHAR(500) | NOT NULL | 图片URL |
| image_type | ENUM('gallery','detail') | NOT NULL, DEFAULT 'gallery' | 轮播图/详情图 |
| sort_order | INT | NOT NULL, DEFAULT 0 | 排序 |
| created_at | DATETIME | NOT NULL | |
| deleted_at | DATETIME | NULL | |

---

### inventory（库存表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT UNSIGNED | PK | |
| sku_id | BIGINT UNSIGNED | UNIQUE, NOT NULL | 关联 product_skus.id（1:1） |
| product_id | BIGINT UNSIGNED | NOT NULL | 冗余，便于查询 |
| quantity | INT UNSIGNED | NOT NULL, DEFAULT 0 | 实际库存 |
| locked_quantity | INT UNSIGNED | NOT NULL, DEFAULT 0 | 已预占未发货 |
| low_stock_alert | INT UNSIGNED | NOT NULL, DEFAULT 10 | 低库存预警阈值 |
| created_at | DATETIME | NOT NULL | |
| updated_at | DATETIME | NOT NULL | |
| deleted_at | DATETIME | NULL | |

---

### cart_items（购物车表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT UNSIGNED | PK | |
| user_id | BIGINT UNSIGNED | NOT NULL | |
| product_id | BIGINT UNSIGNED | NOT NULL | |
| sku_id | BIGINT UNSIGNED | NOT NULL | |
| quantity | INT UNSIGNED | NOT NULL, DEFAULT 1 | |
| created_at | DATETIME | NOT NULL | |
| updated_at | DATETIME | NOT NULL | |
| deleted_at | DATETIME | NULL | |

UNIQUE KEY `uk_user_sku` (`user_id`, `sku_id`) — 同一规格合并数量

---

### orders（订单表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT UNSIGNED | PK | |
| order_no | VARCHAR(32) | UNIQUE, NOT NULL | 订单号（时间戳+随机） |
| user_id | BIGINT UNSIGNED | NOT NULL | |
| merchant_id | BIGINT UNSIGNED | NOT NULL | |
| total_points | INT UNSIGNED | NOT NULL | 订单总积分 |
| total_cash | DECIMAL(10,2) | NOT NULL, DEFAULT 0.00 | 补差现金总额 |
| status | ENUM('pending','paid','shipped','delivered','completed','cancelled','refunding','refunded') | NOT NULL | 订单状态 |
| receiver_name | VARCHAR(50) | NOT NULL | 快照：收件人 |
| receiver_phone | VARCHAR(11) | NOT NULL | 快照：手机号 |
| receiver_address | VARCHAR(300) | NOT NULL | 快照：完整地址 |
| express_company | VARCHAR(50) | NULL | 快递公司 |
| express_no | VARCHAR(50) | NULL | 快递单号 |
| shipped_at | DATETIME | NULL | 发货时间 |
| delivered_at | DATETIME | NULL | 确认收货时间 |
| remark | VARCHAR(500) | NULL | 用户备注 |
| created_at | DATETIME | NOT NULL | |
| updated_at | DATETIME | NOT NULL | |
| deleted_at | DATETIME | NULL | |

---

### order_items（订单明细表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT UNSIGNED | PK | |
| order_id | BIGINT UNSIGNED | NOT NULL | |
| product_id | BIGINT UNSIGNED | NOT NULL | |
| sku_id | BIGINT UNSIGNED | NOT NULL | |
| product_name | VARCHAR(200) | NOT NULL | 快照：商品名 |
| sku_name | VARCHAR(200) | NOT NULL | 快照：规格名 |
| cover_image | VARCHAR(500) | NOT NULL | 快照：主图 |
| points_price | INT UNSIGNED | NOT NULL | 快照：积分单价 |
| cash_supplement | DECIMAL(10,2) | NOT NULL | 快照：补差单价 |
| quantity | INT UNSIGNED | NOT NULL | 数量 |
| created_at | DATETIME | NOT NULL | |
| deleted_at | DATETIME | NULL | |

---

### points_rules（积分规则表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT UNSIGNED | PK | |
| rule_type | ENUM('register','recharge_package') | NOT NULL | 规则类型 |
| name | VARCHAR(100) | NOT NULL | 规则名称 |
| points_amount | INT UNSIGNED | NOT NULL | 积分数量 |
| cash_price | DECIMAL(10,2) | NULL | 充值套餐现金价（仅 recharge_package 有效） |
| is_active | TINYINT(1) | NOT NULL, DEFAULT 1 | 是否启用 |
| created_at | DATETIME | NOT NULL | |
| updated_at | DATETIME | NOT NULL | |
| deleted_at | DATETIME | NULL | |

---

### points_records（积分流水表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT UNSIGNED | PK | |
| user_id | BIGINT UNSIGNED | NOT NULL | |
| type | ENUM('register','recharge','exchange','refund','manual_add','manual_deduct','phone_recharge','flow_recharge') | NOT NULL | 类型 |
| amount | INT | NOT NULL | 变化量（正=增加，负=减少） |
| balance_after | INT UNSIGNED | NOT NULL | 操作后余额 |
| description | VARCHAR(200) | NULL | 描述（如"兑换商品：xxx"） |
| ref_id | BIGINT UNSIGNED | NULL | 关联ID（order_id / recharge_order_id） |
| operator_id | BIGINT UNSIGNED | NULL | 操作人ID（手动调整时为管理员ID） |
| created_at | DATETIME | NOT NULL | |
| deleted_at | DATETIME | NULL | |

---

### reviews（商品评价表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT UNSIGNED | PK | |
| order_id | BIGINT UNSIGNED | NOT NULL | |
| order_item_id | BIGINT UNSIGNED | NOT NULL | |
| user_id | BIGINT UNSIGNED | NOT NULL | |
| product_id | BIGINT UNSIGNED | NOT NULL | |
| sku_id | BIGINT UNSIGNED | NOT NULL | |
| rating | TINYINT UNSIGNED | NOT NULL | 评分 1-5 |
| content | VARCHAR(1000) | NULL | 评价内容 |
| is_anonymous | TINYINT(1) | NOT NULL, DEFAULT 0 | 是否匿名 |
| created_at | DATETIME | NOT NULL | |
| deleted_at | DATETIME | NULL | |

---

### activities（活动表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT UNSIGNED | PK | |
| title | VARCHAR(200) | NOT NULL | 活动标题 |
| description | TEXT | NULL | 活动说明 |
| type | ENUM('discount','flash_sale','gift','sign_in') | NOT NULL | 活动类型 |
| banner_url | VARCHAR(500) | NULL | 活动Banner图 |
| discount_rate | DECIMAL(4,2) | NULL | 折扣率（0.8=8折），discount类型有效 |
| quota | INT UNSIGNED | NULL | 参与限额，NULL为不限 |
| start_at | DATETIME | NOT NULL | 开始时间 |
| end_at | DATETIME | NOT NULL | 结束时间 |
| status | ENUM('draft','active','ended') | NOT NULL, DEFAULT 'draft' | 活动状态 |
| created_by | BIGINT UNSIGNED | NOT NULL | 创建人（管理员ID） |
| created_at | DATETIME | NOT NULL | |
| updated_at | DATETIME | NOT NULL | |
| deleted_at | DATETIME | NULL | |

---

### activity_products（活动商品关联表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT UNSIGNED | PK | |
| activity_id | INT UNSIGNED | NOT NULL | |
| product_id | BIGINT UNSIGNED | NOT NULL | |
| apply_status | ENUM('pending','approved','rejected') | NOT NULL, DEFAULT 'pending' | 商户申请状态 |
| created_at | DATETIME | NOT NULL | |
| deleted_at | DATETIME | NULL | |

---

### activity_participants（活动参与记录表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT UNSIGNED | PK | |
| activity_id | INT UNSIGNED | NOT NULL | |
| user_id | BIGINT UNSIGNED | NOT NULL | |
| created_at | DATETIME | NOT NULL | |
| deleted_at | DATETIME | NULL | |

---

### phone_recharge_orders（话费/流量快捷兑换记录）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT UNSIGNED | PK | |
| user_id | BIGINT UNSIGNED | NOT NULL | |
| recharge_type | ENUM('phone','flow') | NOT NULL | 话费 / 流量 |
| phone_number | VARCHAR(11) | NOT NULL | 充值手机号 |
| package_name | VARCHAR(100) | NOT NULL | 套餐名（如"10元话费"、"500M流量"） |
| points_cost | INT UNSIGNED | NOT NULL | 消耗积分 |
| status | ENUM('success','failed') | NOT NULL, DEFAULT 'success' | Demo中直接成功 |
| created_at | DATETIME | NOT NULL | |
| deleted_at | DATETIME | NULL | |

---

### announcements（商城公告表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT UNSIGNED | PK | |
| title | VARCHAR(200) | NOT NULL | 公告标题 |
| content | TEXT | NOT NULL | 公告内容 |
| is_pinned | TINYINT(1) | NOT NULL, DEFAULT 0 | 是否置顶 |
| published_at | DATETIME | NULL | 发布时间，NULL为草稿 |
| created_by | BIGINT UNSIGNED | NOT NULL | 发布管理员ID |
| created_at | DATETIME | NOT NULL | |
| updated_at | DATETIME | NOT NULL | |
| deleted_at | DATETIME | NULL | |

---

## 手动关联规范（替代 relationship）

```python
# ✅ 正确：Service层手动查询关联数据
class ProductService:
    def get_product_detail(self, db, product_id: int):
        product = db.execute(
            select(Product).where(
                Product.id == product_id,
                Product.deleted_at.is_(None)
            )
        ).scalar_one_or_none()

        skus = db.execute(
            select(ProductSku).where(
                ProductSku.product_id == product_id,
                ProductSku.deleted_at.is_(None)
            )
        ).scalars().all()

        images = db.execute(
            select(ProductImage).where(
                ProductImage.product_id == product_id,
                ProductImage.deleted_at.is_(None)
            )
        ).scalars().all()

        return {"product": product, "skus": skus, "images": images}

# ❌ 禁止：使用 relationship 懒加载
# product.skus  # 禁止
```
