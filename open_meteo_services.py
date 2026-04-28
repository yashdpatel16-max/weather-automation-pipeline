import requests


import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

from datetime import datetime

# ==========================================
# Unit 2: get longitude and latitude for city
# ==========================================

def get_location(city):
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"

        params = {
            "name": city,
            "count": 1
        }

        res = requests.get(url, params=params).json()

        if "results" not in res:
            return None

        r = res["results"][0]

        return {
            "city": r["name"],
            "country": r["country"],
            "country_code": r["country_code"],
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "state":r["admin1"]
        }
    except Exception as e:
        return {"error":str(e)}

# dta = get_location("valsad,India")
# print(dta)




# Weather code mapping
WEATHER_CODES = {
    0: "Clear Sky ☀️",
    1: "Mainly Clear 🌤️",
    2: "Partly Cloudy ⛅",
    3: "Overcast ☁️",
    45: "Fog 🌫️",
    48: "Depositing Rime Fog 🌫️",
    51: "Light Drizzle 🌦️",
    53: "Moderate Drizzle 🌦️",
    55: "Dense Drizzle 🌧️",
    61: "Slight Rain 🌧️",
    63: "Moderate Rain 🌧️",
    65: "Heavy Rain 🌧️",
    71: "Slight Snow ❄️",
    73: "Moderate Snow ❄️",
    75: "Heavy Snow ❄️",
    95: "Thunderstorm ⛈️"
}


def preprocess_weather_data(
    city: str,
    daily_weather_code,
    daily_temperature_2m_max,
    daily_temperature_2m_min,
    daily_sunrise,
    daily_sunset,
    daily_uv_index_max,
):
    """
    Converts raw Open-Meteo API arrays into a clean dictionary
    ready for email generation.
    """

    # Convert sunrise/sunset timestamps
    sunrise_time = datetime.fromtimestamp(
            int(daily_sunrise[0])
        ).strftime("%I:%M %p")

    sunset_time = datetime.fromtimestamp(
        int(daily_sunset[0])
    ).strftime("%I:%M %p")

    # Weather code
    weather_code = int(daily_weather_code[0])

    # Final cleaned data
    weather_data = {
        "city": city,

        "condition": WEATHER_CODES.get(
            weather_code,
            "Unknown Weather"
        ),

        "weather_code": weather_code,

        "max_temp": round(
            float(daily_temperature_2m_max[0]), 1
        ),

        "min_temp": round(
            float(daily_temperature_2m_min[0]), 1
        ),

        "uv_index": round(
            float(daily_uv_index_max[0]), 1
        ),

        "sunrise": sunrise_time,
        "sunset": sunset_time,
    }

    return weather_data

# ==========================================
# Unit 2: day weather predication data
# ==========================================

def get_day_weather_predication_data(city,latitude: int=22,longitude: int =79):
    try:
        # city longitude and latitude
        if city:
            city_data = get_location(city)

            if "latitude" and "longitude" in city_data:
                latitude = city_data.get("latitude")
                longitude = city_data.get("longitude")

        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        openmeteo = openmeteo_requests.Client(session = retry_session)

        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "sunrise", "sunset", "uv_index_max", "uv_index_clear_sky_max", "daylight_duration", "sunshine_duration"],
            "timezone": "auto",
            "forecast_days": 1,
        }
        responses = openmeteo.weather_api(url, params = params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        # print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
        # print(f"Elevation: {response.Elevation()} m asl")
        # print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
        # print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

        # Process daily data. The order of variables needs to be the same as requested.
        daily = response.Daily()
        daily_weather_code = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
        daily_sunrise = daily.Variables(3).ValuesInt64AsNumpy()
        daily_sunset = daily.Variables(4).ValuesInt64AsNumpy()
        daily_uv_index_max = daily.Variables(5).ValuesAsNumpy()
        daily_uv_index_clear_sky_max = daily.Variables(6).ValuesAsNumpy()
        daily_daylight_duration = daily.Variables(7).ValuesAsNumpy()
        daily_sunshine_duration = daily.Variables(8).ValuesAsNumpy()

        daily_data = {"date": pd.date_range(
            start = pd.to_datetime(daily.Time() + response.UtcOffsetSeconds(), unit = "s", utc = True),
            end =  pd.to_datetime(daily.TimeEnd() + response.UtcOffsetSeconds(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = daily.Interval()),
            inclusive = "left"
        )}

        weather_data = preprocess_weather_data(
            city=city,
            daily_weather_code=daily_weather_code,
            daily_temperature_2m_max=daily_temperature_2m_max,
            daily_temperature_2m_min=daily_temperature_2m_min,
            daily_sunrise=daily_sunrise,
            daily_sunset=daily_sunset,
            daily_uv_index_max=daily_uv_index_max,
        )

        return weather_data
        
    
    except Exception as e:
        # Failsafe for any unexpected system-level issues
        print(f"weather data fetch Failure: {e}")
        return False