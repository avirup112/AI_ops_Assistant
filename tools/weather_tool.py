"""OpenWeather API tool for fetching weather information."""
import os
import requests
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class WeatherTool:
    """Tool for interacting with OpenWeather API."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY environment variable is required")
        
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, city: str, units: str = "metric") -> Dict[str, Any]:
        """
        Get current weather for a city.
        
        Args:
            city: City name
            units: Temperature units (metric, imperial, kelvin)
            
        Returns:
            Dictionary with weather information
        """
        try:
            url = f"{self.base_url}/weather"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": units
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant weather information
            weather_info = {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "description": data["weather"][0]["description"].title(),
                "main": data["weather"][0]["main"],
                "wind_speed": data.get("wind", {}).get("speed", 0),
                "visibility": data.get("visibility", 0) / 1000,  # Convert to km
                "units": units
            }
            
            # Add unit symbols
            temp_unit = "°C" if units == "metric" else "°F" if units == "imperial" else "K"
            speed_unit = "m/s" if units == "metric" else "mph" if units == "imperial" else "m/s"
            
            return {
                "success": True,
                "data": weather_info,
                "message": f"Current weather in {weather_info['city']}: {weather_info['temperature']}{temp_unit}, {weather_info['description']}",
                "formatted": {
                    "temperature": f"{weather_info['temperature']}{temp_unit}",
                    "feels_like": f"{weather_info['feels_like']}{temp_unit}",
                    "wind_speed": f"{weather_info['wind_speed']} {speed_unit}",
                    "visibility": f"{weather_info['visibility']} km"
                }
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "data": {},
                "error": f"Weather API request failed: {str(e)}",
                "message": f"Failed to get weather for {city}"
            }
        except KeyError as e:
            return {
                "success": False,
                "data": {},
                "error": f"Unexpected API response format: {str(e)}",
                "message": f"Failed to parse weather data for {city}"
            }
        except Exception as e:
            return {
                "success": False,
                "data": {},
                "error": f"Unexpected error: {str(e)}",
                "message": f"Failed to get weather for {city}"
            }
    
    def get_weather_forecast(self, city: str, days: int = 5, units: str = "metric") -> Dict[str, Any]:
        """
        Get weather forecast for a city.
        
        Args:
            city: City name
            days: Number of days (1-5)
            units: Temperature units
            
        Returns:
            Dictionary with forecast information
        """
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": units,
                "cnt": min(days * 8, 40)  # API returns 3-hour intervals
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Process forecast data
            forecasts = []
            for item in data["list"]:
                forecasts.append({
                    "datetime": item["dt_txt"],
                    "temperature": item["main"]["temp"],
                    "description": item["weather"][0]["description"].title(),
                    "humidity": item["main"]["humidity"],
                    "wind_speed": item.get("wind", {}).get("speed", 0)
                })
            
            return {
                "success": True,
                "data": {
                    "city": data["city"]["name"],
                    "country": data["city"]["country"],
                    "forecasts": forecasts
                },
                "message": f"Retrieved {len(forecasts)} forecast entries for {data['city']['name']}"
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "data": {},
                "error": f"Weather API request failed: {str(e)}",
                "message": f"Failed to get forecast for {city}"
            }