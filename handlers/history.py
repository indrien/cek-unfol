"""
Handler History — menampilkan riwayat pengecekan unfollowers user
"""

from aiogram import Router
from aiogram.types import Message

from database.mongodb import get_user_lang, get_history
from utils.auto_delete import mark_important
from utils.helpers import MenuFilter
from utils.i18n import get_text

router = Router()


@router.message(MenuFilter("menu_history"))
async def menu_history(message: Message) -> None:
    """Tampilkan 10 riwayat pengecekan terakhir."""
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    # Ambil riwayat dari database
    records = await get_history(user_id, limit=10)

    if not records:
        sent = await message.answer(
            get_text("history_kosong", lang),
            parse_mode="HTML",
        )
        mark_important(message.chat.id, sent.message_id)
        return

    # Susun teks riwayat
    text = get_text("history_title", lang)
    for i, rec in enumerate(records, 1):
        # Format tanggal
        checked_at = rec.get("checked_at")
        date_str = checked_at.strftime("%d/%m/%Y %H:%M") if checked_at else "-"

        # Terjemahkan metode
        method_raw = rec.get("method", "auto")
        method_label = "⚡ Auto" if method_raw == "auto" else "📁 Manual"

        text += get_text(
            "history_item",
            lang,
            no=i,
            username=rec.get("ig_username", "-"),
            method=method_label,
            unfollowers_count=rec.get("unfollowers_count", 0),
            date=date_str,
        )

    sent = await message.answer(text, parse_mode="HTML")
    # Pesan history penting — tidak dihapus
    mark_important(message.chat.id, sent.message_id)
