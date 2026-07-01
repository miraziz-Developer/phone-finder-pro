"""Seed database with brands, categories, and sample phones."""

import asyncio
from decimal import Decimal

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database.session import get_session_manager
from app.core.logging import setup_logging, get_logger
from app.infrastructure.postgres.models import (
    BrandModel,
    CategoryModel,
    PhoneFeatureModel,
    PhoneImageModel,
    PhoneModel,
)

logger = get_logger(__name__)

BRANDS = [
    {"name": "Apple", "slug": "apple"},
    {"name": "Samsung", "slug": "samsung"},
    {"name": "Xiaomi", "slug": "xiaomi"},
    {"name": "Google", "slug": "google"},
    {"name": "Nothing", "slug": "nothing"},
]

CATEGORIES = [
    {"name": "Flagship", "slug": "flagship", "description": "Premium top-tier devices"},
    {"name": "Mid-Range", "slug": "mid-range", "description": "Balanced performance and value"},
    {"name": "Budget", "slug": "budget", "description": "Affordable everyday phones"},
]

PHONES = [
    {
        "brand": "apple",
        "category": "flagship",
        "name": "iPhone 16 Pro",
        "slug": "iphone-16-pro",
        "model_year": 2025,
        "price": Decimal("999"),
        "cpu": "Apple A18 Pro",
        "gpu": "6-core GPU",
        "ram_gb": 8,
        "storage_gb": 256,
        "battery_mah": 3582,
        "camera_main_mp": 48.0,
        "camera_ultra_mp": 48.0,
        "camera_tele_mp": 12.0,
        "camera_front_mp": 12.0,
        "performance_score": 95.0,
        "camera_score": 92.0,
        "battery_score": 78.0,
        "display_score": 94.0,
        "advantages": ["Excellent ecosystem", "Top-tier video", "Long software support"],
        "disadvantages": ["Premium pricing", "No USB-C fast charge rival", "Limited customization"],
        "features": {
            "has_5g": True, "has_nfc": True, "has_wireless_charging": True,
            "has_esim": True, "has_amoled": True, "has_high_refresh": True,
            "refresh_rate_hz": 120, "display_size_inches": 6.3,
            "display_resolution": "2556x1179", "ip_rating": "IP68", "os_version": "iOS 18",
        },
        "image": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-16-pro-finishselect-202409-6-3inch-naturaltitanium?wid=512&hei=512&fmt=png-alpha",
    },
    {
        "brand": "samsung",
        "category": "flagship",
        "name": "Samsung Galaxy S25 Ultra",
        "slug": "galaxy-s25-ultra",
        "model_year": 2025,
        "price": Decimal("1299"),
        "cpu": "Snapdragon 8 Elite",
        "gpu": "Adreno 830",
        "ram_gb": 12,
        "storage_gb": 256,
        "battery_mah": 5000,
        "camera_main_mp": 200.0,
        "camera_ultra_mp": 50.0,
        "camera_tele_mp": 50.0,
        "camera_front_mp": 12.0,
        "performance_score": 96.0,
        "camera_score": 96.0,
        "battery_score": 88.0,
        "display_score": 97.0,
        "advantages": ["S Pen support", "Versatile camera", "Bright AMOLED display"],
        "disadvantages": ["Very expensive", "Large and heavy", "Bloatware"],
        "features": {
            "has_5g": True, "has_nfc": True, "has_wireless_charging": True,
            "has_esim": True, "has_amoled": True, "has_high_refresh": True,
            "refresh_rate_hz": 120, "display_size_inches": 6.9,
            "display_resolution": "3120x1440", "ip_rating": "IP68", "os_version": "Android 15",
        },
        "image": "https://images.samsung.com/is/image/samsung/assets/global/galaxy-s25-ultra/images/galaxy-s25-ultra-share-image.jpg",
    },
    {
        "brand": "google",
        "category": "flagship",
        "name": "Google Pixel 9 Pro",
        "slug": "pixel-9-pro",
        "model_year": 2025,
        "price": Decimal("899"),
        "cpu": "Google Tensor G4",
        "gpu": "Mali-G715",
        "ram_gb": 12,
        "storage_gb": 128,
        "battery_mah": 4700,
        "camera_main_mp": 50.0,
        "camera_ultra_mp": 48.0,
        "camera_tele_mp": 48.0,
        "camera_front_mp": 42.0,
        "performance_score": 82.0,
        "camera_score": 95.0,
        "battery_score": 80.0,
        "display_score": 90.0,
        "advantages": ["Best computational photography", "Clean Android", "7 years updates"],
        "disadvantages": ["Tensor chip thermals", "Average gaming", "Slow wired charging"],
        "features": {
            "has_5g": True, "has_nfc": True, "has_wireless_charging": True,
            "has_esim": True, "has_amoled": True, "has_high_refresh": True,
            "refresh_rate_hz": 120, "display_size_inches": 6.3,
            "display_resolution": "2856x1280", "ip_rating": "IP68", "os_version": "Android 15",
        },
        "image": "https://storage.googleapis.com/gweb-uniblog-publish-prod/images/Pixel_9_Pro_1000.width-500.png",
    },
    {
        "brand": "xiaomi",
        "category": "mid-range",
        "name": "Xiaomi 14T Pro",
        "slug": "xiaomi-14t-pro",
        "model_year": 2025,
        "price": Decimal("649"),
        "cpu": "MediaTek Dimensity 9300+",
        "gpu": "Mali-G720",
        "ram_gb": 12,
        "storage_gb": 256,
        "battery_mah": 5000,
        "camera_main_mp": 50.0,
        "camera_ultra_mp": 50.0,
        "camera_tele_mp": None,
        "camera_front_mp": 32.0,
        "performance_score": 88.0,
        "camera_score": 85.0,
        "battery_score": 90.0,
        "display_score": 88.0,
        "advantages": ["Great value", "Fast charging 120W", "Solid performance"],
        "disadvantages": ["MIUI ads", "Average low-light", "No telephoto"],
        "features": {
            "has_5g": True, "has_nfc": True, "has_wireless_charging": False,
            "has_esim": False, "has_amoled": True, "has_high_refresh": True,
            "refresh_rate_hz": 144, "display_size_inches": 6.67,
            "display_resolution": "2712x1220", "ip_rating": "IP54", "os_version": "Android 14",
        },
        "image": "https://i01.appmifile.com/webfile/globalimg/products/pc/xiaomi-14t-pro/specs-header.png",
    },
    {
        "brand": "nothing",
        "category": "mid-range",
        "name": "Nothing Phone (3)",
        "slug": "nothing-phone-3",
        "model_year": 2025,
        "price": Decimal("599"),
        "cpu": "Snapdragon 8s Gen 3",
        "gpu": "Adreno 735",
        "ram_gb": 12,
        "storage_gb": 256,
        "battery_mah": 5000,
        "camera_main_mp": 50.0,
        "camera_ultra_mp": 50.0,
        "camera_tele_mp": None,
        "camera_front_mp": 32.0,
        "performance_score": 84.0,
        "camera_score": 80.0,
        "battery_score": 85.0,
        "display_score": 86.0,
        "advantages": ["Unique design", "Clean Nothing OS", "Good battery life"],
        "disadvantages": ["No wireless charging", "Average camera", "Limited availability"],
        "features": {
            "has_5g": True, "has_nfc": True, "has_wireless_charging": False,
            "has_esim": True, "has_amoled": True, "has_high_refresh": True,
            "refresh_rate_hz": 120, "display_size_inches": 6.7,
            "display_resolution": "2412x1080", "ip_rating": "IP54", "os_version": "Android 15",
        },
        "image": "https://nothing.tech/cdn/shop/files/phone-3-black-front.png",
    },
    {
        "brand": "samsung",
        "category": "mid-range",
        "name": "Samsung Galaxy A55",
        "slug": "galaxy-a55",
        "model_year": 2024,
        "price": Decimal("449"),
        "cpu": "Exynos 1480",
        "gpu": "Xclipse 530",
        "ram_gb": 8,
        "storage_gb": 128,
        "battery_mah": 5000,
        "camera_main_mp": 50.0,
        "camera_ultra_mp": 12.0,
        "camera_tele_mp": None,
        "camera_front_mp": 32.0,
        "performance_score": 72.0,
        "camera_score": 75.0,
        "battery_score": 88.0,
        "display_score": 82.0,
        "advantages": ["Great battery", "IP67 rating", "Samsung ecosystem"],
        "disadvantages": ["Mid-range performance", "Slow charging", "No telephoto"],
        "features": {
            "has_5g": True, "has_nfc": True, "has_wireless_charging": False,
            "has_esim": False, "has_amoled": True, "has_high_refresh": True,
            "refresh_rate_hz": 120, "display_size_inches": 6.6,
            "display_resolution": "2340x1080", "ip_rating": "IP67", "os_version": "Android 14",
        },
        "image": "https://images.samsung.com/is/image/samsung/assets/uk/smartphones/galaxy-a55/images/galaxy-a55-share-image.jpg",
    },
    {
        "brand": "xiaomi",
        "category": "budget",
        "name": "Redmi Note 14 Pro",
        "slug": "redmi-note-14-pro",
        "model_year": 2025,
        "price": Decimal("299"),
        "cpu": "MediaTek Dimensity 7300",
        "gpu": "Mali-G615",
        "ram_gb": 8,
        "storage_gb": 256,
        "battery_mah": 5110,
        "camera_main_mp": 200.0,
        "camera_ultra_mp": 8.0,
        "camera_tele_mp": None,
        "camera_front_mp": 20.0,
        "performance_score": 68.0,
        "camera_score": 72.0,
        "battery_score": 92.0,
        "display_score": 78.0,
        "advantages": ["Incredible value", "Huge battery", "200MP camera"],
        "disadvantages": ["Plastic build", "Ads in UI", "Average processor"],
        "features": {
            "has_5g": True, "has_nfc": True, "has_wireless_charging": False,
            "has_esim": False, "has_amoled": True, "has_high_refresh": True,
            "refresh_rate_hz": 120, "display_size_inches": 6.67,
            "display_resolution": "2712x1220", "ip_rating": "IP54", "os_version": "Android 14",
        },
        "image": "https://i01.appmifile.com/webfile/globalimg/products/pc/redmi-note-14-pro/specs-header.png",
    },
    {
        "brand": "google",
        "category": "budget",
        "name": "Google Pixel 8a",
        "slug": "pixel-8a",
        "model_year": 2024,
        "price": Decimal("499"),
        "cpu": "Google Tensor G3",
        "gpu": "Mali-G715",
        "ram_gb": 8,
        "storage_gb": 128,
        "battery_mah": 4492,
        "camera_main_mp": 64.0,
        "camera_ultra_mp": 13.0,
        "camera_tele_mp": None,
        "camera_front_mp": 13.0,
        "performance_score": 75.0,
        "camera_score": 88.0,
        "battery_score": 76.0,
        "display_score": 80.0,
        "advantages": ["Flagship camera at mid price", "Clean Android", "Long updates"],
        "disadvantages": ["Average battery", "60Hz display", "Slow charging"],
        "features": {
            "has_5g": True, "has_nfc": True, "has_wireless_charging": True,
            "has_esim": True, "has_amoled": True, "has_high_refresh": False,
            "refresh_rate_hz": 60, "display_size_inches": 6.1,
            "display_resolution": "2400x1080", "ip_rating": "IP67", "os_version": "Android 14",
        },
        "image": "https://storage.googleapis.com/gweb-uniblog-publish-prod/images/Pixel_8a_1000.width-500.png",
    },
]


async def seed() -> None:
    """Seed the database with initial catalog data."""
    setup_logging()
    settings = get_settings()
    manager = get_session_manager()
    manager.init()

    async with manager.session_factory() as session:
        existing = await session.execute(select(BrandModel).limit(1))
        if existing.scalar_one_or_none():
            logger.info("seed_skipped", reason="data_already_exists")
            return

        brand_map: dict[str, int] = {}
        for b in BRANDS:
            model = BrandModel(name=b["name"], slug=b["slug"], is_active=True)
            session.add(model)
            await session.flush()
            brand_map[b["slug"]] = model.id

        category_map: dict[str, int] = {}
        for c in CATEGORIES:
            model = CategoryModel(name=c["name"], slug=c["slug"], description=c["description"])
            session.add(model)
            await session.flush()
            category_map[c["slug"]] = model.id

        for p in PHONES:
            phone = PhoneModel(
                brand_id=brand_map[p["brand"]],
                category_id=category_map[p["category"]],
                name=p["name"],
                slug=p["slug"],
                model_year=p["model_year"],
                price=p["price"],
                currency="USD",
                cpu=p["cpu"],
                gpu=p.get("gpu"),
                ram_gb=p["ram_gb"],
                storage_gb=p["storage_gb"],
                battery_mah=p["battery_mah"],
                camera_main_mp=p["camera_main_mp"],
                camera_ultra_mp=p.get("camera_ultra_mp"),
                camera_tele_mp=p.get("camera_tele_mp"),
                camera_front_mp=p["camera_front_mp"],
                performance_score=p["performance_score"],
                camera_score=p["camera_score"],
                battery_score=p["battery_score"],
                display_score=p["display_score"],
                advantages=p["advantages"],
                disadvantages=p["disadvantages"],
                is_active=True,
                view_count=0,
                recommendation_count=0,
            )
            session.add(phone)
            await session.flush()

            feat = p["features"]
            session.add(
                PhoneFeatureModel(
                    phone_id=phone.id,
                    has_5g=feat["has_5g"],
                    has_nfc=feat["has_nfc"],
                    has_wireless_charging=feat["has_wireless_charging"],
                    has_esim=feat["has_esim"],
                    has_amoled=feat["has_amoled"],
                    has_high_refresh=feat["has_high_refresh"],
                    refresh_rate_hz=feat["refresh_rate_hz"],
                    display_size_inches=feat["display_size_inches"],
                    display_resolution=feat["display_resolution"],
                    ip_rating=feat.get("ip_rating"),
                    os_version=feat.get("os_version"),
                )
            )
            session.add(
                PhoneImageModel(
                    phone_id=phone.id,
                    url=p["image"],
                    is_primary=True,
                    sort_order=0,
                )
            )

        await session.commit()
        logger.info("seed_completed", brands=len(BRANDS), categories=len(CATEGORIES), phones=len(PHONES))

    await manager.close()


if __name__ == "__main__":
    asyncio.run(seed())
