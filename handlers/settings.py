"""
Handler Pengaturan — ubah bahasa (Indonesia / English)
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from config import ADMIN_IDS
from database.mongodb import get_user_lang, set_user_lang, save_user
from keyboards.inline_kb import bahasa_kb
from keyboards.reply_kb import main_menu_kb
from utils.auto_delete import safe_delete, mark_important
from utils.helpers import MenuFilter
from utils.i18n import get_text

router = Router()


@router.message(MenuFilter("menu_settings"))
async def menu_settings(message: Message) -> None:
    """Tampilkan pengaturan — pilih bahasa."""
    lang = await get_user_lang(message.from_user.id)

    sent = await message.answer(
        get_text("pengaturan", lang),
        reply_markup=bahasa_kb(),
        parse_mode="HTML",
    )
    mark_important(message.chat.id, sent.message_id)


# ── Callback: ganti bahasa ──

@router.callback_query(F.data.startswith("lang_"))
async def cb_change_lang(callback: CallbackQuery) -> None:
    """Proses perubahan bahasa dari InlineKeyboard."""
    user_id = callback.from_user.id
    new_lang = callback.data.replace("lang_", "")  # "id" atau "en"

    await callback.answer()

    # Simpan bahasa baru ke database
    await set_user_lang(user_id, new_lang)
    await save_user(
        user_id,
        callback.from_user.username or "",
        new_lang,
    )

    # Hapus pesan pengaturan lama
    await safe_delete(
        callback.bot,
        callback.message.chat.id,
        callback.message.message_id,
    )

    # Kirim konfirmasi
    sent = await callback.message.answer(
        get_text("bahasa_diubah", new_lang),
        parse_mode="HTML",
    )
    mark_important(callback.message.chat.id, sent.message_id)

    # Kirim ulang menu utama dengan bahasa baru
    is_admin = user_id in ADMIN_IDS
    sent_menu = await callback.message.answer(
        get_text("welcome", new_lang),
        reply_markup=main_menu_kb(new_lang, is_admin),
        parse_mode="HTML",
    )
    mark_important(callback.message.chat.id, sent_menu.message_id)
