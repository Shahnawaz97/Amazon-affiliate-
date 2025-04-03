import os
import logging
import threading
from app import app
from config import WEBHOOK_ENABLED, PORT
from bot import run_polling_bot

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # If not in webhook mode, start the polling bot in a separate thread
    if not WEBHOOK_ENABLED:
        logger.info("Starting polling bot in background thread")
        bot_thread = threading.Thread(target=run_polling_bot)
        bot_thread.daemon = True
        bot_thread.start()
    
    # Start the Flask web server
    logger.info(f"Starting Flask server on port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
