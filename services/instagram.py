"""
Layanan Instagram — dua metode pengecekan unfollowers:
1. Auto  : via Instagrapi (unofficial API), user cukup kirim username.
2. Manual: user upload file ZIP/JSON dari Instagram Data Download.
"""

from __future__ import annotations

import asyncio
import json
import io
import zipfile
import logging
from typing import Optional, List

from instagrapi import Client
from instagrapi.exceptions import (
    LoginRequired,
    ClientError,
    ChallengeRequired,
    PleaseWaitFewMinutes,
)

from config import IG_USERNAME, IG_PASSWORD

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════
#  METODE 1 — AUTO (Instagrapi)
# ══════════════════════════════════════════════

# Singleton client Instagram
_client: Optional[Client] = None


async def _get_client() -> Client:
    """Dapatkan client Instagram yang sudah login (singleton)."""
    global _client
    if _client is None:
        _client = Client()
        # Login di thread terpisah agar tidak blocking
        try:
            await asyncio.to_thread(_client.login, IG_USERNAME, IG_PASSWORD)
            logger.info("Login Instagram berhasil.")
        except Exception as e:
            logger.error("Gagal login Instagram: %s", e)
            _client = None
            raise
    return _client


async def check_unfollowers_auto(username: str) -> dict:
    """
    Cek unfollowers secara otomatis via Instagrapi.
    Hanya bisa untuk akun publik.

    Returns:
        dict: {success, username, followers_count, following_count,
               unfollowers, unfollowers_count} atau {success, error}
    """
    try:
        cl = await _get_client()

        # Ambil info user
        user_id = await asyncio.to_thread(
            cl.user_id_from_username, username
        )
        user_info = await asyncio.to_thread(cl.user_info, user_id)

        # Cek akun private
        if user_info.is_private:
            return {"success": False, "error": "private_account"}

        # Ambil followers & following (di thread terpisah)
        followers_raw = await asyncio.to_thread(cl.user_followers, user_id)
        following_raw = await asyncio.to_thread(cl.user_following, user_id)

        # Bandingkan: yang di-follow tapi tidak follow-back = unfollowers
        followers_set = {u.username for u in followers_raw.values()}
        following_set = {u.username for u in following_raw.values()}
        unfollowers = sorted(following_set - followers_set)

        return {
            "success": True,
            "username": username,
            "followers_count": len(followers_raw),
            "following_count": len(following_raw),
            "unfollowers": unfollowers,
            "unfollowers_count": len(unfollowers),
        }

    except (LoginRequired, ChallengeRequired):
        # Reset client agar login ulang di request berikutnya
        global _client
        _client = None
        return {"success": False, "error": "login_required"}
    except PleaseWaitFewMinutes:
        return {"success": False, "error": "rate_limited"}
    except ClientError as e:
        err = str(e).lower()
        if "not found" in err:
            return {"success": False, "error": "user_not_found"}
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error("Error cek unfollowers auto: %s", e)
        return {"success": False, "error": str(e)}


# ══════════════════════════════════════════════
#  METODE 2 — MANUAL (Upload file ZIP/JSON)
# ══════════════════════════════════════════════

def _extract_usernames_from_list(data: list) -> List[str]:
    """Ekstrak username dari format list Instagram JSON."""
    usernames = []
    for item in data:
        if isinstance(item, dict) and "string_list_data" in item:
            for sd in item["string_list_data"]:
                val = sd.get("value", "")
                if val:
                    usernames.append(val)
        elif isinstance(item, str):
            usernames.append(item)
    return usernames


def parse_instagram_zip(file_bytes: bytes) -> dict:
    """
    Parse file ZIP dari Instagram Data Download.
    Mencari followers_1.json dan following.json di dalamnya.
    """
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
            followers_data = []
            following_data = []

            for name in zf.namelist():
                lower = name.lower()
                # Cari file followers
                if "followers" in lower and lower.endswith(".json"):
                    with zf.open(name) as f:
                        raw = json.load(f)
                        if isinstance(raw, list):
                            followers_data.extend(raw)
                        elif isinstance(raw, dict):
                            # Format baru: key relationships_followers
                            for key in raw:
                                if "follower" in key.lower():
                                    followers_data.extend(raw[key])
                # Cari file following
                elif "following" in lower and lower.endswith(".json"):
                    with zf.open(name) as f:
                        raw = json.load(f)
                        if isinstance(raw, list):
                            following_data.extend(raw)
                        elif isinstance(raw, dict):
                            for key in raw:
                                if "following" in key.lower():
                                    following_data.extend(raw[key])

            if not followers_data and not following_data:
                return {"success": False, "error": "file_empty"}

            followers_set = set(_extract_usernames_from_list(followers_data))
            following_set = set(_extract_usernames_from_list(following_data))
            unfollowers = sorted(following_set - followers_set)

            return {
                "success": True,
                "followers_count": len(followers_set),
                "following_count": len(following_set),
                "unfollowers": unfollowers,
                "unfollowers_count": len(unfollowers),
            }
    except zipfile.BadZipFile:
        return {"success": False, "error": "bad_zip"}
    except Exception as e:
        logger.error("Error parse ZIP: %s", e)
        return {"success": False, "error": str(e)}


def parse_instagram_json(file_bytes: bytes) -> dict:
    """
    Parse file JSON tunggal dari Instagram Data Download.
    Mendukung format lama & baru.
    """
    try:
        data = json.loads(file_bytes)
        followers_list: List[str] = []
        following_list: List[str] = []

        if isinstance(data, dict):
            # Format: {"relationships_followers": [...], ...}
            for key, val in data.items():
                lower_key = key.lower()
                if "follower" in lower_key and isinstance(val, list):
                    followers_list.extend(_extract_usernames_from_list(val))
                elif "following" in lower_key and isinstance(val, list):
                    following_list.extend(_extract_usernames_from_list(val))

        elif isinstance(data, list):
            # Single list — anggap ini followers, following perlu file terpisah
            followers_list = _extract_usernames_from_list(data)

        followers_set = set(followers_list)
        following_set = set(following_list)

        if not followers_set and not following_set:
            return {"success": False, "error": "file_empty"}

        unfollowers = sorted(following_set - followers_set)

        return {
            "success": True,
            "followers_count": len(followers_set),
            "following_count": len(following_set),
            "unfollowers": unfollowers,
            "unfollowers_count": len(unfollowers),
        }
    except json.JSONDecodeError:
        return {"success": False, "error": "invalid_json"}
    except Exception as e:
        logger.error("Error parse JSON: %s", e)
        return {"success": False, "error": str(e)}
