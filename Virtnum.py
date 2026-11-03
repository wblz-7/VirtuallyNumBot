import json
import os
import logging
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ----------------- कॉन्फ़िगरेशन -----------------
TELEGRAM_BOT_TOKEN = "9022890187:AAG0o-38kvoTT9VqZp1zncjfw5L0ZDSeTa4"
API_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tness/@public/api"
API_KEY = "MXTFIGM7AIX"

# Apna Telegram User ID yahan replace karein (e.g. 123456789)
ADMIN_ID = 7194867487

HEADERS = {
    "mauthapi": API_KEY,
    "Content-Type": "application/json"
}

DB_FILE = "users.json"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ----------------- डेटाबेस फ़ंक्शंस -----------------
def load_users():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.add(user_id)
        with open(DB_FILE, "w") as f:
            json.dump(list(users), f)

# ----------------- मेन डैशबोर्ड -----------------
def main_dashboard(is_admin=False):
    text = (
        "◈ ──────────── ◈\n"
        "      𝖵𝖨𝖱𝖳𝖴𝖠𝖫 𝖭𝖴𝖬𝖡𝖤𝖱 𝖲𝖴𝖨𝖳𝖤      \n"
        "◈ ──────────── ◈\n\n"
        "⟡ 𝖲𝖤𝖱𝖵𝖨𝖢𝖤  : ᯤ̸ 𝖮𝖭𝖫𝖨𝖭𝖤\n"
        "⟡ 𝖲𝖳𝖠𝖳𝖴𝖲    : 𝖱𝖤𝖠𝖣𝖸\n\n"
        "✦ 𝖲𝖾𝗅𝖾𝖼𝗍 𝖺𝗇 𝗈𝗉𝗍𝗂𝗈𝗇 𝗍𝗈 𝗉𝗋𝗈𝖼𝖾𝖾𝖽:"
    )
    keyboard = [
        [InlineKeyboardButton("◈ 𝖱𝖤𝖰𝖴𝖤𝖲𝖳 𝖭𝖴𝖬𝖡𝖤𝖱 ◈", callback_data="btn_ask_rid")],
        [
            InlineKeyboardButton("▣ 𝖢𝖮𝖭𝖲𝖮𝖫𝖤 𝖫𝖮𝖦𝖲", callback_data="btn_console_logs"),
            InlineKeyboardButton("✦ 𝖲𝖤𝖱𝖵𝖤𝖱 𝖨𝖭𝖥𝖮", callback_data="btn_live_status")
        ]
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton("⚙ 𝖮𝖶𝖭𝖤𝖱 𝖯𝖠𝖭𝖤𝖫 ⚙", callback_data="btn_admin_panel")])

    return text, InlineKeyboardMarkup(keyboard)

# ----------------- कमांड और कॉलबैक हैंडलर -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    context.user_data.clear()

    is_admin = (user_id == ADMIN_ID)
    text, markup = main_dashboard(is_admin=is_admin)
    if update.message:
        await update.message.reply_text(text, reply_markup=markup, parse_mode="Markdown")

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id

    # 1. RANGE INPUT SCREEN
    if data == "btn_ask_rid":
        context.user_data["awaiting_rid"] = True
        out = (
            "◈ ──────────── ◈\n"
            "        𝖤𝖭𝖳𝖤𝖱 𝖱𝖠𝖭𝖦𝖤 𝖣𝖨𝖦𝖨𝖳𝖲        \n"
            "◈ ──────────── ◈\n\n"
            "⟡ Example: `2992`\n"
            "◈ 𝖲𝖳𝖠𝖳𝖴𝖲 : ᯤ̸ Awaiting RID...\n\n"
            "✦ नीचे चैट में रेंज नंबर टाइप करके भेजें।"
        )
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("─ 𝖢𝖠𝖭𝖢𝖤𝖫 ─", callback_data="btn_home")]
        ])
        await query.edit_message_text(out, reply_markup=btn, parse_mode="Markdown")

    # 2. CHECK OTP
    elif data == "btn_check_otp":
        url = f"{API_BASE_URL}/success-otp"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=HEADERS) as resp:
                    res_raw = await resp.text()
                    try:
                        res_json = json.loads(res_raw)
                        data_block = res_json.get("data", {})
                        if isinstance(data_block, dict):
                            otp_code = data_block.get("otp") or data_block.get("code") or "No OTP yet"
                        else:
                            otp_code = res_raw
                    except Exception:
                        otp_code = res_raw

                    out = (
                        "◈ ──────────── ◈\n"
                        "          𝖮𝖳𝖯 𝖱𝖤𝖢𝖤𝖨𝖵𝖤𝖣          \n"
                        "◈ ──────────── ◈\n\n"
                        f"```\n{otp_code}\n```\n\n"
                        "◈ 𝖲𝖳𝖠𝖳𝖴𝖲 : ᯤ̸ Delivered"
                    )
            except Exception as e:
                out = f"◈ ERROR: {str(e)}"

        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("▣ 𝖱𝖤𝖢𝖧𝖤𝖢𝖪 𝖮𝖳𝖯 ▣", callback_data="btn_check_otp")],
            [InlineKeyboardButton("◈ 𝖭𝖤𝖶 𝖭𝖴𝖬𝖡𝖤𝖱", callback_data="btn_ask_rid")],
            [InlineKeyboardButton("─ 𝖬𝖠𝖨𝖭 𝖬𝖤𝖭𝖴 ─", callback_data="btn_home")]
        ])
        await query.edit_message_text(out, reply_markup=btn, parse_mode="Markdown")

    # 3. CONSOLE LOGS (Telegram 4096-char safe parser)
    elif data == "btn_console_logs":
        url = f"{API_BASE_URL}/console"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=HEADERS) as resp:
                    res_raw = await resp.text()
                    try:
                        res_json = json.loads(res_raw)
                        data_items = res_json.get("data", [])

                        # Log format clean banaya taaki clutter na ho
                        if isinstance(data_items, list) and len(data_items) > 0:
                            parsed_lines = []
                            for item in data_items[:12]:  # Last 12 records
                                num = item.get("number") or item.get("phone") or "N/A"
                                otp = item.get("otp") or item.get("code") or "N/A"
                                parsed_lines.append(f"{num} -> {otp}")
                            formatted_logs = "\n".join(parsed_lines)
                        else:
                            formatted_logs = json.dumps(res_json, indent=2)
                    except Exception:
                        formatted_logs = res_raw

                    if len(formatted_logs) > 3000:
                        formatted_logs = formatted_logs[:3000] + "\n...[TRUNCATED]"

                    out = (
                        "◈ ──────────── ◈\n"
                        "        𝖢𝖮𝖭𝖲𝖮𝖫𝖤 𝖧𝖨𝖲𝖳𝖮𝖱𝖸        \n"
                        "◈ ──────────── ◈\n\n"
                        f"```\n{formatted_logs}\n```"
                    )
            except Exception as e:
                out = (
                    "◈ ──────────── ◈\n"
                    f"◈ ᯤ̸ 𝖤𝖱𝖱𝖮𝖱: {str(e)}\n"
                    "◈ ──────────── ◈"
                )

        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("ᯤ̸ 𝖱𝖤𝖥𝖱𝖤𝖲𝖧 𝖫𝖮𝖦𝖲", callback_data="btn_console_logs")],
            [InlineKeyboardButton("─ 𝖡𝖠𝖢𝖪 𝖳𝖮 𝖬𝖤𝖭𝖴 ─", callback_data="btn_home")]
        ])
        await query.edit_message_text(out, reply_markup=btn, parse_mode="Markdown")

    # 4. LIVE SERVER STATUS
    elif data == "btn_live_status":
        url = f"{API_BASE_URL}/liveaccess"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=HEADERS) as resp:
                    res_raw = await resp.text()
                    if len(res_raw) > 3000:
                        res_raw = res_raw[:3000] + "\n...[TRUNCATED]"
                    out = (
                        "◈ ──────────── ◈\n"
                        "         𝖲𝖤𝖱𝖵𝖤𝖱 𝖲𝖳𝖠𝖳𝖴𝖲          \n"
                        "◈ ──────────── ◈\n\n"
                        f"```\n{res_raw}\n```"
                    )
            except Exception as e:
                out = f"◈ ERROR: {str(e)}"

        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("─ 𝖡𝖠𝖢𝖪 𝖳𝖮 𝖬𝖤𝖭𝖴 ─", callback_data="btn_home")]
        ])
        await query.edit_message_text(out, reply_markup=btn, parse_mode="Markdown")

    # 5. ADMIN CONTROL PANEL
    elif data == "btn_admin_panel":
        if user_id != ADMIN_ID:
            await query.answer("Access Denied!", show_alert=True)
            return

        total_users = len(load_users())
        out = (
            "◈ ──────────── ◈\n"
            "       ⚙ 𝖠𝖣𝖬𝖨𝖭 𝖢𝖮𝖭𝖳𝖱𝖮𝖫 ⚙       \n"
            "◈ ──────────── ◈\n\n"
            f"◈ 𝖳𝖮𝖳𝖠𝖫 𝖴𝖲𝖤𝖱𝖲 : `{total_users}`\n"
            "◈ 𝖡𝖱𝖮𝖠𝖣𝖢𝖠𝖲𝖳   : Inline Buttons Support\n\n"
            "✦ Select an administrative action:"
        )
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 𝖡𝖱𝖮𝖠𝖣𝖢𝖠𝖲𝖳 𝖬𝖤𝖲𝖲𝖠𝖦𝖤", callback_data="btn_ask_broadcast")],
            [InlineKeyboardButton("─ 𝖡𝖠𝖢𝖪 𝖳𝖮 𝖬𝖤𝖭𝖴 ─", callback_data="btn_home")]
        ])
        await query.edit_message_text(out, reply_markup=btn, parse_mode="Markdown")

    # 6. ASK BROADCAST MESSAGE
    elif data == "btn_ask_broadcast":
        if user_id != ADMIN_ID:
            return
        context.user_data["awaiting_broadcast"] = True
        out = (
            "◈ ──────────── ◈\n"
            "      📢 𝖲𝖤𝖭𝖣 𝖡𝖱𝖮𝖠𝖣𝖢𝖠𝖲𝖳       \n"
            "◈ ──────────── ◈\n\n"
            "Neeche diye gaye formats me message send karein:\n\n"
            "1️⃣ *Simple Message:*\n"
            "`Hello everyone, service is live!`\n\n"
            "2️⃣ *Message with 1 Button:*\n"
            "`Join Channel\nBUTTON: Click Here | https://t.me/yourchannel`\n\n"
            "3️⃣ *Message with Multiple Buttons:*\n"
            "`Check updates\nBUTTON: Updates | https://t.me/link1\nBUTTON: Support | https://t.me/link2`"
        )
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("─ 𝖢𝖠𝖭𝖢𝖤𝖫 ─", callback_data="btn_admin_panel")]
        ])
        await query.edit_message_text(out, reply_markup=btn, parse_mode="Markdown")

    # 7. MAIN MENU ROUTE
    elif data == "btn_home":
        context.user_data.clear()
        is_admin = (user_id == ADMIN_ID)
        text, markup = main_dashboard(is_admin=is_admin)
        await query.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")

# ----------------- टेक्स्ट इनपुट हैंडलर -----------------
async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    raw_text = update.message.text.strip()

    # ADMIN BROADCAST PROCESSOR
    if context.user_data.get("awaiting_broadcast") and user_id == ADMIN_ID:
        context.user_data["awaiting_broadcast"] = False
        users = load_users()

        lines = raw_text.split("\n")
        msg_lines = []
        keyboard = []

        for line in lines:
            if line.startswith("BUTTON:"):
                # Format: BUTTON: Label | URL
                parts = line.replace("BUTTON:", "").split("|")
                if len(parts) == 2:
                    lbl = parts[0].strip()
                    url = parts[1].strip()
                    keyboard.append([InlineKeyboardButton(lbl, url=url)])
            else:
                msg_lines.append(line)

        broadcast_msg = "\n".join(msg_lines).strip()
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

        sent_count = 0
        fail_count = 0

        status_msg = await update.message.reply_text("◈ ᯤ̸ Broadcasting in progress...")

        for uid in users:
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=broadcast_msg,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
                sent_count += 1
            except Exception:
                fail_count += 1

        out = (
            "◈ ──────────── ◈\n"
            "     📢 𝖡𝖱𝖮𝖠𝖣𝖢𝖠𝖲𝖳 𝖲𝖴𝖬𝖬𝖠𝖱𝖸     \n"
            "◈ ──────────── ◈\n\n"
            f"◈ 𝖲𝖴𝖢𝖢𝖤𝖲𝖲 : `{sent_count}`\n"
            f"◈ 𝖥𝖠𝖨𝖫𝖤𝖣   : `{fail_count}`\n"
            f"◈ 𝖳𝖮𝖳𝖠𝖫    : `{len(users)}`"
        )
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚙ 𝖡𝖠𝖢𝖪 𝖳𝖮 𝖠𝖣𝖬𝖨𝖭 ⚙", callback_data="btn_admin_panel")]
        ])
        await status_msg.edit_text(out, reply_markup=btn, parse_mode="Markdown")
        return

    # USER RID NUMBER ALLOCATION
    if context.user_data.get("awaiting_rid"):
        rid_input = raw_text
        context.user_data["awaiting_rid"] = False

        wait_msg = await update.message.reply_text(
            "◈ ──────────── ◈\n"
            f"◈ ᯤ̸ 𝖥𝖤𝖳𝖢𝖧𝖨𝖭𝖦 𝖭𝖴𝖬𝖡𝖤𝖱 𝖥𝖮𝖱: `{rid_input}`...\n"
            "◈ ──────────── ◈",
            parse_mode="Markdown"
        )

        url = f"{API_BASE_URL}/getnum"
        payload = {"rid": rid_input}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=HEADERS, json=payload) as resp:
                    res_raw = await resp.text()
                    res_json = json.loads(res_raw)

                    meta = res_json.get("meta", {})
                    code = meta.get("code")

                    if code == 200 and res_json.get("data"):
                        data_block = res_json.get("data", {})
                        number = data_block.get("full_number") or data_block.get("no_plus_number")
                        country = data_block.get("country", "Unknown")
                        operator = data_block.get("operator", "Default")

                        out = (
                            "◈ ──────────── ◈\n"
                            "        𝖭𝖴𝖬𝖡𝖤𝖱 𝖠𝖫𝖫𝖮𝖢𝖠𝖳𝖤𝖣        \n"
                            "◈ ──────────── ◈\n"
                            f"```\n{number}\n```\n"
                            f"◈ 𝖢𝖮𝖴𝖭𝖳𝖱𝖸   : {country}\n"
                            f"◈ 𝖮𝖯𝖤𝖱𝖠𝖳𝖮𝖱  : {operator}\n"
                            f"◈ 𝖱𝖨𝖣       : `{rid_input}`\n"
                            "◈ 𝖲𝖳𝖠𝖳𝖴𝖲    : ᯤ̸ 𝖫𝗂𝗌𝗍𝖾𝗇𝗂𝗇𝗀 𝖿𝗈𝗋 𝖲𝖬𝖲"
                        )
                        btn = InlineKeyboardMarkup([
                            [InlineKeyboardButton("▣ 𝖦𝖤𝖳 𝖮𝖳𝖯 ▣", callback_data="btn_check_otp")],
                            [InlineKeyboardButton("◈ 𝖭𝖤𝖶 𝖭𝖴𝖬𝖡𝖤𝖱", callback_data="btn_ask_rid")],
                            [InlineKeyboardButton("─ 𝖬𝖠𝖨𝖭 𝖬𝖤𝖭𝖴 ─", callback_data="btn_home")]
                        ])
                    else:
                        err_msg = res_json.get("message", "No numbers available in this range.")
                        out = (
                            "◈ ──────────── ◈\n"
                            "        𝖭𝖮 𝖭𝖴𝖬𝖡𝖤𝖱 𝖠𝖵𝖠𝖨𝖫𝖠𝖡𝖫𝖤        \n"
                            "◈ ──────────── ◈\n\n"
                            f"```\n{err_msg}\n```\n\n"
                            f"◈ 𝖱𝖨𝖣 𝖴𝖲𝖤𝖣  : `{rid_input}`\n"
                            "◈ 𝖲𝖳𝖠𝖳𝖴𝖲    : ᯤ̸ Please try another range."
                        )
                        btn = InlineKeyboardMarkup([
                            [InlineKeyboardButton("◈ 𝖳𝖱𝖸 𝖠𝖭𝖮𝖳𝖧𝖤𝖱 𝖱𝖠𝖭𝖦𝖤", callback_data="btn_ask_rid")],
                            [InlineKeyboardButton("─ 𝖬𝖠𝖨𝖭 𝖬𝖤𝖭𝖴 ─", callback_data="btn_home")]
                        ])

            except Exception as e:
                out = (
                    "◈ ──────────── ◈\n"
                    f"◈ ᯤ̸ 𝖤𝖱𝖱𝖮𝖱:\n```\n{str(e)}\n```\n"
                    "◈ ──────────── ◈"
                )
                btn = InlineKeyboardMarkup([
                    [InlineKeyboardButton("◈ 𝖱𝖤𝖳𝖱𝖸", callback_data="btn_ask_rid")],
                    [InlineKeyboardButton("─ 𝖬𝖠𝖨𝖭 𝖬𝖤𝖭𝖴 ─", callback_data="btn_home")]
                ])

        await wait_msg.edit_text(out, reply_markup=btn, parse_mode="Markdown")

# ----------------- मेन रनर -----------------
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_input))
    
    print("◈ 𝖡𝖮𝖳 𝖮𝖭𝖫𝖨𝖭𝖤 ᯤ̸")
    app.run_polling()

if __name__ == "__main__":
    main()
