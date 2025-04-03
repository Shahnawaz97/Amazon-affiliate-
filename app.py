import os
import logging
import threading
from flask import Flask, render_template
from telegram import Bot

from config import TELEGRAM_TOKEN, WEBHOOK_ENABLED, PORT
from bot import run_webhook_bot, run_polling_bot

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", os.urandom(24).hex())

# Create Telegram bot instance
app.bot = Bot(TELEGRAM_TOKEN)

@app.route('/')
def index():
    """Render the main page with bot status and instructions."""
    bot_info = None
    error = None
    
    try:
        # Get bot information
        bot_info = app.bot.get_me()
    except Exception as e:
        error = f"Error connecting to Telegram API: {str(e)}"
        logger.error(error)
    
    return render_template('index.html', 
                          bot_info=bot_info, 
                          error=error, 
                          webhook_mode=WEBHOOK_ENABLED)

# If in webhook mode, configure the webhook routes
if WEBHOOK_ENABLED:
    app = run_webhook_bot(app)
    logger.info("Bot configured in webhook mode")
else:
    # Start the polling bot in a separate thread when not in development mode 
    # (when running with gunicorn, not directly with app.run)
    if not os.environ.get('FLASK_ENV') == 'development':
        logger.info("Starting polling bot in background thread")
        bot_thread = threading.Thread(target=run_polling_bot)
        bot_thread.daemon = True
        bot_thread.start()
    logger.info("Bot will run in polling mode")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
