# bot/handlers/generate.py
from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.services.abtest import (
    create_ab_test, get_ab_test, select_variant,
    set_message_id, mark_published, delete_ab_test
)
from bot.services.publisher import publish_text
from bot.utils.config import Config

router = Router()

def kb_variant(ab_id: str, variant: str, selected: str | None) -> InlineKeyboardMarkup:
    """Клавиатура под конкретным вариантом."""
    if selected == variant:
        choose_btn = InlineKeyboardButton(text="✅ Выбрано", callback_data=f"noop:{variant}:{ab_id}")
    else:
        choose_btn = InlineKeyboardButton(text=f"✅ Выбрать {variant}", callback_data=f"choose:{variant}:{ab_id}")

    return InlineKeyboardMarkup(inline_keyboard=[
        [choose_btn, InlineKeyboardButton(text=f"🚀 Опубликовать {variant}", callback_data=f"pub:{variant}:{ab_id}")],
        [InlineKeyboardButton(text=f"📝 Показать текст {variant}", callback_data=f"show:{variant}:{ab_id}")],
        [InlineKeyboardButton(text="🗑 Удалить черновик", callback_data=f"del:{ab_id}")]
    ])

@router.message(Command("generate"))
async def generate_cmd(msg: types.Message, command: CommandObject):
    topic = (command.args or "").strip()
    if not topic:
        await msg.answer(
            "Использование:\n"
            "<code>/generate тема/идея поста</code>\n\n"
            "Напр.: <code>/generate распаковка набора кистей Ozon до 1500₽</code>"
        )
        return
    if not Config.N8N_WEBHOOK_BASE:
        await msg.answer("ℹ️ Генерация сейчас работает в демо-режиме (шаблоны), так как N8N_WEBHOOK_BASE не задан в .env")

    ab_id = create_ab_test(msg.from_user.id, topic)
    ab = get_ab_test(msg.from_user.id, ab_id)
    A = ab["variants"]["A"]["text"]
    B = ab["variants"]["B"]["text"]

    mA = await msg.answer(
        f"<b>Вариант A</b> (предикт ≈ {ab['variants']['A']['pred']:.2f})\n\n{A}",
        reply_markup=kb_variant(ab_id, "A", selected=None)
    )
    set_message_id(msg.from_user.id, ab_id, "A", mA.message_id)

    mB = await msg.answer(
        f"<b>Вариант B</b> (предикт ≈ {ab['variants']['B']['pred']:.2f})\n\n{B}",
        reply_markup=kb_variant(ab_id, "B", selected=None)
    )
    set_message_id(msg.from_user.id, ab_id, "B", mB.message_id)

    await msg.answer("Выберите лучший вариант: нажмите «✅ Выбрать A/B», затем «🚀 Опубликовать».")

@router.callback_query(F.data.startswith("noop:"))
async def on_noop(call: types.CallbackQuery):
    await call.answer("Этот вариант уже выбран.", show_alert=False)

@router.callback_query(F.data.startswith("choose:"))
async def on_choose(call: types.CallbackQuery):
    _, variant, ab_id = call.data.split(":")
    user_id = call.from_user.id
    select_variant(user_id, ab_id, variant)
    ab = get_ab_test(user_id, ab_id) or {}
    messages = (ab.get("messages") or {})
    sel = ab.get("selected")

    # Обновляем клавиатуры под обоими сообщениями, чтобы отразить выбор
    bot = call.message.bot
    try:
        if messages.get("A"):
            await bot.edit_message_reply_markup(
                chat_id=user_id, message_id=messages["A"],
                reply_markup=kb_variant(ab_id, "A", selected=sel)
            )
        if messages.get("B"):
            await bot.edit_message_reply_markup(
                chat_id=user_id, message_id=messages["B"],
                reply_markup=kb_variant(ab_id, "B", selected=sel)
            )
    except Exception:
        # Если сообщения уже не доступны/изменены — просто игнорируем
        pass

    await call.message.answer(f"Вы выбрали вариант <b>{variant}</b>. Можете сразу нажать «🚀 Опубликовать {variant}» или «📝 Показать текст {variant}».")
    await call.answer("Выбрано!")

@router.callback_query(F.data.startswith("show:"))
async def on_show(call: types.CallbackQuery):
    _, variant, ab_id = call.data.split(":")
    ab = get_ab_test(call.from_user.id, ab_id)
    if not ab:
        await call.answer("Черновик не найден", show_alert=True)
        return
    text = ab["variants"][variant]["text"]
    await call.message.answer(f"Текст варианта {variant}:\n\n{text}")
    await call.answer()

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
        mark_published(call.from_user.id, ab_id, variant)
        await call.message.answer(f"🚀 Опубликовал вариант {variant}. {info}")
    else:
        await call.message.answer(f"⚠️ {info}\n\nТекст варианта {variant}:\n{text}")
    await call.answer("Готово")

@router.callback_query(F.data.startswith("del:"))
async def on_delete(call: types.CallbackQuery):
    _, ab_id = call.data.split(":")
    delete_ab_test(call.from_user.id, ab_id)
    await call.message.answer("Черновик удалён.")
    await call.answer("Удалено")
