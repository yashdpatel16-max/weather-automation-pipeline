import gspread
from google.oauth2.service_account import Credentials
from collections import defaultdict

import os
from dotenv import load_dotenv
load_dotenv()


def get_sheet_data():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_file(
        "service_account.json",  # rename your JSON to this
        scopes=scope
    )

    client = gspread.authorize(creds)

    sheet_name= os.environ.get("SHEET_NAME")
    # Replace with your sheet name EXACTLY
    sheet = client.open(sheet_name).sheet1

    data = sheet.get_all_records()

    city_wise_data = defaultdict(list)

    for user in data:

        key = (
            user['🏙️ Your City'].strip().lower(),
            user['🌍 Your Country'].strip().lower()
        )

        city_wise_data[key].append(user)
    return city_wise_data
