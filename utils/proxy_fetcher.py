"""
Proxy Fetcher — ambil proxy gratis dari GitHub
Sumber: TheSpeedX/PROXY-List & monosans/proxy-list
Proxy di-update otomatis setiap jam oleh pemilik repo.

Catatan: Proxy gratis = datacenter IP, tingkat keberhasilan rendah
untuk Instagram. Tapi patut dicoba sebelum beli proxy berbayar.
"""

from __future__ import annotations

import asyncio
import random
import logging
from typing import Optional, List

import aiohttp

logger = logging.getLogger(__name__)

# ── Sumber proxy gratis dari GitHub (raw URL) ──
PROXY_SOURCES = {
    "http": [
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    ],
    "socks5": [
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    ],
}

# Cache proxy yang sudah di-fetch
_proxy_cache: List[str] = []
_last_fetch: float = 0
CACHE_TTL = 1800  # 30 menit cache


async def _fetch_proxy_list(url: str) -> List[str]:
    """Ambil daftar proxy dari satu URL."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    proxies = [
                        line.strip()
                        for line in text.splitlines()
                        if line.strip() and ":" in line
                    ]
                    logger.info("Dapat %d proxy dari %s", len(proxies), url.split("/")[-1])
                    return proxies
    except Exception as e:
        logger.warning("Gagal fetch proxy dari %s: %s", url, e)
    return []


async def fetch_all_proxies(proxy_type: str = "http") -> List[str]:
    """
    Ambil semua proxy dari berbagai sumber.
    proxy_type: "http" atau "socks5"
    """
    import time
    global _proxy_cache, _last_fetch

    # Gunakan cache jika masih valid
    if _proxy_cache and (time.time() - _last_fetch) < CACHE_TTL:
        return _proxy_cache

    urls = PROXY_SOURCES.get(proxy_type, PROXY_SOURCES["http"])
    tasks = [_fetch_proxy_list(url) for url in urls]
    results = await asyncio.gather(*tasks)

    # Gabungkan semua proxy & hapus duplikat
    all_proxies = list(set(
        proxy for result in results for proxy in result
    ))
    random.shuffle(all_proxies)

    _proxy_cache = all_proxies
    _last_fetch = time.time()

    logger.info("Total proxy tersedia: %d", len(all_proxies))
    return all_proxies


def format_proxy_url(proxy: str, proxy_type: str = "http") -> str:
    """Format proxy mentah (ip:port) ke URL yang bisa dipakai Instagrapi."""
    if proxy.startswith(("http://", "https://", "socks5://")):
        return proxy
    return f"{proxy_type}://{proxy}"


async def get_random_proxy(proxy_type: str = "http") -> Optional[str]:
    """Ambil satu proxy acak yang sudah di-format."""
    proxies = await fetch_all_proxies(proxy_type)
    if not proxies:
        return None
    proxy = random.choice(proxies)
    return format_proxy_url(proxy, proxy_type)
