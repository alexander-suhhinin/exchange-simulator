"""
Main entry point for BingX Emulator
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api.server import api_server
from src.utils.logger import setup_logger

logger = setup_logger('main')

def main():
    """Main function to start the emulator"""
    try:
        logger.info("Starting BingX Emulator...")
        api_server.run()
    except KeyboardInterrupt:
        logger.info("Shutting down BingX Emulator...")
    except Exception as e:
        logger.error(f"Error starting emulator: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()