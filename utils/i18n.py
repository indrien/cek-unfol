"""
Modul multi-bahasa (Indonesia & English)
Teks UI terpusat di sini agar mudah dikelola dan konsisten.
Gunakan get_text(key, lang) untuk mengambil teks sesuai bahasa user.
"""

from __future__ import annotations

from typing import Dict

# ============================================================
# Kamus teks — tambahkan key baru di KEDUA bahasa sekaligus
# ============================================================
TEXTS: Dict[str, Dict[str, str]] = {

    # ── Bahasa Indonesia ──────────────────────────────────
    "id": {
        # Menu utama
        "welcome": (
            "👋 Selamat datang di <b>Cek Unfollowers Bot</b>!\n\n"
            "Bot ini membantu kamu mendeteksi siapa yang tidak "
            "follow-back di Instagram.\n\n"
            "Pilih menu di bawah untuk mulai:"
        ),
        "menu_cek": "🔍 Cek Unfollowers",
        "menu_stats": "📊 Statistik",
        "menu_history": "📋 History",
        "menu_settings": "⚙️ Pengaturan",
        "menu_info": "ℹ️ Info & Bantuan",
        "menu_admin": "🔐 Admin",
        "kembali": "🔙 Kembali",

        # Tools — cek unfollowers
        "pilih_metode": "Pilih metode pengecekan:",
        "metode_auto": "⚡ Auto (Username)",
        "metode_manual": "📁 Manual (Upload File)",
        "kirim_username": (
            "📝 Kirim <b>username Instagram</b> kamu\n"
            "(tanpa tanda @):"
        ),
        "upload_file": (
            "📁 Upload file <b>ZIP</b> dari Instagram Data Download.\n\n"
            "<b>Cara download data:</b>\n"
            "1. Buka Instagram → Settings → Privacy & Security\n"
            "2. Pilih <i>Download Your Information</i>\n"
            "3. Format: <b>JSON</b>\n"
            "4. Download & upload file ZIP-nya ke sini"
        ),
        "proses": "⏳ Sedang memproses, mohon tunggu...",
        "hasil_unfollowers": (
            "📋 <b>Hasil Cek Unfollowers</b>\n\n"
            "👤 Username: <code>{username}</code>\n"
            "👥 Following: <b>{following}</b>\n"
            "👥 Followers: <b>{followers}</b>\n"
            "🚫 Tidak Follow-back: <b>{unfollowers_count}</b>\n\n"
            "{unfollowers_list}"
        ),
        "tidak_ada_unfollowers": (
            "✅ Semua orang yang kamu follow sudah follow-back!"
        ),
        "error_username": (
            "❌ Username tidak ditemukan atau akun bersifat private.\n"
            "Pastikan username benar dan akun tidak di-private."
        ),
        "error_file": (
            "❌ File tidak valid. Pastikan kamu upload file ZIP/JSON "
            "yang benar dari Instagram Data Download."
        ),
        "error_ig_login": (
            "❌ Bot tidak bisa login ke Instagram saat ini.\n"
            "Silakan coba metode Manual (upload file)."
        ),
        "error_ip_blacklist": (
            "🚫 <b>IP server di-blacklist Instagram.</b>\n\n"
            "Metode Auto tidak tersedia saat ini.\n"
            "Gunakan metode <b>📁 Manual (Upload File)</b> sebagai alternatif.\n\n"
            "<i>Admin: tambahkan proxy residensial di .env</i>"
        ),
        "error_umum": "❌ Terjadi kesalahan. Silakan coba lagi nanti.",
        "error_private": (
            "🔒 Akun <code>{username}</code> bersifat <b>private</b>.\n"
            "Metode auto hanya bisa untuk akun publik.\n"
            "Gunakan metode Manual (upload file) sebagai alternatif."
        ),
        "file_terlalu_besar": (
            "📄 Daftar unfollowers terlalu panjang untuk ditampilkan "
            "di chat.\nBerikut file-nya:"
        ),

        # History
        "history_kosong": "📋 Belum ada riwayat pengecekan.",
        "history_title": "📋 <b>Riwayat Pengecekan</b>\n\n",
        "history_item": (
            "{no}. <code>{username}</code> — {method}\n"
            "   🚫 {unfollowers_count} tidak follow-back\n"
            "   🕐 {date}\n\n"
        ),

        # Statistik
        "stats_title": (
            "📊 <b>Statistik Pengecekan Terakhir</b>\n\n"
            "👤 Username: <code>{username}</code>\n"
            "👥 Following: <b>{following}</b>\n"
            "👥 Followers: <b>{followers}</b>\n"
            "📊 Rasio F/F: <b>{ratio}</b>\n"
            "🚫 Tidak Follow-back: <b>{unfollowers}</b>"
        ),
        "stats_kosong": (
            "📊 Belum ada data statistik.\n"
            "Lakukan pengecekan terlebih dahulu."
        ),

        # Pengaturan
        "pengaturan": (
            "⚙️ <b>Pengaturan</b>\n\n"
            "Pilih bahasa / Choose language:"
        ),
        "bahasa_diubah": "✅ Bahasa berhasil diubah ke <b>Bahasa Indonesia</b>.",

        # Info
        "info": (
            "ℹ️ <b>Info & Bantuan</b>\n\n"
            "<b>Cek Unfollowers Bot</b> membantu kamu mendeteksi akun "
            "Instagram yang tidak follow-back.\n\n"
            "<b>Cara Pakai:</b>\n"
            "1. Pilih menu 🔍 Cek Unfollowers\n"
            "2. Pilih metode: <b>Auto</b> atau <b>Manual</b>\n"
            "3. Ikuti instruksi yang diberikan\n\n"
            "<b>⚡ Metode Auto:</b>\n"
            "Kirim username IG → bot otomatis mengecek.\n"
            "Hanya untuk akun <b>publik</b>.\n\n"
            "<b>📁 Metode Manual:</b>\n"
            "Upload file ZIP dari Instagram Data Download.\n"
            "Cocok untuk akun <b>private</b>."
        ),

        # Admin
        "admin_panel": (
            "🔐 <b>Admin Panel</b>\n\n"
            "👥 Total User: <b>{total_users}</b>\n"
            "🔍 Total Pengecekan: <b>{total_checks}</b>"
        ),
        "bukan_admin": "⛔ Kamu tidak memiliki akses admin.",

        # Broadcast (admin)
        "broadcast_kirim": "📢 Kirim pesan yang ingin di-broadcast ke semua user:",
        "broadcast_selesai": "✅ Broadcast selesai dikirim ke <b>{count}</b> user.",
    },

    # ── English ───────────────────────────────────────────
    "en": {
        "welcome": (
            "👋 Welcome to <b>Check Unfollowers Bot</b>!\n\n"
            "This bot helps you detect who doesn't follow you back "
            "on Instagram.\n\n"
            "Choose a menu below to start:"
        ),
        "menu_cek": "🔍 Check Unfollowers",
        "menu_stats": "📊 Statistics",
        "menu_history": "📋 History",
        "menu_settings": "⚙️ Settings",
        "menu_info": "ℹ️ Info & Help",
        "menu_admin": "🔐 Admin",
        "kembali": "🔙 Back",

        "pilih_metode": "Choose checking method:",
        "metode_auto": "⚡ Auto (Username)",
        "metode_manual": "📁 Manual (Upload File)",
        "kirim_username": (
            "📝 Send your <b>Instagram username</b>\n"
            "(without @):"
        ),
        "upload_file": (
            "📁 Upload your <b>ZIP</b> file from Instagram Data Download.\n\n"
            "<b>How to download:</b>\n"
            "1. Open Instagram → Settings → Privacy & Security\n"
            "2. Select <i>Download Your Information</i>\n"
            "3. Format: <b>JSON</b>\n"
            "4. Download & upload the ZIP file here"
        ),
        "proses": "⏳ Processing, please wait...",
        "hasil_unfollowers": (
            "📋 <b>Unfollowers Check Result</b>\n\n"
            "👤 Username: <code>{username}</code>\n"
            "👥 Following: <b>{following}</b>\n"
            "👥 Followers: <b>{followers}</b>\n"
            "🚫 Not Following Back: <b>{unfollowers_count}</b>\n\n"
            "{unfollowers_list}"
        ),
        "tidak_ada_unfollowers": (
            "✅ Everyone you follow is following you back!"
        ),
        "error_username": (
            "❌ Username not found or account is private.\n"
            "Make sure the username is correct and the account is public."
        ),
        "error_file": (
            "❌ Invalid file. Make sure you upload the correct "
            "ZIP/JSON file from Instagram Data Download."
        ),
        "error_ig_login": (
            "❌ Bot can't login to Instagram right now.\n"
            "Please try the Manual method (upload file)."
        ),
        "error_ip_blacklist": (
            "🚫 <b>Server IP is blacklisted by Instagram.</b>\n\n"
            "Auto method is not available right now.\n"
            "Use <b>📁 Manual (Upload File)</b> method instead.\n\n"
            "<i>Admin: add a residential proxy in .env</i>"
        ),
        "error_umum": "❌ An error occurred. Please try again later.",
        "error_private": (
            "🔒 Account <code>{username}</code> is <b>private</b>.\n"
            "Auto method only works for public accounts.\n"
            "Use Manual method (upload file) as an alternative."
        ),
        "file_terlalu_besar": (
            "📄 Unfollowers list is too long to display in chat.\n"
            "Here is the file:"
        ),

        "history_kosong": "📋 No check history yet.",
        "history_title": "📋 <b>Check History</b>\n\n",
        "history_item": (
            "{no}. <code>{username}</code> — {method}\n"
            "   🚫 {unfollowers_count} not following back\n"
            "   🕐 {date}\n\n"
        ),

        "stats_title": (
            "📊 <b>Last Check Statistics</b>\n\n"
            "👤 Username: <code>{username}</code>\n"
            "👥 Following: <b>{following}</b>\n"
            "👥 Followers: <b>{followers}</b>\n"
            "📊 Ratio F/F: <b>{ratio}</b>\n"
            "🚫 Not Following Back: <b>{unfollowers}</b>"
        ),
        "stats_kosong": (
            "📊 No statistics data yet.\n"
            "Run a check first."
        ),

        "pengaturan": (
            "⚙️ <b>Settings</b>\n\n"
            "Pilih bahasa / Choose language:"
        ),
        "bahasa_diubah": "✅ Language changed to <b>English</b>.",

        "info": (
            "ℹ️ <b>Info & Help</b>\n\n"
            "<b>Check Unfollowers Bot</b> helps you detect Instagram "
            "accounts that don't follow you back.\n\n"
            "<b>How to Use:</b>\n"
            "1. Select 🔍 Check Unfollowers menu\n"
            "2. Choose method: <b>Auto</b> or <b>Manual</b>\n"
            "3. Follow the instructions\n\n"
            "<b>⚡ Auto Method:</b>\n"
            "Send IG username → bot auto checks.\n"
            "Only for <b>public</b> accounts.\n\n"
            "<b>📁 Manual Method:</b>\n"
            "Upload ZIP file from Instagram Data Download.\n"
            "Works for <b>private</b> accounts too."
        ),

        "admin_panel": (
            "🔐 <b>Admin Panel</b>\n\n"
            "👥 Total Users: <b>{total_users}</b>\n"
            "🔍 Total Checks: <b>{total_checks}</b>"
        ),
        "bukan_admin": "⛔ You don't have admin access.",

        "broadcast_kirim": "📢 Send the message you want to broadcast to all users:",
        "broadcast_selesai": "✅ Broadcast sent to <b>{count}</b> users.",
    },
}


def get_text(key: str, lang: str = "id", **kwargs) -> str:
    """
    Ambil teks berdasarkan key dan bahasa.
    Jika key tidak ditemukan di bahasa yg dipilih, fallback ke 'id'.
    Keyword arguments akan di-format ke dalam string.
    """
    text = TEXTS.get(lang, TEXTS["id"]).get(key, TEXTS["id"].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text
