from email_module import generate_weather_email_html, send_weather_report_email
from open_meteo_services import get_day_weather_predication_data
from spread_services import get_sheet_data

import time
import os
import smtplib
from dotenv import load_dotenv

load_dotenv()

def connect_to_gmail():
    """Creates a new server connection with a strict timeout."""
    print("🔗 Connecting to Gmail SMTP server...")
    # The 'timeout=15' is the magic bullet! It prevents infinite hanging.
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15)
    server.login(os.getenv("SENDER_EMAIL"), os.getenv("SENDER_APP_PASSWORD"))
    print("✅ Server connected!")
    return server

# --- Testing the Unit ---
if __name__ == "__main__":
    print("🚀 main function execution started")

    # 1. Retrieve user data from Google Sheet
    city_wise_data = get_sheet_data()
    print("✅ phase 1: data from sheet retrieved")

    no_mail_sent = 0
    
    # 2. Open the initial connection
    try:
        server = connect_to_gmail()
    except Exception as e:
        print(f"❌ CRITICAL: Failed to connect to Gmail: {e}")
        exit(1)

    # 3. Run the Email Loop
    try:
        for (city, country), users in city_wise_data.items():
            
            # Added a print statement here so you know if the Weather API hangs!
            print(f"🌍 Fetching weather API data for {city}...")
            weather = get_day_weather_predication_data(f"{city}, {country}")
            print(f"✅ phase 2: weather data for {city} retrieved")

            for user in users:
                recipient_email = user['📧 Your Email']
                username = user['😄 What should we call you? ']
                
                print(f"⏳ Preparing to send to {recipient_email}...")
                
                html = generate_weather_email_html(
                    username=username,
                    weather=weather
                )
                
                # --- 🛡️ THE RECONNECTION SAFETY NET 🛡️ ---
                try:
                    # noop() acts like a ping. If Google silently dropped us, this fails.
                    server.noop() 
                except Exception:
                    print("⚠️ Connection dropped by Google. Reconnecting on the fly...")
                    server = connect_to_gmail()
                # ------------------------------------------

                success = send_weather_report_email(
                    server,
                    html,
                    recipient_email,
                    user['🏙️ Your City']
                )
                
                if success:
                    no_mail_sent += 1
                    print(f"✅ {no_mail_sent} mail sent to {recipient_email}")
                
                time.sleep(2)

    except Exception as e:
        print(f"❌ An error occurred during the email loop: {e}")
        
    finally:
        try:
            server.quit()
        except:
            pass # Ignore if the connection is already dead
        print(f"🎉 Server connection closed. Total emails sent: {no_mail_sent}")
