from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.services.abtest import create_ab_test, get_ab_test, select_variant
from bot.services.storage import get_user
from bot.services.publisher import publish_text

router = Router()

def _kb_choices(ab_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Выбрать A", callback_data=f"choose:A:{ab_id}"),
         InlineKeyboardButton(text="✅ Выбрать B", callback_data=f"choose:B:{ab_id}")],
        [InlineKeyboardButton(text="🚀 Опубликовать A", callback_data=f"pub:A:{ab_id}"),
         InlineKeyboardButton(text="🚀 Опубликовать B", callback_data=f"pub:B:{ab_id}")]
    ])

@router.message(Command("generate"))
async def generate_cmd(msg: types.Message, command: CommandObject):
    topic = (command.args or "").strip()
    if not topic:
        await msg.answer(
            "Использование:\n"
            "<code>/generate тема/идея поста</code>\n\n"
            "Пример: <code>/generate распаковка набора кистей для макияжа</code>"
        )
        return

    ab_id = create_ab_test(msg.from_user.id, topic)
    ab = get_ab_test(msg.from_user.id, ab_id)
    A = ab["variants"]["A"]["text"]
    B = ab["variants"]["B"]["text"]

    await msg.answer(
        f"<b>A</b> (pred≈{ab['variants']['A']['pred']:.2f}):\n{A}",
        reply_markup=_kb_choices(ab_id)
    )
    await msg.answer(
        f"<b>B</b> (pred≈{ab['variants']['B']['pred']:.2f}):\n{B}"
    )

@router.callback_query(F.data.startswith("choose:"))
async def on_choose(call: types.CallbackQuery):
    _, variant, ab_id = call.data.split(":")
    select_variant(call.from_user.id, ab_id, variant)
    await call.message.answer(f"Выбран вариант <b>{variant}</b> для A/B #{ab_id}. Можно жать «Опубликовать {variant}».")
    await call.answer("Выбрано!")

@router.callback_query(F.data.startswith("pub:"))
async def on_publish(call: types.CallbackQuery):
    _, variant, ab_id = call.data.split(":")
    ab = get_ab_test(call.from_user.id, ab_id)
    if not ab:
        await call.answer("Черновик не найден", show_alert=True)
        return
    text = ab["variants"][variant]["text"]
    ok, info = publish_text(call.from_user.id, text)
    if ok:
        await call.message.answer(f"🚀 Опубликовал вариант {variant} через n8n. {info}")
    else:
        # Если n8n не подключён — хотя бы вернём текст пользователю
        await call.message.answer(f"⚠️ {info}\n\nТекст варианта {variant}:\n{text}")
    await call.answer("Готово")
