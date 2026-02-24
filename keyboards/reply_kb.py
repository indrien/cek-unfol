"""
ReplyKeyboardMarkup — Keyboard kustom di bawah chat
Terpusat di sini agar tidak ada code dobel di handler.
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.i18n import get_text


def main_menu_kb(lang: str = "id", is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Keyboard menu utama — muncul setelah /start."""
    buttons = [
        [KeyboardButton(text=get_text("menu_cek", lang))],
        [
            KeyboardButton(text=get_text("menu_stats", lang)),
            KeyboardButton(text=get_text("menu_history", lang)),
        ],
        [
            KeyboardButton(text=get_text("menu_settings", lang)),
            KeyboardButton(text=get_text("menu_info", lang)),
        ],
    ]
    # Tombol admin hanya muncul untuk admin
    if is_admin:
        buttons.append([KeyboardButton(text=get_text("menu_admin", lang))])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def back_kb(lang: str = "id") -> ReplyKeyboardMarkup:
    """Keyboard tombol 🔙 Kembali saja."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=get_text("kembali", lang))]],
        resize_keyboard=True,
    )
