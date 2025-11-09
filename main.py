# ====================== ALIEN X INSTAGRAM RESET BOT WITH OWNER COMMANDS ======================

import requests
import asyncio
import nest_asyncio
import time
import threading
from datetime import datetime
import os

nest_asyncio.apply()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, CallbackQueryHandler, ConversationHandler
)

# Flask imports
from flask import Flask, jsonify

# ================== CONFIG ==================
BOT_TOKEN = "8294042992:AAGkSY7zlyKu5PvaIeCPRsSlznN280Uqmzs"
FLASK_PORT = int(os.environ.get('PORT', 5000))

# Owner IDs - Replace with YOUR Telegram user IDs (get from @userinfobot)
OWNER_IDS = [5316048641, 5819790024]  # ⚠️ REPLACE THESE!

# ⚙️ FORCE JOIN CHANNELS - Add/Remove channels as needed
# Format: {"@channel_username": "https://t.me/channel_username"}
FORCE_JOIN_CHANNELS = {
    "@NYROSTOOLSX": "https://t.me/NYROSTOOLSX",
    "@alienbackupx": "https://t.me/alienbackupx",
    "@Alienpaid": "https://t.me/Alienpaid",
    "@paidfilealien": "https://t.me/paidfilealien"
}

# ⚙️ ALLOWED EMAIL DOMAINS - Add/Remove domains as needed
ALLOWED_DOMAINS = ["gmail.com", "hotmail.com", "aol.com"]

URL = "https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/"
HEADERS = {
    "user-agent": "Mozilla/5.0 (Linux; Android 10; M2101K7BG) AppleWebKit/537.36",
    "x-ig-app-id": "1217981644879628",
    "x-csrftoken": "BbJnjd.Jnw20VyXU0qSsHLV",
    "content-type": "application/x-www-form-urlencoded",
    "x-requested-with": "XMLHttpRequest",
}

SINGLE, BULK, BROADCAST = range(3)

# ================== STATS TRACKING ==================
stats = {
    "bot_started": datetime.now().isoformat(),
    "total_requests": 0,
    "successful_resets": 0,
    "failed_resets": 0,
    "active_users": set(),
    "total_users": set(),
    "recent_activity": []
}

def add_activity(user, email, status):
    """Track bot activity"""
    activity = {
        "timestamp": datetime.now().isoformat(),
        "user": user,
        "email": email,
        "status": "success" if status else "failed"
    }
    stats["recent_activity"].insert(0, activity)
    stats["recent_activity"] = stats["recent_activity"][:20]
    
    stats["total_requests"] += 1
    if status:
        stats["successful_resets"] += 1
    else:
        stats["failed_resets"] += 1

def is_owner(user_id):
    """Check if user is owner"""
    return user_id in OWNER_IDS

# ================== FLASK APP ==================
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    """Bot status page"""
    return jsonify({
        "bot": "ALIEN X Instagram Password Reset Bot",
        "status": "online",
        "uptime_since": stats["bot_started"],
        "total_requests": stats["total_requests"],
        "success_rate": f"{(stats['successful_resets'] / max(stats['total_requests'], 1) * 100):.1f}%"
    })

@flask_app.route('/stats')
def get_stats():
    """Get bot statistics"""
    return jsonify({
        "total_requests": stats["total_requests"],
        "successful_resets": stats["successful_resets"],
        "failed_resets": stats["failed_resets"],
        "active_users": len(stats["active_users"]),
        "total_users": len(stats["total_users"]),
        "success_rate": f"{(stats['successful_resets'] / max(stats['total_requests'], 1) * 100):.1f}%",
        "bot_uptime_since": stats["bot_started"]
    })

@flask_app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

@flask_app.route('/activity')
def activity():
    """Recent activity log"""
    return jsonify({"recent_activity": stats["recent_activity"]})

def run_flask():
    """Run Flask in a separate thread"""
    flask_app.run(host='0.0.0.0', port=FLASK_PORT, debug=False, use_reloader=False, threaded=True)

# ================== CHECK JOIN ==================
async def is_joined(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    for channel in FORCE_JOIN_CHANNELS.keys():
        try:
            member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# ================== BUTTONS ==================
def join_buttons():
    keyboard = []
    for i, (channel, link) in enumerate(FORCE_JOIN_CHANNELS.items(), 1):
        keyboard.append([InlineKeyboardButton(f"Channel {i}", url=link)])
    keyboard.append([InlineKeyboardButton("I Joined All", callback_data="joined")])
    return InlineKeyboardMarkup(keyboard)

def mode_buttons():
    keyboard = [
        [InlineKeyboardButton("Single Reset", callback_data="single")],
        [InlineKeyboardButton("Bulk Reset (Max 10)", callback_data="bulk")]
    ]
    return InlineKeyboardMarkup(keyboard)

EPIC_START_MSG = (
    "✨**𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗔𝗟𝗜𝗘𝗡 𝗫 𝗣𝗔𝗦𝗦 𝗥𝗘𝗦𝗘𝗧 𝗧𝗢𝗢𝗟**⚡️\n\n"
    "🔥**𝗝𝗢𝗜𝗡 𝗔𝗟𝗟 𝗧𝗛𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟𝗦 𝗔𝗡𝗗 𝗨𝗦𝗘 𝗧𝗛𝗘 𝗕𝗢𝗧**📱\n\n"
    "𝗝𝗨𝗦𝗧 𝗦𝗘𝗡𝗗 𝗠𝗔𝗜𝗟 ⛔\n\n"
    "𝗗𝗘𝗩𝗘𝗟𝗢𝗣𝗘𝗥 - 𝗔𝗟𝗜𝗘𝗡 𝗫👀\n"
    "𝗢𝗪𝗡𝗘𝗥 - @𝗔𝗟𝗜𝗘𝗡𝗦𝗘𝗫𝗬👾"
)

# ================== /start ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats["active_users"].add(user_id)
    stats["total_users"].add(user_id)
    
    if await is_joined(update, context):
        await update.message.reply_text(
            EPIC_START_MSG, 
            parse_mode='Markdown', 
            reply_markup=mode_buttons()
        )
    else:
        await update.message.reply_text(
            "🔒 **𝗙𝗢𝗥𝗖𝗘 𝗝𝗢𝗜𝗡 𝗥𝗘𝗤𝗨𝗜𝗥𝗘𝗗**🔒\n\n"
            f"Join all **{len(FORCE_JOIN_CHANNELS)} channels** → Click **'𝗜 𝗝𝗢𝗜𝗡𝗘𝗗 𝗔𝗟𝗟'**",
            reply_markup=join_buttons(), 
            parse_mode='Markdown'
        )
    return ConversationHandler.END

# ================== BUTTON HANDLER ==================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "joined":
        if await is_joined(update, context):
            await query.edit_message_text(
                EPIC_START_MSG, 
                parse_mode='Markdown', 
                reply_markup=mode_buttons()
            )
        else:
            await query.answer("❌ **𝗬𝗢𝗨 𝗛𝗔𝗩𝗘𝗡'𝗧 𝗝𝗢𝗜𝗡𝗘𝗗 𝗔𝗟𝗟!**", show_alert=True)

    elif query.data == "single":
        await query.edit_message_text(
            "📩 **𝗦𝗜𝗡𝗚𝗟𝗘 𝗥𝗘𝗦𝗘𝗧 𝗠𝗢𝗗𝗘**📩\n\n"
            "Send **1 email** from:\n"
            "• `gmail.com`\n• `hotmail.com`\n• `aol.com`",
            parse_mode='Markdown'
        )
        return SINGLE

    elif query.data == "bulk":
        await query.edit_message_text(
            "📬 **𝗕𝗨𝗟𝗞 𝗥𝗘𝗦𝗘𝗧 𝗠𝗢𝗗𝗘**📬\n\n"
            "Send **1–10 emails** (one per line)\n\n"
            "Only:\n• `gmail.com`\n• `hotmail.com`\n• `aol.com`",
            parse_mode='Markdown'
        )
        return BULK

    return ConversationHandler.END

# ================== SEND RESET ==================
async def send_reset(email: str) -> tuple[bool, float]:
    start = time.time()
    for _ in range(2):
        try:
            r = requests.post(
                URL, 
                headers=HEADERS, 
                data={"email_or_username": email, "flow": "fxcal"}, 
                timeout=15
            )
            elapsed = time.time() - start
            if r.status_code == 200 and any(k in r.text.lower() for k in ["email_sent", "success", "sent", "link"]):
                return True, round(elapsed, 1)
            await asyncio.sleep(2)
        except:
            await asyncio.sleep(2)
    return False, round(time.time() - start, 1)

# ================== SINGLE RESULT FORMAT ==================
def format_single_result(email: str, success: bool, speed: float, username: str):
    status = "SUCCESS" if success else "FAILED"
    emoji = "✅" if success else "❌"
    return (
        f"· · ─ ·✶· ─ · ·· · ─ ·✶· ─ · ·\n"
        f"[🤖] **𝙋𝙍𝙊𝘾𝙀𝙎𝙎𝙀𝘿 𝘽𝙔 : ALIEN RESET BOT**\n\n"
        f"[🔛] **𝙎𝙏𝘼𝙏𝙐𝙎 : {status} {emoji}**\n"
        f"[👤] **𝙐𝙎𝙀𝙍 : {username}**\n"
        f"[🎯] **𝙏𝘼𝙍𝙂𝙀𝙏 : `{email}`**\n"
        f"[⚙️] **𝘼𝙋𝙄 𝙐𝙎𝙀𝘿 : WEB**\n"
        f"[⚡] **𝙎𝙋𝙀𝙀𝘿 : {speed} seconds**\n"
        f"[🧠] **𝘾𝙍𝙀𝘼𝙏𝙊𝙍 : ALIEN X**\n"
        f"[📰] **𝘼𝘿𝙈𝙄𝙉 : ALIEN X**\n"
        f"· · ─ ·✶· ─ · ·· · ─ ·✶· ─ · ·"
    )

# ================== BULK RESULT FORMAT ==================
def format_bulk_result(results, total_time):
    success_count = sum(1 for r in results if r["status"])
    failed_count = len(results) - success_count

    lines = [
        "✨ **𝗕𝗨𝗟𝗞 𝗥𝗘𝗦𝗘𝗧 𝗥𝗘𝗦𝗨𝗟𝗧** ✨",
        "━━━━━━━━━━━━━━━━━━",
        f"⚡ **Processing Time:** {total_time:.1f} seconds",
        ""
    ]

    for i, res in enumerate(results, 1):
        status = "✅ SUCCESS" if res["status"] else "❌ FAILED"
        lines.append(f"🎯 **Target {i}:** `{res['email']}`")
        lines.append(f"   • Status: {status}")
        lines.append(f"   • API Used: WEB API")
        lines.append("")

    lines += [
        "📊 **Summary**",
        f"   • Successful: {success_count}",
        f"   • Failed: {failed_count}",
        "",
        "🔁 **𝗧𝗥𝗬 𝗔𝗚𝗔𝗜𝗡 𝗜𝗙 𝗬𝗢𝗨 𝗙𝗔𝗖𝗘 𝗔𝗡𝗬 𝗘𝗥𝗥𝗢𝗥**",
        "💎 **𝗣𝗢𝗪𝗘𝗥 𝗕𝗬 𝗔𝗟𝗜𝗘𝗡 𝗫**"
    ]

    return "\n".join(lines)

# ================== PROCESS EMAIL ==================
async def process_email(update: Update, context: ContextTypes.DEFAULT_TYPE, is_bulk: bool):
    if not await is_joined(update, context):
        await update.message.reply_text("🔒 **𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟𝗦!**", reply_markup=join_buttons())
        return ConversationHandler.END

    text = update.message.text.strip()
    emails = [e.strip().lower() for e in text.splitlines() if e.strip()] if is_bulk else [text.lower()]
    username = update.effective_user.username or "Unknown"

    if is_bulk and not (1 <= len(emails) <= 10):
        await update.message.reply_text("❌ **𝗜𝗡𝗩𝗔𝗟𝗜𝗗 𝗖𝗢𝗨𝗡𝗧!**\nUse 1–10 emails.", parse_mode='Markdown')
        return BULK

    # DOMAIN FILTER
    valid_emails = []
    invalid = []
    for email in emails:
        domain = email.split("@")[-1] if "@" in email else ""
        if domain in ALLOWED_DOMAINS:
            valid_emails.append(email)
        else:
            invalid.append(email)

    if invalid:
        await update.message.reply_text(
            f"🚫 **𝗜𝗡𝗩𝗔𝗟𝗜𝗗 𝗗𝗢𝗠𝗔𝗜𝗡𝗦:**\n`{'`, `'.join(invalid)}`\n\n"
            f"**Allowed:** `gmail.com`, `hotmail.com`, `aol.com`",
            parse_mode='Markdown'
        )
        if not valid_emails:
            return BULK if is_bulk else SINGLE

    msg = await update.message.reply_text("📤 **𝗦𝗘𝗡𝗗𝗜𝗡𝗚 𝗥𝗘𝗤𝗨𝗘𝗦𝗧...**")

    if not is_bulk and len(valid_emails) == 1:
        # SINGLE MODE
        email = valid_emails[0]
        success, speed = await send_reset(email)
        add_activity(f"@{username}", email, success)
        result = format_single_result(email, success, speed, f"@{username}")
        await msg.edit_text(result, parse_mode='Markdown')
    else:
        # BULK MODE
        start_time = time.time()
        results = []
        for i, email in enumerate(valid_emails):
            success, _ = await send_reset(email)
            results.append({"email": email, "status": success})
            add_activity(f"@{username}", email, success)
            await asyncio.sleep(2.5)
            if (i + 1) % 3 == 0:
                await msg.edit_text(f"📡 **𝗦𝗘𝗡𝗗𝗜𝗡𝗚... {i+1}/{len(valid_emails)}**")

        total_time = time.time() - start_time
        result = format_bulk_result(results, total_time)
        await msg.edit_text(result, parse_mode='Markdown')

    await update.message.reply_text("Choose mode:", reply_markup=mode_buttons())
    return ConversationHandler.END

# ================== OWNER COMMANDS ==================

async def owner_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """OWNER ONLY - View bot statistics"""
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        return  # Silently ignore if not owner
    
    success_rate = (stats['successful_resets'] / max(stats['total_requests'], 1) * 100)
    stats_msg = (
        "📊 **𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦**\n\n"
        f"📈 Total Requests: `{stats['total_requests']}`\n"
        f"✅ Successful: `{stats['successful_resets']}`\n"
        f"❌ Failed: `{stats['failed_resets']}`\n"
        f"📊 Success Rate: `{success_rate:.1f}%`\n"
        f"👥 Active Users: `{len(stats['active_users'])}`\n"
        f"🌐 Total Users: `{len(stats['total_users'])}`\n"
        f"⏰ Uptime Since: `{stats['bot_started']}`"
    )
    await update.message.reply_text(stats_msg, parse_mode='Markdown')

async def owner_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """OWNER ONLY - View user count"""
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        return  # Silently ignore if not owner
    
    await update.message.reply_text(
        f"👥 **𝗨𝗦𝗘𝗥 𝗖𝗢𝗨𝗡𝗧**\n\n"
        f"Active Users: `{len(stats['active_users'])}`\n"
        f"Total Users: `{len(stats['total_users'])}`",
        parse_mode='Markdown'
    )

async def owner_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """OWNER ONLY - Manage force join channels"""
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        return  # Silently ignore if not owner
    
    # Check if adding/removing channel
    if context.args:
        action = context.args[0].lower()
        
        if action == "add" and len(context.args) >= 3:
            channel_username = context.args[1]
            channel_link = context.args[2]
            
            if not channel_username.startswith("@"):
                await update.message.reply_text("❌ Channel username must start with @")
                return
            
            FORCE_JOIN_CHANNELS[channel_username] = channel_link
            await update.message.reply_text(
                f"✅ Added channel: `{channel_username}`\n"
                f"Link: {channel_link}",
                parse_mode='Markdown'
            )
            return
        
        elif action == "remove" and len(context.args) >= 2:
            channel_username = context.args[1]
            
            if channel_username in FORCE_JOIN_CHANNELS:
                del FORCE_JOIN_CHANNELS[channel_username]
                await update.message.reply_text(f"✅ Removed channel: `{channel_username}`", parse_mode='Markdown')
            else:
                await update.message.reply_text(f"❌ Channel not found: `{channel_username}`", parse_mode='Markdown')
            return
    
    # List all channels
    if not FORCE_JOIN_CHANNELS:
        await update.message.reply_text("📭 No force join channels configured.")
        return
    
    lines = ["📢 **𝗙𝗢𝗥𝗖𝗘 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟𝗦**\n"]
    for i, (channel, link) in enumerate(FORCE_JOIN_CHANNELS.items(), 1):
        lines.append(f"{i}. `{channel}`\n   Link: {link}\n")
    
    lines.append("\n**Usage:**")
    lines.append("`/channels add @username https://t.me/username`")
    lines.append("`/channels remove @username`")
    
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')

async def owner_domains(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """OWNER ONLY - Manage allowed domains"""
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        return  # Silently ignore if not owner
    
    # Check if adding/removing domain
    if context.args:
        action = context.args[0].lower()
        
        if action == "add" and len(context.args) >= 2:
            domain = context.args[1].lower()
            
            if domain not in ALLOWED_DOMAINS:
                ALLOWED_DOMAINS.append(domain)
                await update.message.reply_text(f"✅ Added domain: `{domain}`", parse_mode='Markdown')
            else:
                await update.message.reply_text(f"⚠️ Domain already exists: `{domain}`", parse_mode='Markdown')
            return
        
        elif action == "remove" and len(context.args) >= 2:
            domain = context.args[1].lower()
            
            if domain in ALLOWED_DOMAINS:
                ALLOWED_DOMAINS.remove(domain)
                await update.message.reply_text(f"✅ Removed domain: `{domain}`", parse_mode='Markdown')
            else:
                await update.message.reply_text(f"❌ Domain not found: `{domain}`", parse_mode='Markdown')
            return
    
    # List all domains
    lines = ["🌐 **𝗔𝗟𝗟𝗢𝗪𝗘𝗗 𝗗𝗢𝗠𝗔𝗜𝗡𝗦**\n"]
    for i, domain in enumerate(ALLOWED_DOMAINS, 1):
        lines.append(f"{i}. `{domain}`")
    
    lines.append("\n\n**Usage:**")
    lines.append("`/domains add yahoo.com`")
    lines.append("`/domains remove yahoo.com`")
    
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')

async def owner_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """OWNER ONLY - View recent activity"""
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        return  # Silently ignore if not owner
    
    if not stats["recent_activity"]:
        await update.message.reply_text("📭 No recent activity.")
        return
    
    lines = ["🔔 **𝗥𝗘𝗖𝗘𝗡𝗧 𝗔𝗖𝗧𝗜𝗩𝗜𝗧𝗬** (Last 10)\n"]
    
    for i, activity in enumerate(stats["recent_activity"][:10], 1):
        status_emoji = "✅" if activity["status"] == "success" else "❌"
        lines.append(
            f"{i}. {status_emoji} `{activity['email']}`\n"
            f"   User: {activity['user']}\n"
            f"   Time: {activity['timestamp'][:19]}\n"
        )
    
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')

async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """OWNER ONLY - Start broadcast"""
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        return ConversationHandler.END  # Silently ignore if not owner
    
    await update.message.reply_text(
        "📢 **𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗠𝗢𝗗𝗘**\n\n"
        f"Total Users: `{len(stats['total_users'])}`\n\n"
        "Send your message now.\n"
        "Use /cancel to cancel.",
        parse_mode='Markdown'
    )
    return BROADCAST

async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """OWNER ONLY - Send broadcast to all users"""
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        return ConversationHandler.END
    
    message_text = update.message.text
    total = len(stats["total_users"])
    
    success = 0
    failed = 0
    
    msg = await update.message.reply_text(f"📤 Broadcasting to {total} users...")
    
    for uid in stats["total_users"]:
        try:
            await context.bot.send_message(chat_id=uid, text=message_text, parse_mode='Markdown')
            success += 1
            await asyncio.sleep(0.05)  # Avoid rate limits
        except:
            failed += 1
    
    await msg.edit_text(
        f"✅ **𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘!**\n\n"
        f"✅ Success: {success}\n"
        f"❌ Failed: {failed}\n"
        f"👥 Total: {total}",
        parse_mode='Markdown'
    )
    return ConversationHandler.END

# ================== HANDLERS ==================
async def single_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await process_email(update, context, False)

async def bulk_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await process_email(update, context, True)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel any operation"""
    await update.message.reply_text("❌ Operation cancelled.")
    return ConversationHandler.END

# ================== MAIN ==================
async def main():
    print("🚀 ALIEN X INSTAGRAM RESET BOT STARTING...")
    print(f"📊 Flask Dashboard: http://localhost:{FLASK_PORT}")
    print(f"👑 Owner IDs: {OWNER_IDS}")
    
    # Start Flask in background
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("✅ Flask server started\n")
    
    app = Application.builder().token(BOT_TOKEN).build()

    # Main conversation handler
    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(button)
        ],
        states={
            SINGLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, single_email)],
            BULK: [MessageHandler(filters.TEXT & ~filters.COMMAND, bulk_email)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)
    
    # Owner-only commands (hidden from regular users)
    app.add_handler(CommandHandler("stats", owner_stats))
    app.add_handler(CommandHandler("users", owner_users))
    app.add_handler(CommandHandler("activity", owner_activity))
    app.add_handler(CommandHandler("channels", owner_channels))
    app.add_handler(CommandHandler("domains", owner_domains))
    
    # Broadcast conversation handler (owner only)
    broadcast_conv = ConversationHandler(
        entry_points=[CommandHandler("broadcast", broadcast_start)],
        states={
            BROADCAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(broadcast_conv)
    
    print("="*50)
    print("🎉 BOT IS NOW RUNNING!")
    print("\n👑 OWNER COMMANDS (Hidden):")
    print("   /stats - View bot statistics")
    print("   /users - View user count")
    print("   /activity - View recent activity")
    print("   /channels - Manage force join channels")
    print("   /domains - Manage allowed domains")
    print("   /broadcast - Send message to all users")
    print("="*50)
    
    await app.run_polling()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(main())
        else:
            loop.run_until_complete(main())
    except Exception as e:
        print(f"❌ Error: {e}")
