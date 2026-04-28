print("🔥 before imports")

from email_module import generate_weather_email_html, send_weather_report_email
from open_meteo_services import get_day_weather_predication_data
from spread_services import get_sheet_data

import time
from dotenv import load_dotenv
load_dotenv()

print("🔥 Script file loaded")

# --- Testing the Unit ---
if __name__ == "__main__":
    print("main function execution started")

    # user name retrive from a google sheet

    city_wise_data = get_sheet_data()
    print("pahse 1 cleared data from sheet retrived ✅")

    no_mail_sent = 0
    for (city, country), users in city_wise_data.items():

        # same city once api call is there
        weather = get_day_weather_predication_data(
            f"{city}, {country}"
        )
        print("pahse 2 running data for city retrived ✅")


        for user in users:
            # as per user creating a mail template
            html = generate_weather_email_html(
                username=user['😄 What should we call you? '],
                weather=weather
            )
            # sending mail process started
            send_weather_report_email(
                html,
                user['📧 Your Email'],
                user['🏙️ Your City']
            )
            no_mail_sent = no_mail_sent+1
            print(f"{no_mail_sent} mail sent")
            time.sleep(15)
    print("✅ ALL TASKS COMPLETED - EXITING")


    
