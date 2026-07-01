from decimal import Decimal

import pytest

from app.application.services.admin_phone import AdminPhoneService
from app.application.services.phone_import_export import validate_phone_row


@pytest.mark.asyncio
async def test_add_phone(db_session) -> None:
    service = AdminPhoneService(db_session)
    phone_id = await service.add_phone(
        name="Test Phone X",
        brand_slug="samsung",
        price=Decimal("599"),
        specs={"cpu": "Snapdragon 8", "ram_gb": 12},
    )
    assert phone_id == 1
    assert await service.slug_exists("test-phone-x")


@pytest.mark.asyncio
async def test_duplicate_rejected(db_session) -> None:
    service = AdminPhoneService(db_session)
    await service.add_phone(name="Dup Phone", brand_slug="apple", price=Decimal("999"))
    with pytest.raises(ValueError, match="already exists"):
        await service.add_phone(name="Dup Phone", brand_slug="apple", price=Decimal("999"))


@pytest.mark.asyncio
async def test_update_price(db_session) -> None:
    service = AdminPhoneService(db_session)
    phone_id = await service.add_phone(name="Price Test", brand_slug="google", price=Decimal("499"))
    name, old, new = await service.update_price(phone_id, Decimal("449"))
    assert name == "Price Test"
    assert old == Decimal("499")
    assert new == Decimal("449")


@pytest.mark.asyncio
async def test_import_rows(db_session) -> None:
    service = AdminPhoneService(db_session)
    row = validate_phone_row({"name": "Import Phone", "brand": "xiaomi", "price": "299"})
    stats = await service.import_rows([row])
    assert stats.imported == 1

    stats2 = await service.import_rows([row])
    assert stats2.duplicates == 1
