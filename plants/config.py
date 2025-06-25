import os
from dotenv import load_dotenv

load_dotenv()

HOST = "http://localhost:8000"
UPLOAD_DIR = "uploads"
SQLALCHEMY_DATABASE_URL = "sqlite:///./plants.db"

OPEN_WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
ULTRAMSG_INSTANCE_ID = os.getenv("ULTRAMSG_INSTANCE_ID")
ULTRAMSG_API_KEY = os.getenv("ULTRAMSG_API_KEY")
ULTRAMSG_URL = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"

PLANT_ID_API_KEY = os.getenv("PLANT_ID_API_KEY")
