import os
import logging
import random
import asyncio
from datetime import datetime
from typing import Optional, Dict
from collections import defaultdict
from time import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    Defaults,
)

# =========================================================
# CONFIGURATION LAYER
# =========================================================

class Config:
    BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    RATE_LIMIT_SECONDS: int = 2

    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN or ":" not in cls.BOT_TOKEN:
            raise RuntimeError("Invalid or missing TELEGRAM_BOT_TOKEN")

Config.validate()

# =========================================================
# LOGGING (Structured)
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("telegram-bot")

# =========================================================
# RATE LIMITING
# =========================================================

_last_action: Dict[int, float] = defaultdict(float)

def is_rate_limited(user_id: int) -> bool:
    now = time()
    if now - _last_action[user_id] < Config.RATE_LIMIT_SECONDS:
        return True
    _last_action[user_id] = now
    return False

# =========================================================
# RESPONSE UTILITY
# =========================================================

async def safe_reply(update: Update, text: str, **kwargs):
    try:
        msg = update.effective_message
        if msg:
            await msg.reply_text(text, **kwargs)
    except Exception as e:
        logger.warning("Reply failed: %s", e)

def user_context(update: Update) -> str:
    user = update.effective_user
    if not user:
        return "unknown"
    return f"user_id={user.id}"

# =========================================================
# BUSINESS LOGIC (Separated)
# =========================================================

def generate_joke() -> str:
    jokes = [
        "Why do programmers hate nature? Too many bugs 🐛",
        "It works on my machine 🤡",
        "Cache cleared. Brain not found 💀",
    ]
    return random.choice(jokes)

def roll() -> int:
    return random.randint(1, 6)

def flip() -> str:
    return random.choice(["Heads", "Tails"])

# =========================================================
# COMMAND HANDLERS
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Start triggered | %s", user_context(update))

    keyboard = [
        [
            InlineKeyboardButton("🎲 Roll Dice", callback_data="dice"),
            InlineKeyboardButton("📊 Stats", callback_data="stats"),
        ]
    ]

    await safe_reply(
        update,
        "🤖 <b>Welcome!</b>\nProduction-level Telegram bot online 🚀",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_reply(update, "Use /start to begin")

async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_rate_limited(update.effective_user.id):
        return
    await safe_reply(update, generate_joke())

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    await safe_reply(update, f"🕒 <code>{now}</code>")

async def roll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_reply(update, f"🎲 <b>{roll()}</b>")

async def flip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_reply(update, f"🪙 <b>{flip()}</b>")

# =========================================================
# CALLBACK HANDLER
# =========================================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    await query.answer()

    try:
        if query.data == "dice":
            await query.message.reply_text(f"🎲 {roll()}")
        elif query.data == "stats":
            u = query.from_user
            await query.message.reply_text(
                f"📊 <b>Your Stats</b>\n\n"
                f"👤 {u.first_name}\n"
                f"🆔 <code>{u.id}</code>"
            )
    except Exception:
        logger.exception("Callback failure")

# =========================================================
# ERROR HANDLER
# =========================================================

async def error_handler(update, context):
    logger.exception("Unhandled exception", exc_info=context.error)

# =========================================================
# MAIN APPLICATION
# =========================================================

def build_application() -> Application:
    defaults = Defaults(parse_mode=ParseMode.HTML)

    app = (
        Application.builder()
        .token(Config.BOT_TOKEN)
        .defaults(defaults)
        .build()
    )

    # Command registry pattern
    commands = {
        "start": start,
        "help": help_command,
        "joke": joke,
        "time": time_command,
        "roll": roll_command,
        "flip": flip_command,
    }

    for name, handler in commands.items():
        app.add_handler(CommandHandler(name, handler))

    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_error_handler(error_handler)

    return app

def main():
    logger.info("Bootstrapping application...")
    app = build_application()
    logger.info("Bot started successfully")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
