import logging
from telegram import Update, ParseMode
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters,
    CallbackContext
)

from config import TELEGRAM_TOKEN, WEBHOOK_URL, WEBHOOK_ENABLED, PORT
from link_converter import find_and_convert_amazon_links

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_text(
        f"Hi {user.first_name}! I can convert Amazon product links to affiliate links.\n\n"
        f"Just send me a message containing an Amazon link, and I'll convert it for you.\n\n"
        f"Type /help for more information."
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        "🛍️ *Amazon Affiliate Link Converter* 🛍️\n\n"
        "I can convert regular Amazon product links to affiliate links automatically.\n\n"
        "*How to use me:*\n"
        "1. Simply send me any message containing Amazon product links\n"
        "2. I'll detect all Amazon links and convert them\n"
        "3. Copy and share the converted links\n\n"
        "*Example links I can convert:*\n"
        "• amazon.com/dp/B07PVCVBN7\n"
        "• amazon.com/gp/product/B07PVCVBN7\n"
        "• amazon.co.uk/dp/B07PVCVBN7\n\n"
        "*Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help message",
        parse_mode=ParseMode.MARKDOWN
    )

def process_message(update: Update, context: CallbackContext) -> None:
    """Process messages that might contain Amazon links."""
    if not update.message or not update.message.text:
        return
    
    message_text = update.message.text
    logger.debug(f"Received message: {message_text[:50]}...")
    
    # Find and convert all Amazon links in the message
    original_links, converted_links = find_and_convert_amazon_links(message_text)
    
    # If no Amazon links were found
    if not original_links:
        return
    
    # Prepare the response
    response = "I found and converted these Amazon links for you:\n\n"
    
    for i, (original, converted) in enumerate(zip(original_links, converted_links), 1):
        response += f"*Link {i}:*\n"
        response += f"Original: {original}\n"
        response += f"Affiliate: {converted}\n\n"
    
    update.message.reply_text(
        response,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )

def error_handler(update: Update, context: CallbackContext) -> None:
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        update.effective_message.reply_text(
            "Sorry, something went wrong while processing your message. Please try again later."
        )

def create_bot_updater():
    """Create and configure the bot updater."""
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher
    
    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_message))
    
    # Register error handler
    dispatcher.add_error_handler(error_handler)
    
    return updater

def run_webhook_bot(app):
    """Run the bot in webhook mode integrated with Flask."""
    from telegram.ext import Dispatcher
    from flask import request, Response
    
    bot_dispatcher = Dispatcher(app.bot, None, workers=1)
    
    # Register handlers
    bot_dispatcher.add_handler(CommandHandler("start", start))
    bot_dispatcher.add_handler(CommandHandler("help", help_command))
    bot_dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_message))
    bot_dispatcher.add_error_handler(error_handler)
    
    @app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
    def webhook():
        if request.method == "POST":
            update = Update.de_json(request.get_json(force=True), app.bot)
            bot_dispatcher.process_update(update)
        return Response('ok', status=200)
    
    # Set webhook
    app.bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}")
    logger.info(f"Webhook set to {WEBHOOK_URL}")
    
    return app

def run_polling_bot():
    """Run the bot in polling mode (standalone)."""
    updater = create_bot_updater()
    updater.start_polling()
    logger.info("Bot started in polling mode")
    
    # Don't call idle() when running in a thread (with gunicorn)
    # This helps avoid the "signal only works in main thread" error
    import threading
    if threading.current_thread() is threading.main_thread():
        updater.idle()
    else:
        # Keep the updater running without signal handlers
        import time
        while True:
            try:
                time.sleep(10)
            except:
                # Break on exception (like KeyboardInterrupt)
                break
