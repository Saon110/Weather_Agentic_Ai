import os
import requests
import streamlit as st
from datetime import datetime, timedelta
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import geocoder
import re

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")


def get_current_location():
    try:
        response = requests.get('https://ipinfo.io/json')
        response.raise_for_status()
        data = response.json()
        lat, lon = map(float, data['loc'].split(','))
        return {'lat': lat, 'lon': lon, 'city': data['city']}
    except requests.exceptions.RequestException as e:
        print(f"Error fetching location: {e}")
        return None


def get_coordinates(city_name):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {'q': city_name, 'appid': OPENWEATHER_API_KEY}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data['coord']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching coordinates: {e}")
        return None


def get_current_weather(input):
    city_name = input.strip() if input else None
    if not city_name or city_name.lower() == "none":
        location = get_current_location()
        if not location:
            return None
        city_name = location['city']

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city_name,
        'appid': OPENWEATHER_API_KEY,
        'units': "metric",
        'mode': "json",
        'lang': "en"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Extract only essential weather data
        filtered_data = {
            'coord': {
                'lon': data['coord']['lon'],
                'lat': data['coord']['lat']
            },
            'weather': [{
                'id': w['id'],
                'main': w['main'],
                'description': w['description'],
                'icon': w['icon']
            } for w in data['weather']],
            'main': {
                'temp': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'pressure': data['main']['pressure'],
                'humidity': data['main']['humidity']
            },
            'visibility': data.get('visibility'),
            'wind': {
                'speed': data['wind']['speed'],
                'deg': data['wind'].get('deg')
            },
            'clouds': {
                'all': data['clouds']['all']
            },
            'rain': {
                '1h': data['rain'].get('1h') if 'rain' in data else None
            },
            'snow': {
                '1h': data['snow'].get('1h') if 'snow' in data else None
            },
            'dt': data['dt'],
            'sys': {
                'country': data['sys']['country'],
                'sunrise': data['sys']['sunrise'],
                'sunset': data['sys']['sunset']
            },
            'name': data['name']
        }
        
        return filtered_data
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching current weather: {e}")
        return None


def get_daily_forecast(input):
    city_name = input.strip() if input else None
    if not city_name or city_name.lower() == "none":
        location = get_current_location()
        if not location:
            return None
        city_name = location['city']

    url = "https://api.openweathermap.org/data/2.5/forecast/daily"
    params = {
        'q': city_name,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Filtered response structure
        filtered = {
            'city': {
                'name': data['city']['name'],
                'coord': {
                    'lat': data['city']['coord']['lat'],
                    'lon': data['city']['coord']['lon']
                },
                'country': data['city']['country']
            },
            'list': []
        }

        # Process each forecast day
        for day in data['list']:
            filtered_day = {
                'dt': day['dt'],
                'temp': {
                    'day': day['temp']['day'],
                    'min': day['temp']['min'],
                    'max': day['temp']['max']
                },
                'feels_like': day['feels_like']['day'],
                'pressure': day['pressure'],
                'humidity': day['humidity'],
                'weather': [{
                    'id': w['id'],
                    'main': w['main'],
                    'description': w['description'],
                    'icon': w['icon']
                } for w in day['weather']],
                'wind_speed': day['speed'],
                'clouds': day['clouds'],
                'pop': day.get('pop', 0),
                'rain': day.get('rain', 0),
                'snow': day.get('snow', 0)
            }
            filtered['list'].append(filtered_day)
            
        return filtered
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching forecast: {e}")
        return None


def get_historical_weather(input):
    inputs = input.split(",")
    city_name = inputs[0].strip()
    days_count = int(re.sub(r'\D', '', inputs[1].strip())) if len(inputs) > 1 else 1
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_count)
    start = int(start_date.timestamp())
    end = int(end_date.timestamp())

    # Location handling remains the same
    if not city_name or city_name.lower() == "none":
        location = get_current_location()
        if not location:
            return None
        lat, lon = location['lat'], location['lon']
    else:
        coord = get_coordinates(city_name)
        if not coord:
            return None
        lat, lon = coord['lat'], coord['lon']

    url = "https://history.openweathermap.org/data/2.5/history/city"
    params = {
        'lat': lat,
        'lon': lon,
        'type': 'hour',
        'start': start,
        'end': end,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Filtered response structure
        filtered = {
            'coordinates': {'lat': lat, 'lon': lon},
            'period': {'start': start, 'end': end},
            'measurements': []
        }

        for entry in data.get('list', []):
            filtered_entry = {
                'dt': entry['dt'],
                'temp': entry['main']['temp'],
                'feels_like': entry['main']['feels_like'],
                'pressure': entry['main']['pressure'],
                'humidity': entry['main']['humidity'],
                'wind': {
                    'speed': entry['wind']['speed'],
                    'deg': entry['wind'].get('deg')
                },
                'clouds': entry['clouds']['all'],
                'precipitation': {
                    'rain_1h': entry.get('rain', {}).get('1h', 0),
                    'rain_3h': entry.get('rain', {}).get('3h', 0),
                    'snow_1h': entry.get('snow', {}).get('1h', 0),
                    'snow_3h': entry.get('snow', {}).get('3h', 0)
                },
                'weather': [{
                    'id': w['id'],
                    'main': w['main'],
                    'description': w['description'],
                    'icon': w['icon']
                } for w in entry['weather']]
            }
            filtered['measurements'].append(filtered_entry)
        
        return filtered

    except requests.exceptions.RequestException as e:
        print(f"Error fetching historical weather: {e}")
        return None


# Initialize the LLM model
llm = ChatGroq(
    model_name="qwen-qwq-32b",
    temperature=0.4,
)

# Define the tools available for the agent
tools = [
    Tool(
        name="Get Current Weather",
        func=get_current_weather,
        description="Returns current weather conditions. Input: city name (string). Example: 'Paris'. If input is 'None', it uses current location."
    ),
    Tool(
        name="Get Daily Forecast",
        func=get_daily_forecast,
        description="Returns daily weather forecast. Input: city name (string). Example: 'Tokyo'. If input is 'None', it uses current location."
    ),
    Tool(
        name="Get Historical Weather",
        func=get_historical_weather,
        description="Returns past weather data. Input format: 'CityName, NumberOfDays'. Example: 'London, 3'. If city name is 'None', it uses current location."
    )
]

# Initialize the agent with the tools and LLM
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    handle_parsing_errors=True,
    verbose=True,
    max_iterations=5
)



def get_weather(user_input: str) -> str:
   
    system_prompt = (
        "You are a helpful and knowledgeable weather assistant. "
        "You answer weather-related queries using accurate data, avoid making things up, "
        "and explain clearly. Use metric units (°C, km/h, mm). If information is unavailable, say so directly. "
        "Now answer the question: "
    )

    full_prompt = system_prompt + user_input
    response = agent.invoke(full_prompt)

    if isinstance(response, dict):
        return response.get("output", "Sorry, no response from agent.")
    else:
        return str(response)

