"""
Konfigurasi utama bot — memuat environment variables
"""

from __future__ import annotations

import os
from typing import List

from dotenv import load_dotenv

# Muat file .env
load_dotenv()

# === Token Bot Telegram ===
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

# === ID Admin (list integer) ===
_admin_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: List[int] = [
    int(x.strip()) for x in _admin_raw.split(",") if x.strip().isdigit()
]

# === MongoDB ===
MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "cek_unfol_bot")

# === Akun Instagram untuk metode auto ===
IG_USERNAME: str = os.getenv("IG_USERNAME", "")
IG_PASSWORD: str = os.getenv("IG_PASSWORD", "")

# === Proxy untuk Instagram (opsional tapi DISARANKAN) ===
# Format: http://user:pass@host:port atau socks5://user:pass@host:port
# Tanpa proxy, IP datacenter (DigitalOcean, AWS, dll) akan di-blacklist Instagram
IG_PROXY: str = os.getenv("IG_PROXY", "")
