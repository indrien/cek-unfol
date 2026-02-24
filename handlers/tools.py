"""
Handler Tools — Cek Unfollowers (Auto & Manual)
Fitur utama bot: mendeteksi siapa yang tidak follow-back di Instagram.
Menggunakan FSM (Finite State Machine) untuk alur percakapan.
"""

import io
import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    CallbackQuery,
    ForceReply,
    BufferedInputFile,
)

from database.mongodb import get_user_lang, save_history
from keyboards.inline_kb import metode_cek_kb
from keyboards.reply_kb import back_kb, main_menu_kb
from services.instagram import (
    check_unfollowers_auto,
    parse_instagram_zip,
    parse_instagram_json,
)
from utils.auto_delete import safe_delete, mark_important
from utils.helpers import MenuFilter, format_unfollowers_list
from utils.i18n import get_text
from config import ADMIN_IDS

logger = logging.getLogger(__name__)

router = Router()


# ── FSM States ──
class CheckStates(StatesGroup):
    """State untuk alur pengecekan unfollowers."""
    waiting_username = State()  # Menunggu user kirim username IG
    waiting_file = State()      # Menunggu user upload file ZIP/JSON


# ══════════════════════════════════════════════
#  MENU CEK UNFOLLOWERS — pilih metode
# ══════════════════════════════════════════════

@router.message(MenuFilter("menu_cek"))
async def menu_cek_unfollowers(message: Message) -> None:
    """Tampilkan pilihan metode pengecekan (InlineKeyboard)."""
    lang = await get_user_lang(message.from_user.id)

    sent = await message.answer(
        get_text("pilih_metode", lang),
        reply_markup=metode_cek_kb(lang),
        parse_mode="HTML",
    )
    mark_important(message.chat.id, sent.message_id)


# ══════════════════════════════════════════════
#  CALLBACK — user pilih metode Auto
# ══════════════════════════════════════════════

@router.callback_query(F.data == "cek_auto")
async def cb_cek_auto(callback: CallbackQuery, state: FSMContext) -> None:
    """User memilih metode Auto → minta username IG."""
    lang = await get_user_lang(callback.from_user.id)
    await callback.answer()

    # Hapus pesan pilihan metode
    await safe_delete(
        callback.bot, callback.message.chat.id, callback.message.message_id
    )

    # Minta username via ForceReply (step-by-step)
    sent = await callback.message.answer(
        get_text("kirim_username", lang),
        reply_markup=ForceReply(selective=True),
        parse_mode="HTML",
    )
    mark_important(callback.message.chat.id, sent.message_id)

    # Set FSM state: menunggu username
    await state.set_state(CheckStates.waiting_username)


# ══════════════════════════════════════════════
#  CALLBACK — user pilih metode Manual
# ══════════════════════════════════════════════

@router.callback_query(F.data == "cek_manual")
async def cb_cek_manual(callback: CallbackQuery, state: FSMContext) -> None:
    """User memilih metode Manual → minta upload file."""
    lang = await get_user_lang(callback.from_user.id)
    await callback.answer()

    # Hapus pesan pilihan metode
    await safe_delete(
        callback.bot, callback.message.chat.id, callback.message.message_id
    )

    # Minta upload file
    sent = await callback.message.answer(
        get_text("upload_file", lang),
        reply_markup=back_kb(lang),
        parse_mode="HTML",
    )
    mark_important(callback.message.chat.id, sent.message_id)

    # Set FSM state: menunggu file
    await state.set_state(CheckStates.waiting_file)


# ══════════════════════════════════════════════
#  HANDLER — terima username (metode Auto)
# ══════════════════════════════════════════════

@router.message(CheckStates.waiting_username, F.text)
async def process_username(message: Message, state: FSMContext) -> None:
    """Proses username yang dikirim user — cek unfollowers via Instagrapi."""
    lang = await get_user_lang(message.from_user.id)
    username = message.text.strip().lstrip("@").lower()

    # Validasi format username sederhana
    if not username or " " in username or len(username) > 30:
        await message.answer(
            get_text("error_username", lang),
            parse_mode="HTML",
        )
        return

    # Kirim pesan proses
    proses_msg = await message.answer(
        get_text("proses", lang),
        parse_mode="HTML",
    )

    # Jalankan pengecekan
    result = await check_unfollowers_auto(username)

    # Hapus pesan "sedang memproses"
    await safe_delete(message.bot, message.chat.id, proses_msg.message_id)

    if not result["success"]:
        # Tangani error spesifik
        error = result.get("error", "")
        if error == "private_account":
            error_text = get_text("error_private", lang, username=username)
        elif error in ("user_not_found",):
            error_text = get_text("error_username", lang)
        elif error in ("login_required", "rate_limited"):
            error_text = get_text("error_ig_login", lang)
        elif error == "ip_blacklisted":
            error_text = get_text("error_ip_blacklist", lang)
        else:
            error_text = get_text("error_umum", lang)

        await message.answer(error_text, parse_mode="HTML")
        await state.clear()
        return

    # Berhasil — tampilkan hasil & simpan history
    await _send_result(message, lang, username, result, method="auto")

    # Simpan ke database
    await save_history(message.from_user.id, username, "auto", result)

    # Reset FSM
    await state.clear()

    # Kembalikan ke menu utama
    is_admin = message.from_user.id in ADMIN_IDS
    sent = await message.answer(
        get_text("welcome", lang),
        reply_markup=main_menu_kb(lang, is_admin),
        parse_mode="HTML",
    )
    mark_important(message.chat.id, sent.message_id)


# ══════════════════════════════════════════════
#  HANDLER — terima file (metode Manual)
# ══════════════════════════════════════════════

@router.message(CheckStates.waiting_file, F.document)
async def process_file(message: Message, state: FSMContext) -> None:
    """Proses file ZIP/JSON yang diupload user."""
    lang = await get_user_lang(message.from_user.id)
    doc = message.document

    # Validasi tipe file
    file_name = (doc.file_name or "").lower()
    if not (file_name.endswith(".zip") or file_name.endswith(".json")):
        await message.answer(
            get_text("error_file", lang),
            parse_mode="HTML",
        )
        return

    # Kirim pesan proses
    proses_msg = await message.answer(
        get_text("proses", lang),
        parse_mode="HTML",
    )

    # Download file dari Telegram
    file = await message.bot.download(doc)
    file_bytes = file.read()

    # Parse berdasarkan tipe file
    if file_name.endswith(".zip"):
        result = parse_instagram_zip(file_bytes)
    else:
        result = parse_instagram_json(file_bytes)

    # Hapus pesan proses
    await safe_delete(message.bot, message.chat.id, proses_msg.message_id)

    if not result["success"]:
        await message.answer(
            get_text("error_file", lang),
            parse_mode="HTML",
        )
        await state.clear()
        return

    # Ambil username dari file name atau pakai placeholder
    ig_username = file_name.replace(".zip", "").replace(".json", "")

    # Berhasil — tampilkan hasil & simpan history
    await _send_result(message, lang, ig_username, result, method="manual")

    await save_history(message.from_user.id, ig_username, "manual", result)
    await state.clear()

    # Kembalikan ke menu utama
    is_admin = message.from_user.id in ADMIN_IDS
    sent = await message.answer(
        get_text("welcome", lang),
        reply_markup=main_menu_kb(lang, is_admin),
        parse_mode="HTML",
    )
    mark_important(message.chat.id, sent.message_id)


# ══════════════════════════════════════════════
#  HELPER — kirim hasil ke user
# ══════════════════════════════════════════════

async def _send_result(
    message: Message,
    lang: str,
    username: str,
    result: dict,
    method: str,
) -> None:
    """
    Kirim hasil pengecekan ke user.
    Jika daftar terlalu panjang → kirim sebagai file TXT.
    """
    unfollowers = result.get("unfollowers", [])

    if not unfollowers:
        # Tidak ada unfollowers
        sent = await message.answer(
            get_text("tidak_ada_unfollowers", lang),
            parse_mode="HTML",
        )
        mark_important(message.chat.id, sent.message_id)
        return

    # Format daftar unfollowers (maks 50 untuk chat)
    unfollowers_text = format_unfollowers_list(unfollowers, max_display=50)

    # Kirim hasil (pesan penting — tidak dihapus)
    sent = await message.answer(
        get_text(
            "hasil_unfollowers",
            lang,
            username=username,
            following=result["following_count"],
            followers=result["followers_count"],
            unfollowers_count=result["unfollowers_count"],
            unfollowers_list=unfollowers_text,
        ),
        parse_mode="HTML",
    )
    mark_important(message.chat.id, sent.message_id)

    # Jika lebih dari 50 unfollowers, kirim file TXT tambahan
    if len(unfollowers) > 50:
        file_content = "\n".join(
            f"{i}. @{u}" for i, u in enumerate(unfollowers, 1)
        )
        file_buf = BufferedInputFile(
            file_content.encode("utf-8"),
            filename=f"unfollowers_{username}.txt",
        )
        sent_file = await message.answer_document(
            file_buf,
            caption=get_text("file_terlalu_besar", lang),
        )
        mark_important(message.chat.id, sent_file.message_id)
