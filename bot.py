import os
import logging
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get token from environment variable (NEVER hardcode tokens!)
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# ==================== COMMAND HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with interactive buttons"""
    user = update.effective_user
    
    keyboard = [
        [
            InlineKeyboardButton("🎲 Roll Dice", callback_data='dice'),
            InlineKeyboardButton("📊 Stats", callback_data='stats')
        ],
        [
            InlineKeyboardButton("🌐 Website", url='https://example.com'),
            InlineKeyboardButton("📢 Channel", url='https://t.me/channel')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""
🤖 <b>Welcome, {user.first_name}!</b>

I'm personal assistant to bossdestiny 🔥.

<b>Available Commands:</b>
/start - Show this menu
/help - Get assistance
/echo <text> - Repeat your message
/joke - Random joke
/time - Current time
/caps <text> - SHOUT YOUR TEXT
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help information"""
    help_text = """
🆘 <b>Bot Help Center</b>

<b>Basic Commands:</b>
/start - Start the bot
/help - Show this help message
/echo - Repeat what you say
/time - Show current time

<b>Fun Commands:</b>
/joke - Get a random joke
/roll - Roll a dice (1-6)
/flip - Flip a coin
/caps - Convert text to uppercase

<b>Interactive Features:</b>
• Send any photo - I'll analyze it
• Send location - I'll show coordinates
• Send sticker - I'll echo it back

<b>Need more help?</b> Contact @admin
    """
    await update.message.reply_text(help_text, parse_mode='HTML')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo user message"""
    if context.args:
        text = ' '.join(context.args)
        await update.message.reply_text(f"📢 You said:\n\n<i>{text}</i>", parse_mode='HTML')
    else:
        await update.message.reply_text("Usage: /echo <your message>")

async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convert text to uppercase"""
    if context.args:
        text = ' '.join(context.args).upper()
        await update.message.reply_text(f"🔊 {text}")
    else:
        await update.message.reply_text("Usage: /caps <text to shout>")

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current time"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await update.message.reply_text(f"🕐 Current time:\n<code>{now}</code>", parse_mode='HTML')

async def roll_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Roll a dice"""
    result = random.randint(1, 6)
    dice_emojis = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
    await update.message.reply_text(f"🎲 You rolled: {dice_emojis[result-1]} <b>{result}</b>", parse_mode='HTML')

async def flip_coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Flip a coin"""
    result = random.choice(["Heads", "Tails"])
    emoji = "👑" if result == "Heads" else "🪙"
    await update.message.reply_text(f"{emoji} <b>{result}</b>!", parse_mode='HTML')

async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send random joke"""
    jokes = [
        "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
        "Why did the developer go broke? Because he used up all his cache! 💸",
        "How many programmers does it take to change a light bulb? None, that's a hardware problem! 💡",
        "Why do Java developers wear glasses? Because they don't C#! 👓",
        "What's a computer's favorite snack? Microchips! 🍟"
    ]
    await update.message.reply_text(random.choice(jokes))

# ==================== MESSAGE HANDLERS ====================

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    text = update.message.text
    
    # Simple keyword responses
    if any(word in text.lower() for word in ['hello', 'hi', 'hey']):
        await update.message.reply_text(f"👋 Hello {update.effective_user.first_name}!")
    elif 'thank' in text.lower():
        await update.message.reply_text("🙏 You're welcome!")
    else:
        # Echo with formatting
        await update.message.reply_text(
            f"You sent: <code>{text}</code>\n\nTry /help for commands!",
            parse_mode='HTML'
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photos"""
    photo = update.message.photo[-1]  # Get highest resolution
    await update.message.reply_text(
        f"📸 Nice photo!\n"
        f"Resolution: {photo.width}x{photo.height}\n"
        f"File size: {photo.file_size} bytes"
    )

async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo stickers back"""
    await update.message.reply_sticker(update.message.sticker.file_id)

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle location sharing"""
    loc = update.message.location
    await update.message.reply_text(
        f"📍 Location received!\n"
        f"Latitude: <code>{loc.latitude}</code>\n"
        f"Longitude: <code>{loc.longitude}</code>\n\n"
        f"<a href='https://www.google.com/maps?q={loc.latitude},{loc.longitude}'>View on Google Maps</a>",
        parse_mode='HTML',
        disable_web_page_preview=True
    )

# ==================== CALLBACK HANDLERS ====================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'dice':
        result = random.randint(1, 6)
        await query.edit_message_text(
            f"🎲 You rolled: <b>{result}</b>",
            parse_mode='HTML'
        )
    elif query.data == 'stats':
        user = query.from_user
        stats_text = f"""
📊 <b>Your Stats</b>

👤 Name: {user.first_name}
🆔 ID: <code>{user.id}</code>
📛 Username: @{user.username if user.username else 'N/A'}
🌐 Language: {user.language_code}
        """
        await query.edit_message_text(stats_text, parse_mode='HTML')

# ==================== ERROR HANDLER ====================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ An error occurred. Please try again later."
        )

# ==================== MAIN FUNCTION ====================

def main():
    if not TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set!")
        print("Set it with: export TELEGRAM_BOT_TOKEN='your_token_here'")
        return

    # Create application
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("echo", echo))
    application.add_handler(CommandHandler("caps", caps))
    application.add_handler(CommandHandler("time", time_command))
    application.add_handler(CommandHandler("roll", roll_dice))
    application.add_handler(CommandHandler("flip", flip_coin))
    application.add_handler(CommandHandler("joke", joke))

    # Add message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))

    # Add callback handler
    application.add_handler(CallbackQueryHandler(button_callback))

    # Add error handler
    application.add_error_handler(error_handler)

    # Start the bot
    print("🤖 Bot is running... Press Ctrl+C to stop")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
