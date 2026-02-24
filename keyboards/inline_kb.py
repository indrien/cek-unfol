"""
InlineKeyboardMarkup — Keyboard menempel di pesan
Terpusat di sini agar tidak ada code dobel di handler.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.i18n import get_text


def metode_cek_kb(lang: str = "id") -> InlineKeyboardMarkup:
    """Pilih metode pengecekan: Auto / Manual."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("metode_auto", lang),
                    callback_data="cek_auto",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_text("metode_manual", lang),
                    callback_data="cek_manual",
                ),
            ],
        ]
    )


def bahasa_kb() -> InlineKeyboardMarkup:
    """Pilih bahasa: Indonesia / English."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇮🇩 Indonesia", callback_data="lang_id"
                ),
                InlineKeyboardButton(
                    text="🇬🇧 English", callback_data="lang_en"
                ),
            ],
        ]
    )


def back_inline_kb(lang: str = "id") -> InlineKeyboardMarkup:
    """Tombol kembali inline."""
    label = "🔙 Kembali" if lang == "id" else "🔙 Back"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, callback_data="back_menu")],
        ]
    )
