import json
from decimal import Decimal

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message

from app.application.services.admin_phone import AdminPhoneService
from app.application.services.analytics import AnalyticsService
from app.application.services.phone_import_export import PhoneImportExportService
from app.core.database.unit_of_work import UnitOfWork
from app.presentation.bot.filters import IsAdminFilter
from app.presentation.bot.states import AdminStates
from app.presentation.bot.texts import MESSAGE_SEPARATOR
from app.shared.exceptions import ValidationError

router = Router(name="admin")
router.message.filter(IsAdminFilter())


@router.message(Command("admin"))
async def cmd_admin_panel(message: Message) -> None:
    await message.answer(
        "🔐 <b>Admin Panel</b>\n"
        f"{MESSAGE_SEPARATOR}\n"
        "/stats — Dashboard\n"
        "/phones — Catalog list\n"
        "/add_phone — Add phone\n"
        "/delete_phone &lt;id&gt; — Deactivate\n"
        "/update_price — Change USD price\n"
        "/add_image — Attach image URL\n"
        "/import_json /import_csv /import_excel — Import\n"
        "/export_json /export_csv — Export",
        parse_mode="HTML",
    )


@router.message(Command("stats"))
async def cmd_stats(message: Message, uow: UnitOfWork) -> None:
    stats = await AnalyticsService(uow.session).get_dashboard_stats()

    viewed = (
        "\n".join(f"  {i}. {n} ({c})" for i, (_, n, c) in enumerate(stats.most_viewed, 1)) or "  —"
    )
    rec = (
        "\n".join(f"  {i}. {n} ({c}x)" for i, (_, n, c) in enumerate(stats.most_recommended, 1))
        or "  —"
    )
    brands = "\n".join(f"  • {n}: {c}" for n, c in stats.top_brands) or "  —"

    await message.answer(
        "📊 <b>Dashboard</b>\n"
        f"{MESSAGE_SEPARATOR}\n"
        f"👥 Users: <b>{stats.users_total}</b> "
        f"(+{stats.users_today} today, +{stats.users_this_month} month)\n"
        f"📱 Phones: <b>{stats.phones_total}</b>\n"
        f"🎯 Recommendations: <b>{stats.recommendations_total}</b>\n"
        f"📈 Avg match: <b>{stats.avg_recommendation_score:.0%}</b>\n"
        f"{MESSAGE_SEPARATOR}\n"
        f"<b>Most viewed</b>\n{viewed}\n"
        f"<b>Most recommended</b>\n{rec}\n"
        f"<b>Top brands</b>\n{brands}",
        parse_mode="HTML",
    )


@router.message(Command("phones"))
async def cmd_list_phones(message: Message, uow: UnitOfWork) -> None:
    phones = await uow.phones.get_all_active()
    if not phones:
        await message.answer("Catalog is empty.")
        return

    lines = ["📱 <b>Catalog</b>", MESSAGE_SEPARATOR]
    for i, phone in enumerate(phones[:20], 1):
        tag = f" (-{phone.discount_percent:.0f}%)" if phone.discount_percent else ""
        lines.append(f"{i}. <b>{phone.name}</b> — ${phone.price:,.0f}{tag} [{phone.id}]")

    if len(phones) > 20:
        lines.append(f"\n<i>+{len(phones) - 20} more</i>")

    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("add_phone"))
async def cmd_add_phone_start(message: Message, state: FSMContext) -> None:
    await state.set_state(AdminStates.add_name)
    await message.answer(
        "➕ <b>Add phone</b> (1/4)\nEnter model name:",
        parse_mode="HTML",
    )


@router.message(AdminStates.add_name)
async def admin_add_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(AdminStates.add_brand)
    await message.answer("2/4 — Brand slug (apple, samsung, xiaomi...):")


@router.message(AdminStates.add_brand)
async def admin_add_brand(message: Message, state: FSMContext) -> None:
    await state.update_data(brand=(message.text or "").lower().strip())
    await state.set_state(AdminStates.add_price)
    await message.answer("3/4 — Price in USD:")


@router.message(AdminStates.add_price)
async def admin_add_price(message: Message, state: FSMContext) -> None:
    await state.update_data(price=(message.text or "").replace("$", "").strip())
    await state.set_state(AdminStates.add_specs)
    await message.answer(
        "4/4 — Specs JSON or <code>default</code>\n"
        '<code>{"cpu":"Snapdragon 8","ram_gb":12,"storage_gb":256}</code>',
        parse_mode="HTML",
    )


@router.message(AdminStates.add_specs)
async def admin_add_specs(message: Message, state: FSMContext, uow: UnitOfWork) -> None:
    data = await state.get_data()
    specs: dict = {}

    if message.text and message.text.strip().lower() != "default":
        try:
            specs = json.loads(message.text)
        except json.JSONDecodeError:
            await message.answer("Invalid JSON.")
            return

    service = AdminPhoneService(uow.session)
    try:
        phone_id = await service.add_phone(
            name=data["name"],
            brand_slug=data["brand"],
            price=Decimal(data["price"]),
            specs=specs,
        )
    except ValueError as exc:
        await message.answer(f"⚠️ {exc}")
        await state.clear()
        return

    await state.clear()
    await message.answer(
        f"✅ <b>{data['name']}</b> added — ${Decimal(data['price']):,.0f} (ID {phone_id})",
        parse_mode="HTML",
    )


@router.message(Command("delete_phone"))
async def cmd_delete_phone(message: Message, uow: UnitOfWork) -> None:
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.answer("Usage: <code>/delete_phone 5</code>", parse_mode="HTML")
        return
    phone_id = int(parts[1])
    await uow.phones.delete(phone_id)
    await message.answer(f"Phone {phone_id} deactivated.")


@router.message(Command("update_price"))
async def cmd_update_price(message: Message, state: FSMContext) -> None:
    await state.set_state(AdminStates.update_price)
    await message.answer("Format: <code>phone_id price</code>", parse_mode="HTML")


@router.message(AdminStates.update_price)
async def admin_update_price(message: Message, state: FSMContext, uow: UnitOfWork) -> None:
    parts = (message.text or "").split()
    if len(parts) != 2:
        await message.answer("Use: <code>3 749</code>", parse_mode="HTML")
        return

    service = AdminPhoneService(uow.session)
    try:
        name, old, new = await service.update_price(
            int(parts[0]), Decimal(parts[1].replace("$", ""))
        )
    except ValueError:
        await message.answer("Phone not found.")
        await state.clear()
        return

    await state.clear()
    await message.answer(
        f"💲 <b>{name}</b>: ${old:,.0f} → ${new:,.0f}",
        parse_mode="HTML",
    )


@router.message(Command("add_image"))
async def cmd_add_image(message: Message, state: FSMContext) -> None:
    await state.set_state(AdminStates.add_image)
    await message.answer("Format: <code>phone_id url</code>", parse_mode="HTML")


@router.message(AdminStates.add_image)
async def admin_add_image(message: Message, state: FSMContext, uow: UnitOfWork) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Invalid format.")
        return

    await AdminPhoneService(uow.session).add_image(int(parts[0]), parts[1].strip())
    await state.clear()
    await message.answer("Image saved.")


async def _import_file(message: Message, uow: UnitOfWork, fmt: str) -> None:
    if not message.document:
        await message.answer(f"Attach a .{fmt} file.")
        return

    file = await message.bot.download(message.document)
    if not file:
        await message.answer("Download failed.")
        return

    parser = PhoneImportExportService()
    try:
        content = file.read()
        if fmt == "json":
            rows = parser.parse_json(content)
        elif fmt == "csv":
            rows = parser.parse_csv(content)
        else:
            rows = parser.parse_excel(content)
    except (ValidationError, json.JSONDecodeError, ValueError) as exc:
        await message.answer(f"⚠️ {exc}")
        return

    stats = await AdminPhoneService(uow.session).import_rows(rows)
    await message.answer(
        f"📂 <b>Import done</b>\n"
        f"✅ {stats.imported} · 🔄 {stats.duplicates} dup · ⚠️ {stats.skipped} skipped",
        parse_mode="HTML",
    )


@router.message(Command("import_json"))
async def cmd_import_json(message: Message, uow: UnitOfWork) -> None:
    await _import_file(message, uow, "json")


@router.message(Command("import_csv"))
async def cmd_import_csv(message: Message, uow: UnitOfWork) -> None:
    await _import_file(message, uow, "csv")


@router.message(Command("import_excel"))
async def cmd_import_excel(message: Message, uow: UnitOfWork) -> None:
    await _import_file(message, uow, "xlsx")


@router.message(Command("export_json"))
async def cmd_export_json(message: Message, uow: UnitOfWork) -> None:
    phones = await uow.phones.get_all_active()
    payload = json.dumps(
        [
            {
                "id": p.id,
                "name": p.name,
                "brand": p.brand_name,
                "price_usd": float(p.price),
                "cpu": p.cpu,
                "ram_gb": p.ram_gb,
                "storage_gb": p.storage_gb,
            }
            for p in phones
        ],
        indent=2,
    )
    doc = BufferedInputFile(payload.encode(), filename="phones.json")
    await message.answer_document(doc, caption=f"{len(phones)} phones")


@router.message(Command("export_csv"))
async def cmd_export_csv(message: Message, uow: UnitOfWork) -> None:
    phones = await uow.phones.get_all_active()
    rows = [
        {
            "name": p.name,
            "brand": p.brand_name or "",
            "price": str(p.price),
            "cpu": p.cpu,
            "ram_gb": p.ram_gb,
            "storage_gb": p.storage_gb,
            "battery_mah": p.battery_mah,
        }
        for p in phones
    ]
    doc = BufferedInputFile(
        PhoneImportExportService().export_csv(rows),
        filename="phones.csv",
    )
    await message.answer_document(doc, caption=f"{len(phones)} phones")
