"""
Registrasi semua router handler ke dispatcher.
Urutan penting: handler yang lebih spesifik didaftarkan lebih dulu.
"""

from aiogram import Router

from handlers import start, tools, stats, history, settings, info, admin


def register_all_routers() -> Router:
    """Buat router utama & daftarkan semua sub-router."""
    main_router = Router()

    # Urutan registrasi:
    # 1. Admin (spesifik, ada pengecekan akses)
    # 2. Tools (fitur utama, ada FSM)
    # 3. Lainnya (menu biasa)
    # 4. Start (paling umum: /start & kembali)
    main_router.include_router(admin.router)
    main_router.include_router(tools.router)
    main_router.include_router(stats.router)
    main_router.include_router(history.router)
    main_router.include_router(settings.router)
    main_router.include_router(info.router)
    main_router.include_router(start.router)

    return main_router
