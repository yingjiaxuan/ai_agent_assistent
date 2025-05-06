# Context-aware life assistant functions
import requests
from datetime import datetime

def get_context_info():
    # Fetch weather information
    weather_api_url = "http://api.weatherapi.com/v1/current.json?key=YOUR_WEATHER_API_KEY&q=Tokyo"
    weather_response = requests.get(weather_api_url)
    weather_info = weather_response.json()
    
    # Fetch holiday information
    holidays_api_url = "https://date.nager.at/Api/v2/PublicHolidays/2025/JP"
    holidays_response = requests.get(holidays_api_url)
    holidays_info = holidays_response.json()
    
    # Mocked free time periods
    free_time_periods = ["Saturday afternoon", "Sunday morning"]
    
    return weather_info, holidays_info, free_time_periods

def generate_life_suggestions():
    weather_info, holidays_info, free_time_periods = get_context_info()
    
    # Generate suggestions using GPT
    prompt = f"Based on the current weather: {weather_info['current']['condition']['text']}, upcoming holidays: {[holiday['localName'] for holiday in holidays_info]}, and free time periods: {free_time_periods}, suggest some activities for this weekend."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100
    )
    suggestion = response.choices[0].text.strip()
    return suggestion