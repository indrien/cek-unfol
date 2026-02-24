"""
Modul auto-delete pesan
Menghapus pesan bot & user secara realtime tanpa delay.
Pesan yang ditandai 'penting' tidak akan dihapus.
"""

import asyncio
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

# ── Penyimpanan pesan penting (tidak boleh dihapus) ──
_important_messages: set[tuple[int, int]] = set()


def mark_important(chat_id: int, message_id: int) -> None:
    """Tandai pesan sebagai penting — tidak akan dihapus otomatis."""
    _important_messages.add((chat_id, message_id))


def is_important(chat_id: int, message_id: int) -> bool:
    """Cek apakah pesan termasuk penting."""
    return (chat_id, message_id) in _important_messages


async def safe_delete(bot: Bot, chat_id: int, message_id: int) -> None:
    """Hapus satu pesan dengan aman (skip jika sudah terhapus)."""
    if is_important(chat_id, message_id):
        return
    try:
        await bot.delete_message(chat_id, message_id)
    except TelegramBadRequest:
        pass  # Pesan sudah terhapus atau tidak bisa dihapus


async def auto_delete_messages(
    bot: Bot, chat_id: int, *message_ids: int
) -> None:
    """Hapus beberapa pesan sekaligus secara paralel."""
    tasks = [safe_delete(bot, chat_id, mid) for mid in message_ids]
    await asyncio.gather(*tasks)
