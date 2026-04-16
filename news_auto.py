from datetime import datetime
from typing import Optional

import socket

import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

from email_module import generate_weather_email_html,send_weather_report_email
import os

# ==========================================
# Unit 1: The Timestamp Generator
# ==========================================
def get_report_timestamp(custom_format: Optional[str] = None) -> str:
    """
    Generates a standardized timestamp for automated PDF reports and system logs.
    
    Args:
        custom_format (Optional[str]): A specific strftime format string. 
                                       If None, defaults to 'YYYY-MM-DD HH:MM:SS'.
        
    Returns:
        str: The safely formatted current local time.
    """
    # Set our default enterprise-standard format
    format_string = custom_format or "%Y-%m-%d %H:%M:%S"
    
    try:
        current_time = datetime.now()
        return current_time.strftime(format_string)
        
    except ValueError as ve:
        # This catches if someone passes a completely invalid format string
        print(f"Warning: Invalid time format provided ({ve}). Defaulting to ISO 8601.")
        return datetime.now().isoformat()
    except Exception as e:
        # Failsafe for any other system error
        print(f"System Error: Could not generate time due to: {e}")
        return "TIMESTAMP_ERROR"



# ==========================================
# Unit 2: The Network Connectivity Validator
# ==========================================
def is_internet_active(host: str = "8.8.8.8", port: int = 53, timeout: int = 3) -> bool:
    """
    Checks if the device has an active internet connection by attempting 
    to open a TCP socket to a highly reliable external server.
    
    Args:
        host (str): The IP address to connect to. Defaults to Google's public DNS (8.8.8.8).
        port (int): The port to connect on. Defaults to 53 (Standard DNS port).
        timeout (int): Seconds to wait before assuming the network is down.
        
    Returns:
        bool: True if the connection succeeds, False if offline.
    """
    try:
        # Create a socket object (IPv4, TCP stream)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Set a strict timeout so the script doesn't hang indefinitely
            sock.settimeout(timeout)
            
            # Attempt to connect to the target host and port
            sock.connect((host, port))
            
        # If it reaches here without throwing an error, we have internet
        return True
        
    except OSError:
        # OSError gracefully catches "network unreachable", "timeout", etc.
        return False
    except Exception as e:
        # Failsafe for any unexpected system-level issues
        print(f"Critical Network Check Failure: {e}")
        return False


# ==========================================
# Unit 3: day weather predication data
# ==========================================

def get_day_weather_predication_data(latitude: int=22,longitude: int =79):
    try:
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
        print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
        print(f"Elevation: {response.Elevation()} m asl")
        print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
        print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

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

        daily_data["weather_code"] = daily_weather_code
        daily_data["temperature_2m_max"] = daily_temperature_2m_max
        daily_data["temperature_2m_min"] = daily_temperature_2m_min
        daily_data["sunrise"] = daily_sunrise
        daily_data["sunset"] = daily_sunset
        daily_data["uv_index_max"] = daily_uv_index_max
        daily_data["uv_index_clear_sky_max"] = daily_uv_index_clear_sky_max
        daily_data["daylight_duration"] = daily_daylight_duration
        daily_data["sunshine_duration"] = daily_sunshine_duration

        daily_dataframe = pd.DataFrame(data = daily_data)
        # print("\nDaily data\n", daily_dataframe)
        return daily_dataframe
    
    except Exception as e:
        # Failsafe for any unexpected system-level issues
        print(f"weather data fetch Failure: {e}")
        return False
# --- Testing the Unit ---
if __name__ == "__main__":
    # Test 1: Standard Output (For logging or database entries)
    print("Standard:", get_report_timestamp())
    
    # Test 2: Clean Output (Great for saving PDF file names without spaces/colons)
    # print("File Name Safe:", get_report_timestamp("%Y%m%d_%H%M%S"))

    print("Initiating Network Diagnostics...")
    
    if is_internet_active():
        print("System Status: ONLINE. Proceeding with automation pipeline.")
    else:
        print("System Status: OFFLINE. Aborting pipeline to prevent data loss.")

    daily_dataframe = get_day_weather_predication_data()

    # if not daily_dataframe:
        # print("error while weather data fetch")
    
    # print("\nDaily data\n", daily_dataframe)

    mail_template = generate_weather_email_html(daily_dataframe)

    # print(mail_template)
    
    target_inbox = os.environ.get("TARGET_INBOX") # Replace with your actual email
    
    send_weather_report_email(mail_template, target_inbox)




    