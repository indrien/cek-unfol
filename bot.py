"""
Bot Telegram — Cek Unfollowers Instagram
Entry point utama. Jalankan dengan: python bot.py

Fitur:
- Cek unfollowers via username (Instagrapi) atau upload file ZIP/JSON
- Statistik akun & riwayat pengecekan
- Multi-bahasa (Indonesia & English)
- Auto-delete pesan realtime
- Panel admin & broadcast
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import register_all_routers
from middlewares.delete_middleware import AutoDeleteMiddleware

# ── Logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Inisialisasi dan jalankan bot."""

    # Validasi token
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN belum diisi! Cek file .env")
        return

    # Buat instance Bot & Dispatcher
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Daftarkan middleware auto-delete (berlaku global untuk semua pesan)
    dp.message.middleware(AutoDeleteMiddleware())

    # Daftarkan semua router handler
    main_router = register_all_routers()
    dp.include_router(main_router)

    # Info startup
    bot_info = await bot.get_me()
    logger.info("Bot @%s berhasil dijalankan!", bot_info.username)

    # Mulai polling (skip update lama)
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
