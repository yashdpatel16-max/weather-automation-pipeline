from email_module import generate_weather_email_html, send_weather_report_email
from open_meteo_services import get_day_weather_predication_data
from spread_services import get_sheet_data

import time
import os
import smtplib
from dotenv import load_dotenv

load_dotenv()

# --- Testing the Unit ---
if __name__ == "__main__":
    print("main function execution started")

    # 1. Retrieve user data from Google Sheet
    city_wise_data = get_sheet_data()
    print("phase 1 cleared data from sheet retrieved ✅")

    no_mail_sent = 0
    
    # 2. Fetch credentials for the server connection
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_APP_PASSWORD")
    
    if not sender_email or not sender_password:
        print("CRITICAL: Email credentials missing. Exiting.")
        exit(1)

    # 3. OPEN THE CONNECTION ONCE
    print("Connecting to Gmail SMTP server...")
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        print("Server connected successfully! ✅")
    except Exception as e:
        print(f"CRITICAL: Failed to connect to Gmail server: {e}")
        exit(1)

    # 4. Run the Email Loop
    try:
        for (city, country), users in city_wise_data.items():

            # Same city, one API call
            weather = get_day_weather_predication_data(f"{city}, {country}")
            print(f"phase 2 running data for {city} retrieved ✅")

            for user in users:
                # Create the mail template per user
                html = generate_weather_email_html(
                    username=user['😄 What should we call you?'],
                    weather=weather
                )
                
                # Send the email by passing the OPEN 'server' connection
                success = send_weather_report_email(
                    server,
                    html,
                    user['📧 Your Email'],
                    user['🏙️ Your City']
                )
                
                if success:
                    no_mail_sent += 1
                    print(f"{no_mail_sent} mail sent to {user['😄 What should we call you?']} ")
                
                # A 2-second sleep is perfect now to respect general API limits
                time.sleep(2)

    except Exception as e:
        print(f"An error occurred during the email loop: {e}")
        
    finally:
        # 5. CLOSE THE CONNECTION ONCE
        server.quit()
        print(f"Server connection closed. Total emails sent: {no_mail_sent} 🎉")
