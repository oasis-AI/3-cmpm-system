"""
种子数据初始化脚本
用法：cd backend && python scripts/seed.py

会创建：
  - 管理员账号
  - 1 个审核通过的商户
  - 1 个普通用户（含积分）
  - 积分规则（注册送积分 + 充值套餐）
  - 10 个商品分类
  - 20 个示例商品（含 SKU 和库存）
  - 3 条商城公告
  - 1 个进行中的活动
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timezone, timedelta
from app.core.database import SessionLocal
from app.core.config import settings
from app.core.security import hash_password
from app.models import (
    Base,
    User,
    Merchant,
    Category,
    Product,
    ProductSku,
    ProductImage,
    Inventory,
    PointsRule,
    PointsRecord,
    Activity,
    ActivityProduct,
    Announcement,
)
from app.core.database import engine

# ---- 图片占位符（Unsplash 免费图片） ----
PLACEHOLDER_IMAGES = [
    "https://images.unsplash.com/photo-1586769852836-bc069f19e1b6?w=400",
    "https://images.unsplash.com/photo-1585011664466-b7bbe92f34ef?w=400",
    "https://images.unsplash.com/photo-1542838132-92c53300491e?w=400",
    "https://images.unsplash.com/photo-1571950006419-f20e6a16d36e?w=400",
    "https://images.unsplash.com/photo-1585825882861-97e5ec8a4d76?w=400",
    "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=400",
    "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=400",
    "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400",
    "https://images.unsplash.com/photo-1612817288484-6f916006741a?w=400",
    "https://images.unsplash.com/photo-1585828922344-85c9daa264b0?w=400",
]


def now() -> datetime:
    return datetime.now(timezone.utc)


def seed():
    print("🌱 开始初始化种子数据...")

    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")

    db = SessionLocal()
    try:
        _clear_data(db)
        _seed_points_rules(db)
        admin = _seed_admin(db)
        merchant_user, merchant = _seed_merchant(db, admin.id)
        user = _seed_user(db)
        categories = _seed_categories(db)
        products = _seed_products(db, merchant.id, categories)
        _seed_activity(db, admin.id, products)
        _seed_announcements(db, admin.id)

        db.commit()
        print("\n🎉 种子数据初始化完成！")
        print("=" * 50)
        print(f"管理员  电话：{admin.phone}  密码：{settings.ADMIN_PASSWORD}")
        print(f"商户    电话：{merchant_user.phone}  密码：merchant123")
        print(f"用户    电话：{user.phone}  密码：user123  积分：{user.points_balance}")
        print("=" * 50)

    except Exception as e:
        db.rollback()
        print(f"❌ 初始化失败：{e}")
        raise
    finally:
        db.close()


def _clear_data(db):
    """清空所有业务数据（保留表结构），用于重置"""
    tables_in_order = [
        "activity_participants", "activity_products", "activities",
        "announcements", "reviews", "order_items", "orders",
        "cart_items", "inventory", "product_images", "product_skus",
        "products", "categories", "points_records", "points_rules",
        "addresses", "merchants", "users",
    ]
    for table in tables_in_order:
        db.execute(__import__("sqlalchemy").text(f"DELETE FROM {table}"))
    db.commit()
    print("🗑️  已清空旧数据")


def _seed_points_rules(db):
    rules = [
        PointsRule(
            rule_type="register",
            name="注册赠送积分",
            points_amount=1000,
            cash_price=None,
            is_active=1,
            created_at=now(), updated_at=now(),
        ),
        PointsRule(
            rule_type="recharge_package",
            name="体验套餐",
            points_amount=100,
            cash_price=0,
            is_active=1,
            created_at=now(), updated_at=now(),
        ),
        PointsRule(
            rule_type="recharge_package",
            name="基础套餐",
            points_amount=500,
            cash_price=0,
            is_active=1,
            created_at=now(), updated_at=now(),
        ),
        PointsRule(
            rule_type="recharge_package",
            name="标准套餐",
            points_amount=1000,
            cash_price=0,
            is_active=1,
            created_at=now(), updated_at=now(),
        ),
        PointsRule(
            rule_type="recharge_package",
            name="豪华套餐",
            points_amount=5000,
            cash_price=0,
            is_active=1,
            created_at=now(), updated_at=now(),
        ),
    ]
    db.add_all(rules)
    db.flush()
    print("✅ 积分规则创建完成")
    return rules


def _seed_admin(db) -> User:
    admin = User(
        phone=settings.ADMIN_PHONE,
        email="admin@cmpm.demo",
        nickname="超级管理员",
        password_hash=hash_password(settings.ADMIN_PASSWORD),
        role="admin",
        points_balance=0,
        is_banned=0,
        created_at=now(), updated_at=now(),
    )
    db.add(admin)
    db.flush()
    print(f"✅ 管理员创建：{admin.phone}")
    return admin


def _seed_merchant(db, admin_id: int):
    merchant_user = User(
        phone="13900000001",
        email="merchant@cmpm.demo",
        nickname="甄选旗舰店",
        password_hash=hash_password("merchant123"),
        role="merchant",
        points_balance=0,
        is_banned=0,
        created_at=now(), updated_at=now(),
    )
    db.add(merchant_user)
    db.flush()

    merchant = Merchant(
        user_id=merchant_user.id,
        merchant_name="中移甄选旗舰店",
        contact_name="李商户",
        contact_phone="13900000001",
        business_license=None,
        status="approved",
        approved_at=now(),
        reviewed_by=admin_id,
        created_at=now(), updated_at=now(),
    )
    db.add(merchant)
    db.flush()
    print(f"✅ 商户创建：{merchant.merchant_name}（已审核通过）")
    return merchant_user, merchant


def _seed_user(db) -> User:
    user = User(
        phone="13800000002",
        email="user@cmpm.demo",
        nickname="测试用户",
        password_hash=hash_password("user123"),
        role="user",
        points_balance=5000,
        is_banned=0,
        created_at=now(), updated_at=now(),
    )
    db.add(user)
    db.flush()

    # 写积分流水（注册送1000 + 模拟充值4000）
    db.add(PointsRecord(
        user_id=user.id, type="register", amount=1000, balance_after=1000,
        description="注册赠送积分", created_at=now(),
    ))
    db.add(PointsRecord(
        user_id=user.id, type="recharge", amount=4000, balance_after=5000,
        description="模拟充值：豪华套餐 × 4", created_at=now(),
    ))
    db.flush()
    print(f"✅ 用户创建：{user.phone}  积分：{user.points_balance}")
    return user


def _seed_categories(db) -> list[Category]:
    top_categories = [
        ("流量/专属权益", "📶"),
        ("休闲娱乐/电商平台", "🎮"),
        ("餐饮/出行/健康", "🍜"),
        ("厨具/家居/生活", "🏠"),
        ("数码电子/智能设备", "💻"),
        ("酒品茶饮/粮油零食", "🍵"),
        ("鞋靴箱包/服饰", "👟"),
        ("孕婴/运动健身", "👶"),
        ("金融/电商积分", "💳"),
        ("生活用品/纸品", "🧻"),
    ]
    categories = []
    for i, (name, _) in enumerate(top_categories):
        cat = Category(
            parent_id=None,
            name=name,
            sort_order=i,
            created_at=now(), updated_at=now(),
        )
        db.add(cat)
        categories.append(cat)
    db.flush()
    print(f"✅ 商品分类创建：{len(categories)} 个")
    return categories


PRODUCT_DATA = [
    # (名称, 分类索引, 最低积分, 标签, 是否自营, 评价数, 好评率)
    ("甄选维达抽纸 130抽×3包", 9, 1160, "精选,爆品", 1, 136317, 99.00),
    ("甄选北大荒东北珍珠米1kg", 9, 1250, "精选", 1, 299323, 99.00),
    ("甄选洁柔抽纸 130抽×3包", 9, 1160, "精选", 1, 76518, 99.00),
    ("甄选多力压榨玉米胚芽油400ml", 5, 1490, "精选,新品", 1, 15687, 98.50),
    ("甄选超能西柚洗洁精500g", 9, 980, "爆品", 1, 21715, 97.00),
    ("甄选威露士天然洗衣液2kg", 9, 2720, "精选", 1, 46489, 99.00),
    ("甄选孚日纯棉毛巾1条装", 3, 1190, "精选", 1, 218205, 99.00),
    ("甄选福临门小站稻香米1kg", 5, 1260, "精选", 1, 224250, 99.00),
    ("甄选福临门爱福家玉米油400ml", 5, 1500, "新品", 1, 12686, 98.00),
    ("甄选蓝月亮深层洗衣液2kg", 9, 2720, "爆品", 1, 29211, 99.00),
    ("500M流量包（当月有效）", 0, 800, "精选", 0, 52341, 99.50),
    ("1GB流量包（当月有效）", 0, 1500, "爆品", 0, 38920, 99.20),
    ("5GB流量包（当月有效）", 0, 6000, "精选", 0, 15678, 99.00),
    ("爱奇艺会员月卡", 1, 2500, "热门", 0, 89234, 98.00),
    ("腾讯视频会员月卡", 1, 2500, "热门", 0, 102341, 98.50),
    ("优酷会员月卡", 1, 2200, "新品", 0, 34521, 97.50),
    ("QQ音乐绿钻月卡", 1, 1800, "精选", 0, 67890, 98.00),
    ("曹操出行打车券50元", 2, 3000, "热门", 0, 23456, 97.00),
    ("肯德基代金券50元", 2, 3500, "爆品", 0, 45678, 98.50),
    ("瑞幸咖啡折扣券", 2, 2000, "新品", 0, 18923, 97.00),
]


def _seed_products(db, merchant_id: int, categories: list[Category]) -> list[Product]:
    products = []
    for i, (name, cat_idx, base_points, tags, is_self, review_cnt, good_rate) in enumerate(PRODUCT_DATA):
        cover = PLACEHOLDER_IMAGES[i % len(PLACEHOLDER_IMAGES)]
        product = Product(
            merchant_id=merchant_id,
            category_id=categories[cat_idx].id,
            name=name,
            description=f"{name} - 高品质商品，放心兑换。",
            cover_image=cover,
            min_points=base_points,
            cash_supplement=0,
            tags=tags,
            brand="甄选" if is_self else "官方",
            status="on_sale",
            total_sales=review_cnt // 3,
            review_count=review_cnt,
            good_review_rate=good_rate,
            is_self_operated=is_self,
            created_at=now(), updated_at=now(),
        )
        db.add(product)
        db.flush()

        # SKU（每个商品创建1-2个规格）
        skus_data = [
            (f"标准装", base_points),
            (f"大容量装", int(base_points * 1.5)) if i % 3 == 0 else None,
        ]
        for sku_data in skus_data:
            if not sku_data:
                continue
            sku_name, sku_points = sku_data
            sku = ProductSku(
                product_id=product.id,
                sku_name=sku_name,
                points_price=sku_points,
                cash_supplement=0,
                created_at=now(), updated_at=now(),
            )
            db.add(sku)
            db.flush()

            # 库存
            inv = Inventory(
                sku_id=sku.id,
                product_id=product.id,
                quantity=100 + i * 10,
                locked_quantity=0,
                low_stock_alert=10,
                created_at=now(), updated_at=now(),
            )
            db.add(inv)

        # 额外图片
        img = ProductImage(
            product_id=product.id,
            image_url=PLACEHOLDER_IMAGES[(i + 1) % len(PLACEHOLDER_IMAGES)],
            image_type="gallery",
            sort_order=0,
            created_at=now(),
        )
        db.add(img)

        products.append(product)

    db.flush()
    print(f"✅ 商品创建：{len(products)} 个（含SKU和库存）")
    return products


def _seed_activity(db, admin_id: int, products: list[Product]):
    activity = Activity(
        title="新春好物节 · 限时8折",
        description="精选生活好物，限时8折兑换，先到先得！",
        type="discount",
        banner_url=PLACEHOLDER_IMAGES[0],
        discount_rate=0.80,
        quota=None,
        start_at=now() - timedelta(days=1),
        end_at=now() + timedelta(days=15),
        status="active",
        created_by=admin_id,
        created_at=now(), updated_at=now(),
    )
    db.add(activity)
    db.flush()

    # 前5个商品加入活动
    for product in products[:5]:
        ap = ActivityProduct(
            activity_id=activity.id,
            product_id=product.id,
            apply_status="approved",
            created_at=now(),
        )
        db.add(ap)

    db.flush()
    print("✅ 活动创建：新春好物节（进行中，5个商品参与）")


def _seed_announcements(db, admin_id: int):
    announcements_data = [
        ('关于中国移动积分更名为"AI豆"的公告', '尊敬的用户，……（Demo公告内容）', 1),
        ('商城积分兑换规则更新说明', '本次更新主要涉及……（Demo公告内容）', 0),
        ('实物类商品配送时效提升公告', '为提升用户体验……（Demo公告内容）', 0),
    ]
    for title, content, is_pinned in announcements_data:
        ann = Announcement(
            title=title,
            content=content,
            is_pinned=is_pinned,
            published_at=now(),
            created_by=admin_id,
            created_at=now(), updated_at=now(),
        )
        db.add(ann)
    db.flush()
    print("✅ 公告创建：3 条")


if __name__ == "__main__":
    seed()
