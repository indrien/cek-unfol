"""
Operasi MongoDB — User, History, Statistik
Menggunakan Motor (async driver) agar tidak blocking event loop.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, MONGO_DB_NAME

# ── Inisialisasi koneksi ──
client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB_NAME]

# ── Koleksi ──
users_col = db["users"]
history_col = db["history"]


# ═══════════════════════════════════════════
#  USER
# ═══════════════════════════════════════════

async def save_user(user_id: int, username: str, lang: str = "id") -> None:
    """Simpan atau update data user (upsert)."""
    now = datetime.now(timezone.utc)
    await users_col.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "user_id": user_id,
                "username": username,
                "lang": lang,
                "updated_at": now,
            },
            "$setOnInsert": {"created_at": now},
        },
        upsert=True,
    )


async def get_user(user_id: int) -> Optional[dict]:
    """Ambil data user berdasarkan user_id."""
    return await users_col.find_one({"user_id": user_id})


async def set_user_lang(user_id: int, lang: str) -> None:
    """Ubah bahasa preferensi user."""
    await users_col.update_one(
        {"user_id": user_id},
        {"$set": {"lang": lang}},
    )


async def get_user_lang(user_id: int) -> str:
    """Ambil bahasa user, default 'id' jika belum ada."""
    user = await users_col.find_one({"user_id": user_id})
    return user.get("lang", "id") if user else "id"


async def get_all_user_ids() -> list[int]:
    """Ambil semua user_id untuk broadcast."""
    cursor = users_col.find({}, {"user_id": 1})
    docs = await cursor.to_list(length=None)
    return [d["user_id"] for d in docs]


# ═══════════════════════════════════════════
#  HISTORY
# ═══════════════════════════════════════════

async def save_history(
    user_id: int,
    ig_username: str,
    method: str,
    result: dict,
) -> None:
    """Simpan riwayat pengecekan unfollowers."""
    await history_col.insert_one(
        {
            "user_id": user_id,
            "ig_username": ig_username,
            "method": method,
            "followers_count": result.get("followers_count", 0),
            "following_count": result.get("following_count", 0),
            "unfollowers_count": result.get("unfollowers_count", 0),
            "unfollowers": result.get("unfollowers", []),
            "checked_at": datetime.now(timezone.utc),
        }
    )


async def get_history(user_id: int, limit: int = 10) -> list[dict]:
    """Ambil riwayat pengecekan user (terbaru di atas)."""
    cursor = (
        history_col.find({"user_id": user_id})
        .sort("checked_at", -1)
        .limit(limit)
    )
    return await cursor.to_list(length=limit)


async def get_last_check(user_id: int) -> Optional[dict]:
    """Ambil pengecekan terakhir user (untuk statistik)."""
    return await history_col.find_one(
        {"user_id": user_id},
        sort=[("checked_at", -1)],
    )


# ═══════════════════════════════════════════
#  ADMIN — Statistik Global
# ═══════════════════════════════════════════

async def get_total_users() -> int:
    """Hitung total user terdaftar."""
    return await users_col.count_documents({})


async def get_total_checks() -> int:
    """Hitung total pengecekan yang pernah dilakukan."""
    return await history_col.count_documents({})
