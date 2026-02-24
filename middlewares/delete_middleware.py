"""
Middleware Auto-Delete — menghapus pesan user secara realtime
setelah handler selesai memproses (tanpa delay).
Pesan penting tidak akan dihapus.
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from utils.auto_delete import safe_delete


class AutoDeleteMiddleware(BaseMiddleware):
    """
    Middleware yang otomatis menghapus pesan dari user
    setelah bot selesai memprosesnya.
    Ini menjaga chat tetap bersih.
    """

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        # Jalankan handler terlebih dahulu
        result = await handler(event, data)

        # Setelah handler selesai, hapus pesan user (realtime)
        if isinstance(event, Message) and event.from_user and not event.from_user.is_bot:
            await safe_delete(event.bot, event.chat.id, event.message_id)

        return result
