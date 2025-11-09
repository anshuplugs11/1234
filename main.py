# ====================== ALIEN X INSTAGRAM RESET BOT - PYTHON 3.13 COMPATIBLE ======================

import requests
import asyncio
import time
import threading
from datetime import datetime
import os
import sys

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)

# Flask imports
from flask import Flask, jsonify

# ================== CONFIG ==================
BOT_TOKEN = "8294042992:AAGkSY7zlyKu5PvaIeCPRsSlznN280Uqmzs"
FLASK_PORT = int(os.environ.get('PORT', 5000))

# Owner IDs
OWNER_IDS = [5316048641, 5819790024]

# FORCE JOIN CHANNELS
FORCE_JOIN_CHANNELS = {
    "@NYROSTOOLSX": "https://t.me/NYROSTOOLSX",
    "@alienbackupx": "https://t.me/alienbackupx",
    "@Alienpaid": "https://t.me/Alienpaid",
    "@paidfilealien": "https://t.me/paidfilealien"
}

# ALLOWED EMAIL DOMAINS
ALLOWED_DOMAINS = ["gmail.com", "hotmail.com", "aol.com"]

URL = "https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/"
HEADERS = {
    "user-agent": "Mozilla/5.0 (Linux; Android 10; M2101K7BG) AppleWebKit/537.36",
    "x-ig-app-id": "1217981644879628",
    "x-csrftoken": "BbJnjd.Jnw20VyXU0qSsHLV",
    "content-type": "application/x-www-form-urlencoded",
    "x-requested-with": "XMLHttpRequest",
}

BROADCAST = 0

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

# ================== /start ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats["active_users"].add(user_id)
    stats["total_users"].add(user_id)
    
    start_msg = (
        "✨**𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗔𝗟𝗜𝗘𝗡 𝗫 𝗣𝗔𝗦𝗦 𝗥𝗘𝗦𝗘𝗧 𝗧𝗢𝗢𝗟**⚡️\n\n"
        "🔥**𝗝𝗢𝗜𝗡 𝗔𝗟𝗟 𝗧𝗛𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟𝗦 𝗔𝗡𝗗 𝗨𝗦𝗘 𝗧𝗛𝗘 𝗕𝗢𝗧**📱\n\n"
        "**🎯 AVAILABLE COMMANDS:**\n\n"
        "📩 `/reset <email>` - Single reset\n"
        "📬 `/bulk` - Bulk reset (1-10 emails)\n"
        "📖 `/help` - Show commands\n\n"
        "**📢 Required Channels:**\n"
    )
    
    for i, (channel, link) in enumerate(FORCE_JOIN_CHANNELS.items(), 1):
        start_msg += f"{i}. {channel}\n"
    
    start_msg += (
        "\n💎 **𝗗𝗘𝗩𝗘𝗟𝗢𝗣𝗘𝗥** - 𝗔𝗟𝗜𝗘𝗡 𝗫👀\n"
        "👾 **𝗢𝗪𝗡𝗘𝗥** - @𝗔𝗟𝗜𝗘𝗡𝗦𝗘𝗫𝗬"
    )
    
    await update.message.reply_text(start_msg, parse_mode='Markdown')

# ================== /help ==================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_msg = (
        "📖 **𝗛𝗘𝗟𝗣 & 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦**\n\n"
        "**👤 USER COMMANDS:**\n\n"
        "📩 `/reset <email>` - Reset single email\n"
        "   Example: `/reset user@gmail.com`\n\n"
        "📬 `/bulk` - Start bulk reset mode\n"
        "   Send 1-10 emails (one per line)\n\n"
        "📖 `/help` - Show this message\n\n"
        "**✅ ALLOWED DOMAINS:**\n"
        "• gmail.com\n"
        "• hotmail.com\n"
        "• aol.com\n\n"
        "💡 **NOTE:** Join all channels to use the bot!"
    )
    
    await update.message.reply_text(help_msg, parse_mode='Markdown')

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

# ================== FORMAT RESULTS ==================
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

# ================== /reset COMMAND ==================
async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    
    # Check if user joined channels
    if not await is_joined(update, context):
        not_joined_msg = (
            "🔒 **𝗙𝗢𝗥𝗖𝗘 𝗝𝗢𝗜𝗡 𝗥𝗘𝗤𝗨𝗜𝗥𝗘𝗗**🔒\n\n"
            f"Join all **{len(FORCE_JOIN_CHANNELS)} channels** first:\n\n"
        )
        for i, (channel, link) in enumerate(FORCE_JOIN_CHANNELS.items(), 1):
            not_joined_msg += f"{i}. {channel}\n   {link}\n\n"
        
        await update.message.reply_text(not_joined_msg, parse_mode='Markdown')
        return
    
    # Check if email provided
    if not context.args:
        await update.message.reply_text(
            "❌ **Usage:** `/reset <email>`\n\n"
            "**Example:** `/reset user@gmail.com`",
            parse_mode='Markdown'
        )
        return
    
    email = context.args[0].strip().lower()
    
    # Validate domain
    domain = email.split("@")[-1] if "@" in email else ""
    if domain not in ALLOWED_DOMAINS:
        await update.message.reply_text(
            f"🚫 **𝗜𝗡𝗩𝗔𝗟𝗜𝗗 𝗗𝗢𝗠𝗔𝗜𝗡:** `{domain}`\n\n"
            f"**Allowed domains:**\n• `gmail.com`\n• `hotmail.com`\n• `aol.com`",
            parse_mode='Markdown'
        )
        return
    
    # Process reset
    msg = await update.message.reply_text("📤 **𝗦𝗘𝗡𝗗𝗜𝗡𝗚 𝗥𝗘𝗤𝗨𝗘𝗦𝗧...**")
    
    success, speed = await send_reset(email)
    add_activity(f"@{username}", email, success)
    
    result = format_single_result(email, success, speed, f"@{username}")
    await msg.edit_text(result, parse_mode='Markdown')

# ================== /bulk COMMAND ==================
async def bulk_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Check if user joined channels
    if not await is_joined(update, context):
        not_joined_msg = (
            "🔒 **𝗙𝗢𝗥𝗖𝗘 𝗝𝗢𝗜𝗡 𝗥𝗘𝗤𝗨𝗜𝗥𝗘𝗗**🔒\n\n"
            f"Join all **{len(FORCE_JOIN_CHANNELS)} channels** first:\n\n"
        )
        for i, (channel, link) in enumerate(FORCE_JOIN_CHANNELS.items(), 1):
            not_joined_msg += f"{i}. {channel}\n   {link}\n\n"
        
        await update.message.reply_text(not_joined_msg, parse_mode='Markdown')
        return ConversationHandler.END
    
    await update.message.reply_text(
        "📬 **𝗕𝗨𝗟𝗞 𝗥𝗘𝗦𝗘𝗧 𝗠𝗢𝗗𝗘**📬\n\n"
        "Send **1–10 emails** (one per line)\n\n"
        "**Allowed domains only:**\n"
        "• `gmail.com`\n"
        "• `hotmail.com`\n"
        "• `aol.com`\n\n"
        "Use /cancel to cancel.",
        parse_mode='Markdown'
    )
    return BROADCAST

async def bulk_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username or "Unknown"
    text = update.message.text.strip()
    emails = [e.strip().lower() for e in text.splitlines() if e.strip()]
    
    if not (1 <= len(emails) <= 10):
        await update.message.reply_text(
            "❌ **𝗜𝗡𝗩𝗔𝗟𝗜𝗗 𝗖𝗢𝗨𝗡𝗧!**\n"
            "Send between 1–10 emails.\n\n"
            "Use /cancel to cancel.",
            parse_mode='Markdown'
        )
        return BROADCAST
    
    # Domain filter
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
            return BROADCAST
    
    # Process bulk
    msg = await update.message.reply_text("📤 **𝗦𝗘𝗡𝗗𝗜𝗡𝗚 𝗥𝗘𝗤𝗨𝗘𝗦𝗧𝗦...**")
    
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
    
    return ConversationHandler.END

# ================== OWNER COMMANDS ==================

async def owner_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """OWNER ONLY - View bot statistics"""
    if not is_owner(update.effective_user.id):
        return
    
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
    if not is_owner(update.effective_user.id):
        return
    
    await update.message.reply_text(
        f"👥 **𝗨𝗦𝗘𝗥 𝗖𝗢𝗨𝗡𝗧**\n\n"
        f"Active Users: `{len(stats['active_users'])}`\n"
        f"Total Users: `{len(stats['total_users'])}`",
        parse_mode='Markdown'
    )

async def owner_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """OWNER ONLY - Manage force join channels"""
    if not is_owner(update.effective_user.id):
        return
    
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
    if not is_owner(update.effective_user.id):
        return
    
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
    
    lines = ["🌐 **𝗔𝗟𝗟𝗢𝗪𝗘𝗗 𝗗𝗢𝗠𝗔𝗜𝗡𝗦**\n"]
    for i, domain in enumerate(ALLOWED_DOMAINS, 1):
        lines.append(f"{i}. `{domain}`")
    
    lines.append("\n\n**Usage:**")
    lines.append("`/domains add yahoo.com`")
    lines.append("`/domains remove yahoo.com`")
    
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')

async def owner_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """OWNER ONLY - View recent activity"""
    if not is_owner(update.effective_user.id):
        return
    
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

async def broadcast_start_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """OWNER ONLY - Start broadcast"""
    if not is_owner(update.effective_user.id):
        return ConversationHandler.END
    
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
    if not is_owner(update.effective_user.id):
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
            await asyncio.sleep(0.05)
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

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel any operation"""
    await update.message.reply_text("❌ Operation cancelled.")
    return ConversationHandler.END

# ================== MAIN - PYTHON 3.13 COMPATIBLE ==================
async def async_main():
    """Async main function"""
    print("🚀 ALIEN X INSTAGRAM RESET BOT STARTING...")
    print(f"📊 Flask Dashboard: http://localhost:{FLASK_PORT}")
    print(f"👑 Owner IDs: {OWNER_IDS}")
    print(f"🐍 Python Version: {sys.version}")
    
    # Start Flask in background
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("✅ Flask server started\n")
    
    # Build application WITHOUT creating event loop issues
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    # User commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("reset", reset_command))
    
    # Bulk reset conversation handler
    bulk_conv = ConversationHandler(
        entry_points=[CommandHandler("bulk", bulk_start)],
        states={
            BROADCAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, bulk_process)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(bulk_conv)
    
    # Owner-only commands (hidden from regular users)
    app.add_handler(CommandHandler("stats", owner_stats))
    app.add_handler(CommandHandler("users", owner_users))
    app.add_handler(CommandHandler("activity", owner_activity))
    app.add_handler(CommandHandler("channels", owner_channels))
    app.add_handler(CommandHandler("domains", owner_domains))
    
    # Broadcast conversation handler (owner only)
    broadcast_conv = ConversationHandler(
        entry_points=[CommandHandler("broadcast", broadcast_start_owner)],
        states={
            BROADCAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(broadcast_conv)
    
    print("="*50)
    print("🎉 BOT IS NOW RUNNING!")
    print("\n👤 USER COMMANDS:")
    print("   /start - Welcome message")
    print("   /help - Show commands")
    print("   /reset <email> - Single reset")
    print("   /bulk - Bulk reset (1-10 emails)")
    print("\n👑 OWNER COMMANDS (Hidden):")
    print("   /stats - View bot statistics")
    print("   /users - View user count")
    print("   /activity - View recent activity")
    print("   /channels - Manage force join channels")
    print("   /domains - Manage allowed domains")
    print("   /broadcast - Send message to all users")
    print("="*50)
    
    # Initialize and run polling
    await app.initialize()
    await app.start()
    await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Shutting down bot...")
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

def main():
    """Main entry point - Python 3.13 compatible"""
    try:
        # Run the async main function
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\n✅ Bot stopped gracefully")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
