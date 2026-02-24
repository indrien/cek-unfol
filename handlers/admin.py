"""
Handler Admin — panel khusus admin
Menampilkan statistik global & fitur broadcast.
"""

import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from config import ADMIN_IDS
from database.mongodb import (
    get_user_lang,
    get_total_users,
    get_total_checks,
    get_all_user_ids,
)
from utils.auto_delete import mark_important
from utils.helpers import MenuFilter
from utils.i18n import get_text

logger = logging.getLogger(__name__)

router = Router()


# ── FSM untuk broadcast ──
class AdminStates(StatesGroup):
    waiting_broadcast = State()


# ══════════════════════════════════════════════
#  MENU ADMIN — tampilkan panel
# ══════════════════════════════════════════════

@router.message(MenuFilter("menu_admin"))
async def menu_admin(message: Message) -> None:
    """Tampilkan panel admin — hanya untuk admin."""
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    # Cek akses admin
    if user_id not in ADMIN_IDS:
        await message.answer(
            get_text("bukan_admin", lang),
            parse_mode="HTML",
        )
        return

    total_users = await get_total_users()
    total_checks = await get_total_checks()

    sent = await message.answer(
        get_text(
            "admin_panel",
            lang,
            total_users=total_users,
            total_checks=total_checks,
        ),
        parse_mode="HTML",
    )
    mark_important(message.chat.id, sent.message_id)


# ══════════════════════════════════════════════
#  BROADCAST — kirim pesan ke semua user
#  (Fitur tambahan admin, gunakan command /broadcast)
# ══════════════════════════════════════════════

@router.message(F.text == "/broadcast")
async def cmd_broadcast(message: Message, state: FSMContext) -> None:
    """Admin memulai broadcast."""
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    if user_id not in ADMIN_IDS:
        await message.answer(
            get_text("bukan_admin", lang),
            parse_mode="HTML",
        )
        return

    sent = await message.answer(
        get_text("broadcast_kirim", lang),
        parse_mode="HTML",
    )
    mark_important(message.chat.id, sent.message_id)

    await state.set_state(AdminStates.waiting_broadcast)


@router.message(AdminStates.waiting_broadcast, F.text)
async def process_broadcast(message: Message, state: FSMContext) -> None:
    """Proses & kirim broadcast ke semua user."""
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)
    broadcast_text = message.text

    user_ids = await get_all_user_ids()
    success_count = 0

    for uid in user_ids:
        try:
            await message.bot.send_message(uid, broadcast_text)
            success_count += 1
        except Exception:
            logger.warning("Gagal broadcast ke user %s", uid)

    sent = await message.answer(
        get_text("broadcast_selesai", lang, count=success_count),
        parse_mode="HTML",
    )
    mark_important(message.chat.id, sent.message_id)

    await state.clear()
