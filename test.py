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
        return response.json()
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
        'cnt': 7,
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
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
        'appid': OPENWEATHER_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching historical weather: {e}")
        return None


# Initialize the LLM model
llm = ChatGroq(
    model_name="qwen-qwq-32b",
    temperature=0.3,
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
    max_iterations=8
)

# Streamlit Frontend
def main():
    st.title("Weather Assistant")
    st.write("Ask your weather-related questions, and I'll fetch the data for you!")

    # User input
    query = st.text_input("Enter your weather query:")

    # Query submission
    if st.button("Get Weather"):
        if query:
            # Call the agent to process the query
            system_message = """You are a helpful and knowledgeable weather assistant. You answer weather-related queries using accurate data, avoid making things up, and explain clearly. Use metric units (°C, km/h, mm). If information is unavailable, say so directly. Now ans the question: """
            response = agent.invoke(system_message + query)
            st.write(response)
        else:
            st.warning("Please enter a query.")

if __name__ == "__main__":
    main()
