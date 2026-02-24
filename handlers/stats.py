"""
Handler Statistik — menampilkan statistik pengecekan terakhir user
"""

from aiogram import Router
from aiogram.types import Message

from database.mongodb import get_user_lang, get_last_check
from utils.auto_delete import mark_important
from utils.helpers import MenuFilter, calculate_ratio
from utils.i18n import get_text

router = Router()


@router.message(MenuFilter("menu_stats"))
async def menu_stats(message: Message) -> None:
    """Tampilkan statistik pengecekan terakhir."""
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    # Ambil pengecekan terakhir dari database
    last = await get_last_check(user_id)

    if not last:
        sent = await message.answer(
            get_text("stats_kosong", lang),
            parse_mode="HTML",
        )
        mark_important(message.chat.id, sent.message_id)
        return

    # Hitung rasio followers/following
    ratio = calculate_ratio(
        last.get("followers_count", 0),
        last.get("following_count", 0),
    )

    sent = await message.answer(
        get_text(
            "stats_title",
            lang,
            username=last.get("ig_username", "-"),
            following=last.get("following_count", 0),
            followers=last.get("followers_count", 0),
            ratio=ratio,
            unfollowers=last.get("unfollowers_count", 0),
        ),
        parse_mode="HTML",
    )
    # Pesan statistik penting — tidak dihapus
    mark_important(message.chat.id, sent.message_id)
