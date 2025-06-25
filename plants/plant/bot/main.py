import schedule
import time
import logging
from sqlalchemy.orm import Session
from database import SessionLocal
from .bot_service import PlantBotService
from user.model import User

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PlantBot:
    def __init__(self):
        self.db: Session = SessionLocal()
        self.bot_service = PlantBotService(self.db)
        logger.info("PlantBot initialized")
        
    def send_recommendations(self):
        """Send plant care recommendations to all users with phone numbers."""
        logger.info("Starting to send recommendations")
        try:
            # Get all users with phone numbers
            users = self.db.query(User).filter(User.phone_number.isnot(None)).all()
            logger.info(f"Found {len(users)} users with phone numbers")
            
            for user in users:
                logger.info(f"Sending recommendations to user {user.id}")
                self.bot_service.send_plant_recommendations(user.phone_number)
                logger.info(f"Successfully sent recommendations to user {user.id}")
                
        except Exception as e:
            logger.error(f"Error sending recommendations: {e}", exc_info=True)
        
    def run(self):
        """Run the bot with scheduled tasks."""
        logger.info("Setting up scheduled tasks")
        
        # Schedule recommendations
        schedule.every().day.at("08:00").do(self.send_recommendations)
        schedule.every().second.do(self.send_recommendations)
        schedule.every().day.at("14:00").do(self.send_recommendations)
        schedule.every().day.at("20:00").do(self.send_recommendations)
        
        logger.info("✅ Bot started! Waiting for scheduled message times...")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)  # Check every second instead of every minute
            except Exception as e:
                logger.error(f"Error in bot main loop: {e}", exc_info=True)
                time.sleep(60)  # If there's an error, wait a minute before retrying

def run_bot():
    """Run the plant care bot."""
    logger.info("Starting PlantBot")
    bot = PlantBot()
    bot.run()

if __name__ == "__main__":
    run_bot() 
