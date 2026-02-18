import os
import logging
import random
from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
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

# ==================== LOGGING ====================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("telegram-bot")

# ==================== ENV ====================

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ==================== COMMAND HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.effective_message

    keyboard = [
        [
            InlineKeyboardButton("🎲 Roll Dice", callback_data="dice"),
            InlineKeyboardButton("📊 Stats", callback_data="stats"),
        ],
        [
            InlineKeyboardButton("🌐 Website", url="https://example.com"),
            InlineKeyboardButton("📢 Channel", url="https://t.me/channel"),
        ],
    ]

    text = (
        f"🤖 <b>Welcome, {user.first_name}!</b>\n\n"
        "I'm a feature-rich Telegram bot built with Python.\n\n"
        "<b>Commands</b>\n"
        "/start – Menu\n"
        "/help – Help\n"
        "/echo <text>\n"
        "/joke\n"
        "/time\n"
        "/caps <text>\n"
    )

    await msg.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "🆘 <b>Help Center</b>\n\n"
        "<b>Basic</b>\n"
        "/start /help /time /echo\n\n"
        "<b>Fun</b>\n"
        "/joke /roll /flip /caps\n"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not context.args:
        await msg.reply_text("Usage: /echo <text>")
        return
    await msg.reply_text(f"📢 <i>{' '.join(context.args)}</i>")

async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not context.args:
        await msg.reply_text("Usage: /caps <text>")
        return
    await msg.reply_text(f"🔊 {' '.join(context.args).upper()}")

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    await update.effective_message.reply_text(f"🕐 <code>{now}</code>")

async def roll_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        f"🎲 <b>{random.randint(1, 6)}</b>"
    )

async def flip_coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        f"🪙 <b>{random.choice(['Heads', 'Tails'])}</b>"
    )

async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jokes = [
        "Why do programmers hate nature? Too many bugs 🐛",
        "It works on my machine 🤡",
        "Cache cleared. Brain not found 💀",
    ]
    await update.effective_message.reply_text(random.choice(jokes))

# ==================== MESSAGE HANDLERS ====================

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.effective_message.text.lower()
    user = update.effective_user.first_name

    if any(w in text for w in ("hi", "hello", "hey")):
        await update.effective_message.reply_text(f"👋 Hello {user}")
    else:
        await update.effective_message.reply_text(
            f"You said:\n<code>{update.effective_message.text}</code>"
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.effective_message.photo[-1]
    await update.effective_message.reply_text(
        f"📸 {photo.width}x{photo.height} | {photo.file_size} bytes"
    )

async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_sticker(
        update.effective_message.sticker.file_id
    )

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.effective_message.location
    await update.effective_message.reply_text(
        f"📍 <code>{loc.latitude}, {loc.longitude}</code>\n"
        f"<a href='https://maps.google.com/?q={loc.latitude},{loc.longitude}'>Open Map</a>",
        disable_web_page_preview=True,
    )

# ==================== CALLBACK HANDLER ====================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "dice":
        await query.message.reply_text(f"🎲 {random.randint(1, 6)}")
    elif query.data == "stats":
        u = query.from_user
        await query.message.reply_text(
            f"📊 <b>Your Stats</b>\n\n"
            f"👤 {u.first_name}\n"
            f"🆔 <code>{u.id}</code>\n"
            f"📛 @{u.username or 'N/A'}"
        )

# ==================== ERROR HANDLER ====================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.exception("Unhandled error", exc_info=context.error)

# ==================== MAIN ====================

def main():
    if not TOKEN:
        logger.critical("❌ TELEGRAM_BOT_TOKEN not set")
        raise SystemExit(1)

    defaults = Defaults(parse_mode=ParseMode.HTML)

    app = (
        Application.builder()
        .token(TOKEN)
        .defaults(defaults)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("echo", echo))
    app.add_handler(CommandHandler("caps", caps))
    app.add_handler(CommandHandler("time", time_command))
    app.add_handler(CommandHandler("roll", roll_dice))
    app.add_handler(CommandHandler("flip", flip_coin))
    app.add_handler(CommandHandler("joke", joke))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(CallbackQueryHandler(button_callback))

    app.add_error_handler(error_handler)

    logger.info("🤖 Bot started successfully (Render-ready)")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
