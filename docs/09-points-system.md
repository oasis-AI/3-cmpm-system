# 09 · 积分系统设计

## 1. 积分来源与消耗总览

```
积分来源（+）                    积分消耗（-）
─────────────────            ─────────────────
注册赠送                      兑换普通商品
模拟充值                      话费快捷兑换
确认收货奖励（可选）            流量快捷兑换
管理员手动增加                 管理员手动扣减
退款退还                      （退款场景，回正方向）
```

---

## 2. points_records 流水类型

| type | 流向 | 触发场景 | amount 符号 |
|------|------|---------|-------------|
| `register` | + | 用户注册成功 | 正 |
| `recharge` | + | 用户模拟充值 | 正 |
| `exchange` | - | 用户下单成功（积分扣减） | 负 |
| `refund` | + | 售后退款通过，积分返还 | 正 |
| `phone_recharge` | - | 话费快捷兑换 | 负 |
| `flow_recharge` | - | 流量快捷兑换 | 负 |
| `manual_add` | + | 管理员手动增加 | 正 |
| `manual_deduct` | - | 管理员手动扣减 | 负 |

---

## 3. 注册送积分流程

```
POST /api/v1/auth/register
    │
    ▼
1. 验证手机号不重复
2. bcrypt 哈希密码
3. INSERT INTO users (phone, password_hash, nickname, role='user', points_balance=0)
    │
    ▼
4. 查询 points_rules WHERE rule_type='register' AND is_active=1
   → 获取 register_points（如 1000）
    │
    ▼
5. 开启事务：
   a. UPDATE users SET points_balance = points_balance + register_points WHERE id = user_id
   b. INSERT INTO points_records (user_id, type='register', amount=+1000, balance_after=1000, description='注册赠送积分')
   COMMIT
    │
    ▼
6. 返回 access_token + refresh_token + user_info（含积分余额）
```

---

## 4. 模拟充值流程

```
POST /api/v1/user/points/recharge
Body: { rule_id: 3 }  ← 选择充值套餐ID
    │
    ▼
1. 查询 points_rules WHERE id=rule_id AND rule_type='recharge_package' AND is_active=1
    │
    ▼
2. 开启事务：
   a. UPDATE users SET points_balance += points_amount WHERE id = user_id
   b. INSERT INTO points_records (type='recharge', amount=+points_amount, ...)
   COMMIT
    │
    ▼
3. 返回新的积分余额
```

---

## 5. 兑换商品积分扣减（核心原子操作）

```
POST /api/v1/user/orders
    │
    ▼
【Step 1】参数验证
- 验证 sku_id 存在且商品已上架
- 验证 address_id 属于当前用户

【Step 2】检查积分余额（DB查询）
- SELECT points_balance FROM users WHERE id = user_id
- IF points_balance < total_points → raise BusinessException(42200, "积分余额不足")

【Step 3】Redis 原子预占库存（防超卖）
- key = f"inventory:stock:{sku_id}"
- 首次初始化：从 DB 读取库存写入 Redis（SETNX）
- DECR inventory:stock:{sku_id} by quantity
- IF 结果 < 0:
    INCR inventory:stock:{sku_id} by quantity（回滚）
    raise BusinessException(42201, "库存不足")

【Step 4】开启 DB 事务
4a. INSERT INTO orders (order_no, user_id, merchant_id, total_points, status='pending', ...)
4b. INSERT INTO order_items (order_id, product_id, sku_id, ...)
4c. UPDATE inventory SET locked_quantity += quantity WHERE sku_id = sku_id  ← 软锁定
4d. UPDATE users SET points_balance -= total_points WHERE id = user_id
4e. INSERT INTO points_records (type='exchange', amount=-total_points, ...)
COMMIT

【Step 5】返回订单信息
- 包含 order_no, status, total_points, receiver_info
```

---

## 6. 退款退积分流程

```
用户申请售后 → 商户处理通过（或管理员介入）

【商户/管理员通过退款】
PUT /api/v1/merchant/orders/{order_no}/refund
Body: { action: "approve" }
    │
    ▼
1. 验证订单状态为 refunding
    │
    ▼
2. 开启 DB 事务：
   a. UPDATE orders SET status='refunded' WHERE order_no = ?
   b. UPDATE inventory
      SET locked_quantity -= order_items.quantity,
          quantity += order_items.quantity   ← 归还实际库存
      WHERE sku_id IN (order_items中的sku_id)
   c. UPDATE users SET points_balance += order.total_points WHERE id = user_id
   d. INSERT INTO points_records (type='refund', amount=+total_points, description='售后退款返还')
   COMMIT
    │
    ▼
3. Redis 同步：INCR inventory:stock:{sku_id} by quantity（回滚预占）
```

---

## 7. 话费/流量快捷兑换

```
POST /api/v1/user/quick-recharge/phone
Body: { phone_number: "138...", package_name: "10元话费", points_cost: 1000 }
    │
    ▼
1. 检查积分余额 >= points_cost
2. 开启 DB 事务：
   a. UPDATE users SET points_balance -= points_cost
   b. INSERT INTO points_records (type='phone_recharge', amount=-points_cost, ...)
   c. INSERT INTO phone_recharge_orders (status='success', ...)  ← Demo中直接成功
   COMMIT
    │
    ▼
3. 返回充值结果（Demo: 直接成功提示）
```

---

## 8. Redis 防超卖方案

### 8.1 库存 Key 初始化策略

```python
def get_available_stock(redis_client, sku_id: int, db: Session) -> int:
    """
    获取可用库存，优先从 Redis 读取
    Redis 中不存在时从 DB 初始化
    """
    key = f"inventory:stock:{sku_id}"
    stock = redis_client.get(key)

    if stock is None:
        # 从 DB 读取（quantity - locked_quantity）
        inv = db.execute(
            select(Inventory).where(Inventory.sku_id == sku_id)
        ).scalar_one_or_none()

        if inv is None:
            return 0

        available = inv.quantity - inv.locked_quantity
        redis_client.set(key, available)  # 写入 Redis，无TTL（永久）
        return available

    return int(stock)
```

### 8.2 原子预占

```python
def reserve_stock(redis_client, sku_id: int, quantity: int) -> bool:
    """
    原子预占库存
    Returns: True=成功, False=库存不足
    """
    key = f"inventory:stock:{sku_id}"

    # Lua 脚本保证原子性
    lua_script = """
    local stock = tonumber(redis.call('GET', KEYS[1]) or 0)
    if stock < tonumber(ARGV[1]) then
        return -1
    end
    return redis.call('DECRBY', KEYS[1], ARGV[1])
    """
    result = redis_client.eval(lua_script, 1, key, quantity)
    return result >= 0

def release_stock(redis_client, sku_id: int, quantity: int):
    """释放预占库存（退款或下单失败回滚时调用）"""
    key = f"inventory:stock:{sku_id}"
    redis_client.incrby(key, quantity)
```

---

## 9. 积分并发安全：分布式锁

积分操作涉及"读取余额 → 判断 → 扣减"三步，高并发下需加锁：

```python
import uuid

def acquire_points_lock(redis_client, user_id: int, ttl: int = 5) -> str | None:
    """
    获取积分操作锁
    Returns: lock_value（用于释放锁），None=获取失败
    """
    key = f"lock:points:{user_id}"
    lock_value = str(uuid.uuid4())
    result = redis_client.set(key, lock_value, nx=True, ex=ttl)
    return lock_value if result else None

def release_points_lock(redis_client, user_id: int, lock_value: str):
    """释放积分锁（只有持有者才能释放）"""
    lua_script = """
    if redis.call('GET', KEYS[1]) == ARGV[1] then
        return redis.call('DEL', KEYS[1])
    end
    return 0
    """
    redis_client.eval(lua_script, 1, f"lock:points:{user_id}", lock_value)
```

使用方式（在 `order_service.create_order` 中）：
```python
lock_value = acquire_points_lock(redis, user_id)
if not lock_value:
    raise BusinessException(50000, "操作频繁，请稍后重试")
try:
    # ... 检查余额、扣积分 ...
finally:
    release_points_lock(redis, user_id, lock_value)
```

---

## 10. 积分余额一致性保障

`users.points_balance` 是冗余字段（以 `points_records` 流水汇总为准）：

- **写入时**：每次积分变动同时更新 `users.points_balance` 和写入 `points_records`，在同一事务内
- **查询时**：直接读 `users.points_balance`（快）
- **对账时**：可通过 `SELECT SUM(amount) FROM points_records WHERE user_id=?` 校验是否与余额字段一致

---

## 11. 管理员手动调整积分

```python
# admin_service.py
def adjust_user_points(db, redis, admin_id, user_id, amount, remark):
    """
    管理员手动增减积分
    amount: 正数=增加，负数=减少
    """
    lock = acquire_points_lock(redis, user_id)
    if not lock:
        raise BusinessException(50000, "用户积分正在操作中，请稍后")

    try:
        user = db.execute(select(User).where(...)).scalar_one()

        new_balance = user.points_balance + amount
        if new_balance < 0:
            raise BusinessException(40001, "扣减后余额不能为负数")

        record_type = 'manual_add' if amount > 0 else 'manual_deduct'

        # 事务
        user.points_balance = new_balance
        db.add(PointsRecord(
            user_id=user_id,
            type=record_type,
            amount=amount,
            balance_after=new_balance,
            description=remark,
            operator_id=admin_id
        ))
        db.commit()
    finally:
        release_points_lock(redis, user_id, lock)
```
