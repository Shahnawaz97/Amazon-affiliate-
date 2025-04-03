import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bot configuration
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
if not TELEGRAM_TOKEN:
    logger.error("No Telegram token provided! Set the TELEGRAM_TOKEN environment variable.")

# Amazon affiliate configuration
AFFILIATE_TAG = os.environ.get("AMAZON_AFFILIATE_TAG", "yourtag-20")

# Webhook settings (for production)
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
WEBHOOK_ENABLED = WEBHOOK_URL != ""

# Flask settings
PORT = int(os.environ.get("PORT", 5000))
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
