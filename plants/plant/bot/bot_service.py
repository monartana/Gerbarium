from typing import Dict, Optional
import requests
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Depends

from ..recommendation import PlantRecommendationService
from ..model import Plant
from ..schema import PlantRead
from favorite.model import Favorite
from user.model import User
from database import get_db
from . import keys
from .weather import Weather
from plant.model import TemperaturePreference, Location, WaterNeeds, HumidityNeeds, LightNeeds

logger = logging.getLogger(__name__)

class PlantBotService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.weather = Weather()
        self.recommendation_service = PlantRecommendationService(db)
        
        # Verify API keys are set
        if not keys.token or not keys.url:
            logger.error("UltraMsg API keys are not properly configured")
            raise ValueError("UltraMsg API keys are not properly configured")

    def _get_greeting(self):
        current_hour = datetime.now().hour
        if 5 <= current_hour < 12:
            return "Good morning 🌅"
        elif 12 <= current_hour < 18:
            return "Good afternoon ☀️"
        else:
            return "Good evening 🌙"

    def send_message(self, phone_number: str, message: str):
        """Send WhatsApp message using UltraMsg API."""
        try:
            logger.info(f"Attempting to send message to {phone_number}")
            
            # Format phone number (remove any spaces or special characters)
            phone_number = ''.join(filter(str.isdigit, phone_number))
            
            # Add country code if not present
            if not phone_number.startswith('+'):
                phone_number = f"+{phone_number}"
            
            payload = f"token={keys.token}&to={phone_number}&body={message}"
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            payload = payload.encode('utf8')
            
            logger.info(f"Sending request to UltraMsg API: {keys.url}")
            response = requests.post(keys.url, data=payload, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
                raise Exception(f"Failed to send message: {response.text}")
                
            logger.info(f"Successfully sent message to {phone_number}")
            
        except Exception as e:
            logger.error(f"Error sending message to {phone_number}: {str(e)}", exc_info=True)
            raise

    def send_plant_recommendations(self, phone_number: str):
        """Send personalized plant recommendations to user."""
        # Get user by phone number
        user = self.db.query(User).filter(User.phone_number == phone_number).first()
        if not user:
            self.send_message(phone_number, "Please register with your phone number to get personalized recommendations.")
            return

        # Get user's favorite plants
        favorites = self.db.query(Favorite).filter(Favorite.user_id == user.id).all()
        if not favorites:
            self.send_message(phone_number, "You don't have any favorite plants yet. Add some to get personalized recommendations!")
            return

        # Get weather info
        self.weather.check_for_rain()
        weather_info = (
            f"🌤 Weather: {self.weather.forecast_value}\n"
            f"🌡 Temperature: {self.weather.temperature_value}°C (Feels like {self.weather.feels_like}°C)\n"
            f"💧 Humidity: {self.weather.humidity_value}%\n"
            f"💨 Wind Speed: {self.weather.wind_speed} m/s\n"
        )

        # Get plant care recommendations
        recommendations = []
        for favorite in favorites:
            plant = self.db.query(Plant).filter(Plant.id == favorite.plant_id).first()
            if not plant:
                continue
                
            care_tip = self._get_plant_care_tip(plant)
            recommendations.append(f"🌿 {plant.name}: {care_tip}")

        # Send message
        message = (
            f"*{self._get_greeting()}*\n\n"
            f"{weather_info}\n"
            "Today's care tips for your favorite plants:\n\n" +
            "\n".join(recommendations)
        )
        
        self.send_message(phone_number, message)

    def _get_plant_care_tip(self, plant: Plant) -> str:
        """Generate a care tip based on structured plant attributes and weather conditions."""
        is_rainy = self.weather.condition_code < 600
        temp = self.weather.temperature_value
        humidity = self.weather.humidity_value
        
        tips = []
        
        # Temperature-based tips
        if plant.temperature_preference == TemperaturePreference.COLD and temp > 20:
            tips.append(f"Move {plant.name} to a cooler spot, it prefers temperatures below 15°C")
        elif plant.temperature_preference == TemperaturePreference.WARM and temp < 15:
            tips.append(f"Consider moving {plant.name} to a warmer location, it prefers temperatures above 25°C")
            
        # Water needs based on rain and plant preferences
        if is_rainy:
            if plant.location == Location.OUTDOOR:
                if plant.water_needs == WaterNeeds.LOW:
                    tips.append(f"Protect {plant.name} from rain, it prefers dry conditions")
                elif plant.water_needs == WaterNeeds.HIGH:
                    tips.append(f"Natural rain is great for {plant.name}, but check drainage")
            elif plant.location == Location.INDOOR:
                if plant.water_needs == WaterNeeds.LOW:
                    tips.append(f"Keep {plant.name} on the dry side today")
                elif plant.water_needs == WaterNeeds.HIGH:
                    tips.append(f"Despite the rain, indoor {plant.name} may still need watering")
        
        # Humidity needs
        if plant.humidity_needs == HumidityNeeds.HIGH and humidity < 40:
            tips.append(f"Increase humidity around {plant.name} with misting or a humidity tray")
        elif plant.humidity_needs == HumidityNeeds.LOW and humidity > 70:
            tips.append(f"Ensure good air circulation around {plant.name} to prevent moisture issues")
            
        # Light needs based on weather
        if self.weather.forecast_value.lower().startswith("clear"):
            if plant.light_needs == LightNeeds.LOW:
                tips.append(f"Protect {plant.name} from direct sunlight today")
            elif plant.light_needs == LightNeeds.HIGH and temp < 30:
                tips.append(f"Great day to give {plant.name} some direct sunlight")
                
        # Fallback tips based on basic needs
        if not tips:
            if plant.water_needs == WaterNeeds.HIGH:
                tips.append(f"Check if {plant.name} needs watering, it likes consistent moisture")
            elif plant.water_needs == WaterNeeds.LOW:
                tips.append(f"Be careful not to overwater {plant.name}")
            else:
                tips.append(f"Check {plant.name}'s soil moisture - water if top layer is dry")
        
        return tips[0] if tips else "No specific care tips for today."

def get_bot_service(db: Session = Depends(get_db)) -> PlantBotService:
    return PlantBotService(db) 