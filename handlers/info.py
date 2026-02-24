"""
Handler Info — menampilkan informasi & bantuan penggunaan bot
"""

from aiogram import Router
from aiogram.types import Message

from database.mongodb import get_user_lang
from utils.auto_delete import mark_important
from utils.helpers import MenuFilter
from utils.i18n import get_text

router = Router()


@router.message(MenuFilter("menu_info"))
async def menu_info(message: Message) -> None:
    """Tampilkan halaman info & bantuan."""
    lang = await get_user_lang(message.from_user.id)

    sent = await message.answer(
        get_text("info", lang),
        parse_mode="HTML",
    )
    # Pesan info penting — tidak dihapus
    mark_important(message.chat.id, sent.message_id)
