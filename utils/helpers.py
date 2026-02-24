"""
Fungsi pembantu umum & custom filter Aiogram
"""

from aiogram.filters import BaseFilter
from aiogram.types import Message
from utils.i18n import TEXTS


# ── Custom filter: cocokkan teks tombol multi-bahasa ──
class MenuFilter(BaseFilter):
    """
    Filter untuk mencocokkan teks tombol menu di semua bahasa.
    Contoh: MenuFilter("menu_cek") akan cocok dengan
    "🔍 Cek Unfollowers" (id) dan "🔍 Check Unfollowers" (en).
    """

    def __init__(self, key: str) -> None:
        self.key = key

    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        return message.text in [
            TEXTS[lang].get(self.key, "") for lang in TEXTS
        ]


# ── Formatter daftar unfollowers ──
def format_unfollowers_list(
    unfollowers: list[str], max_display: int = 50
) -> str:
    """Format daftar unfollowers untuk ditampilkan di chat."""
    if not unfollowers:
        return ""
    lines = [f"{i}. @{u}" for i, u in enumerate(unfollowers[:max_display], 1)]
    if len(unfollowers) > max_display:
        lines.append(f"\n... dan {len(unfollowers) - max_display} lainnya")
    return "\n".join(lines)


# ── Hitung rasio followers / following ──
def calculate_ratio(followers: int, following: int) -> str:
    """Hitung rasio followers/following. Return string."""
    if following == 0:
        return "∞"
    return f"{followers / following:.2f}"
