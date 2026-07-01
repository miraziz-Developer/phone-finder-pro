import os

os.environ.setdefault("BOT_TOKEN", "1234567890:TEST_TOKEN_FOR_PYTEST_ONLY")
os.environ.setdefault("APP_ENV", "development")

from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.domain.entities.phone import Phone, PhoneFeatures
from app.domain.value_objects import BudgetRange, UserPreferencesInput
from app.infrastructure.postgres.models import Base
from app.shared.enums import BrandName, UseCase


@pytest.fixture
def sample_phone() -> Phone:
    phone = Phone(
        id=1,
        brand_id=1,
        category_id=1,
        name="Galaxy S25",
        slug="galaxy-s25",
        model_year=2025,
        price=Decimal("799"),
        currency="USD",
        cpu="Snapdragon 8 Elite",
        gpu="Adreno",
        ram_gb=12,
        storage_gb=256,
        battery_mah=5000,
        camera_main_mp=50.0,
        camera_ultra_mp=12.0,
        camera_tele_mp=10.0,
        camera_front_mp=12.0,
        performance_score=90.0,
        camera_score=88.0,
        battery_score=85.0,
        display_score=92.0,
        advantages=["Fast", "Good camera"],
        disadvantages=["Pricey"],
        brand_name="Samsung",
    )
    phone.features = PhoneFeatures(
        id=1,
        phone_id=1,
        has_5g=True,
        has_nfc=True,
        has_wireless_charging=True,
        has_esim=True,
        has_amoled=True,
        has_high_refresh=True,
        refresh_rate_hz=120,
        display_size_inches=6.7,
        display_resolution="2400x1080",
        ip_rating="IP68",
        os_version="Android 15",
    )
    return phone


@pytest.fixture
def sample_preferences() -> UserPreferencesInput:
    return UserPreferencesInput(
        budget=BudgetRange(min_amount=Decimal("600"), max_amount=Decimal("900")),
        use_case=UseCase.GAMING,
        preferred_brand=BrandName.SAMSUNG,
        min_ram_gb=8,
        min_storage_gb=128,
        requires_5g=True,
        requires_nfc=True,
        requires_wireless_charging=False,
        requires_esim=False,
        requires_amoled=True,
        requires_high_refresh=True,
    )


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session

    await engine.dispose()
