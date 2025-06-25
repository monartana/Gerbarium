import requests
from . import keys

class Weather:
    def __init__(self):
        # Initialize weather attributes
        self.forecast_value = None
        self.condition_code = None
        self.temperature_value = 0
        self.feels_like = 0
        self.humidity_value = 0
        self.wind_speed = 0
        self.pressure_value = 0
        
    def check_for_rain(self):
        """Get current weather data and check for rain."""
        # Request weather data from OpenWeather API
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params=keys.weather_parameters
        )
        
        # Return False if request failed
        if response.status_code != 200:
            print("❌ Error getting weather data:", response.json())
            return False
            
        # Parse weather data
        data = response.json()
        weather_data = data["list"][0]
        
        # Update weather attributes
        self.condition_code = weather_data["weather"][0]["id"]
        self.forecast_value = weather_data["weather"][0]["description"].title()
        self.temperature_value = round(weather_data["main"]["temp"])
        self.feels_like = round(weather_data["main"]["feels_like"])
        self.humidity_value = round(weather_data["main"]["humidity"])
        self.wind_speed = round(weather_data["wind"]["speed"], 1)
        self.pressure_value = round(weather_data["main"]["pressure"])
        
        # Return True if rain is expected (condition codes below 600 indicate rain)
        return self.condition_code < 600 