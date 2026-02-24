"""
Handler /start — Entry point & navigasi menu utama
Menangani command /start dan tombol 🔙 Kembali
"""

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import ADMIN_IDS
from database.mongodb import save_user, get_user_lang
from keyboards.reply_kb import main_menu_kb
from utils.auto_delete import safe_delete, mark_important
from utils.helpers import MenuFilter
from utils.i18n import get_text

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Command /start — tampilkan welcome & menu utama."""
    # Reset state FSM jika ada
    await state.clear()

    user_id = message.from_user.id
    username = message.from_user.username or ""
    lang = await get_user_lang(user_id)

    # Simpan/update data user di database
    await save_user(user_id, username, lang)

    is_admin = user_id in ADMIN_IDS

    # Kirim pesan welcome (ditandai penting — tidak auto-delete)
    sent = await message.answer(
        get_text("welcome", lang),
        reply_markup=main_menu_kb(lang, is_admin),
        parse_mode="HTML",
    )
    mark_important(message.chat.id, sent.message_id)


@router.message(MenuFilter("kembali"))
async def btn_kembali(message: Message, state: FSMContext) -> None:
    """Tombol 🔙 Kembali — kembali ke menu utama."""
    # Reset state FSM
    await state.clear()

    user_id = message.from_user.id
    lang = await get_user_lang(user_id)
    is_admin = user_id in ADMIN_IDS

    # Kirim menu utama (ditandai penting)
    sent = await message.answer(
        get_text("welcome", lang),
        reply_markup=main_menu_kb(lang, is_admin),
        parse_mode="HTML",
    )
    mark_important(message.chat.id, sent.message_id)
