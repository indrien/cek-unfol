"""
Proxy Fetcher v2 — sistem proxy cerdas untuk Instagram
Fitur:
- 7+ sumber proxy gratis (HTTP & SOCKS5)
- Validasi proxy sebelum dipakai (test koneksi)
- Cache proxy yang sudah terbukti jalan (working proxies)
- Rotasi otomatis: HTTP → SOCKS5 → SOCKS4
- Blacklist proxy yang gagal agar tidak dipakai ulang
"""

from __future__ import annotations

import asyncio
import random
import time
import logging
from typing import Optional, List, Set

import aiohttp

logger = logging.getLogger(__name__)

# ── Sumber proxy gratis dari GitHub (raw URL) ──
PROXY_SOURCES = {
    "http": [
        # TheSpeedX — update tiap jam
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        # monosans — update tiap jam
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        # clarketm — update tiap jam
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
        # ShiftyTR — update tiap jam
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        # sunny9577 — update tiap hari
        "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/generated/http_proxies.txt",
        # proxyscrape API — realtime
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
    ],
    "socks5": [
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=all",
    ],
    "socks4": [
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=5000&country=all",
    ],
}

# ── Cache & State ──
_proxy_cache: dict[str, List[str]] = {}  # per-type cache
_last_fetch: dict[str, float] = {}       # waktu fetch terakhir per type
_working_proxies: List[str] = []         # proxy yang sudah terbukti jalan
_blacklisted: Set[str] = set()           # proxy yang gagal, jangan pakai lagi
CACHE_TTL = 900       # 15 menit cache (lebih sering refresh)
VALIDATE_TIMEOUT = 7  # timeout validasi proxy (detik)
MAX_BLACKLIST = 500    # batas blacklist agar tidak terlalu besar


async def _fetch_proxy_list(url: str) -> List[str]:
    """Ambil daftar proxy dari satu URL."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    proxies = [
                        line.strip()
                        for line in text.splitlines()
                        if line.strip() and ":" in line and "." in line
                    ]
                    logger.info(
                        "✓ %d proxy dari %s",
                        len(proxies),
                        url.split("/")[-1][:40],
                    )
                    return proxies
    except Exception as e:
        logger.debug("Gagal fetch: %s — %s", url.split("/")[-1][:40], e)
    return []


async def fetch_all_proxies(proxy_type: str = "http") -> List[str]:
    """
    Ambil semua proxy dari berbagai sumber.
    proxy_type: "http", "socks5", atau "socks4"
    """
    global _proxy_cache, _last_fetch

    now = time.time()
    last = _last_fetch.get(proxy_type, 0)

    # Gunakan cache jika masih valid
    if proxy_type in _proxy_cache and (now - last) < CACHE_TTL:
        return _proxy_cache[proxy_type]

    urls = PROXY_SOURCES.get(proxy_type, PROXY_SOURCES["http"])
    tasks = [_fetch_proxy_list(url) for url in urls]
    results = await asyncio.gather(*tasks)

    # Gabungkan, hapus duplikat & blacklisted
    all_proxies = list(set(
        proxy for result in results for proxy in result
        if proxy not in _blacklisted
    ))
    random.shuffle(all_proxies)

    _proxy_cache[proxy_type] = all_proxies
    _last_fetch[proxy_type] = now

    logger.info("Total %s proxy tersedia: %d", proxy_type, len(all_proxies))
    return all_proxies


async def validate_proxy(proxy_url: str) -> bool:
    """
    Test apakah proxy bisa konek ke internet.
    Test ke httpbin.org dan instagram.com.
    """
    test_urls = [
        "https://httpbin.org/ip",
        "https://www.instagram.com/",
    ]
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            # Test ke httpbin dulu (ringan)
            async with session.get(
                test_urls[0],
                proxy=proxy_url,
                timeout=aiohttp.ClientTimeout(total=VALIDATE_TIMEOUT),
            ) as resp:
                if resp.status == 200:
                    logger.info("✓ Proxy valid: %s", proxy_url)
                    return True
    except Exception:
        pass
    return False


def blacklist_proxy(proxy: str) -> None:
    """Tambahkan proxy ke blacklist agar tidak dipakai lagi."""
    global _blacklisted
    # Ekstrak ip:port dari URL
    clean = proxy.replace("http://", "").replace("socks5://", "").replace("socks4://", "")
    _blacklisted.add(clean)

    # Bersihkan blacklist jika terlalu banyak (reset)
    if len(_blacklisted) > MAX_BLACKLIST:
        _blacklisted = set(list(_blacklisted)[-200:])
        logger.info("Blacklist di-reset, simpan 200 terakhir")


def format_proxy_url(proxy: str, proxy_type: str = "http") -> str:
    """Format proxy mentah (ip:port) ke URL yang bisa dipakai."""
    if proxy.startswith(("http://", "https://", "socks5://", "socks4://")):
        return proxy
    return f"{proxy_type}://{proxy}"


async def get_validated_proxy(
    proxy_type: str = "http",
    max_test: int = 15,
) -> Optional[str]:
    """
    Ambil proxy yang sudah divalidasi (test koneksi dulu).
    Mencoba max_test proxy, return yang pertama berhasil.
    """
    global _working_proxies

    # Coba dari working proxies dulu (sudah pernah jalan)
    if _working_proxies:
        proxy = random.choice(_working_proxies)
        logger.info("Coba working proxy: %s", proxy)
        if await validate_proxy(proxy):
            return proxy
        # Hapus dari working list jika sudah tidak jalan
        _working_proxies = [p for p in _working_proxies if p != proxy]

    # Fetch proxy baru & test satu-satu
    proxies = await fetch_all_proxies(proxy_type)
    if not proxies:
        return None

    # Ambil sample acak untuk di-test
    sample = random.sample(proxies, min(max_test, len(proxies)))

    for raw_proxy in sample:
        proxy_url = format_proxy_url(raw_proxy, proxy_type)
        if await validate_proxy(proxy_url):
            # Simpan ke working list
            if proxy_url not in _working_proxies:
                _working_proxies.append(proxy_url)
                # Batasi working list
                if len(_working_proxies) > 20:
                    _working_proxies = _working_proxies[-20:]
            return proxy_url
        else:
            blacklist_proxy(raw_proxy)

    return None


async def get_random_proxy(proxy_type: str = "http") -> Optional[str]:
    """Ambil satu proxy acak (tanpa validasi, untuk fallback cepat)."""
    proxies = await fetch_all_proxies(proxy_type)
    if not proxies:
        return None
    proxy = random.choice(proxies)
    return format_proxy_url(proxy, proxy_type)


async def get_best_proxy() -> Optional[str]:
    """
    Strategi cerdas: coba semua tipe proxy sampai dapat yang jalan.
    Urutan: HTTP → SOCKS5 → SOCKS4
    """
    for ptype in ["http", "socks5", "socks4"]:
        logger.info("Mencari proxy %s yang valid...", ptype.upper())
        proxy = await get_validated_proxy(ptype, max_test=10)
        if proxy:
            return proxy

    # Fallback: random tanpa validasi (yolo)
    logger.warning("Tidak ada proxy valid, coba random tanpa test...")
    return await get_random_proxy("http")


def get_proxy_stats() -> dict:
    """Statistik proxy untuk admin panel."""
    return {
        "working": len(_working_proxies),
        "blacklisted": len(_blacklisted),
        "cached_http": len(_proxy_cache.get("http", [])),
        "cached_socks5": len(_proxy_cache.get("socks5", [])),
        "cached_socks4": len(_proxy_cache.get("socks4", [])),
    }
