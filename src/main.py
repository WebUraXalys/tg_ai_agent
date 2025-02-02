import os
from dotenv import load_dotenv
from loguru import logger
from bot import main as run_bot

def setup_logging():
    """Configure logging settings"""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logger.add(
        "logs/app.log",
        level=log_level,
        rotation="500 MB",
        compression="zip"
    )

def main():
    """Main entry point of the application"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Setup logging
        setup_logging()
        logger.info("Starting application...")
        
        # Run the bot
        run_bot()
        
    except Exception as e:
        logger.error(f"Application failed to start: {str(e)}")
        raise

if __name__ == "__main__":
    main() 