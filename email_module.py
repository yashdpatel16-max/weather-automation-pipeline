import pandas as pd
from datetime import datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ==========================================
# Unit 3: The Email Template Engine
# ==========================================

def get_weather_description(code: float) -> tuple:
    """
    Translates WMO weather codes from Open-Meteo into readable text and emojis.
    Returns: (Description string, Emoji string)
    """
    weather_mapping = {
        0: ("Clear sky", "☀️"),
        1: ("Mainly clear", "🌤️"),
        2: ("Partly cloudy", "⛅"),
        3: ("Overcast", "☁️"),
        45: ("Foggy", "🌫️"),
        48: ("Depositing rime fog", "🌫️"),
        51: ("Light drizzle", "🌧️"),
        53: ("Moderate drizzle", "🌧️"),
        55: ("Dense drizzle", "🌧️"),
        61: ("Slight rain", "☔"),
        63: ("Moderate rain", "☔"),
        65: ("Heavy rain", "🌊☔"),
        80: ("Slight rain showers", "🌦️"),
    }
    # Default to a general weather emoji if code is not found
    return weather_mapping.get(int(code), ("Variable conditions", "🌍"))

def format_duration(seconds: float) -> str:
    """Converts raw seconds (like daylight_duration) into 'X hrs Y mins'."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}h {minutes}m"

def generate_weather_email_html(df: pd.DataFrame) -> str:
    """
    Ingests the daily_dataframe and returns a fully styled, 
    responsive HTML string ready to be sent via SMTP.
    """
    # Extract the first row of data (assuming it's today's forecast)
    today = df.iloc[0]
    
    # 1. Clean and format the data
    raw_date = today['date']
    date_str = raw_date.strftime("%A, %B %d, %Y") if isinstance(raw_date, datetime) else str(raw_date).split()[0]
    
    max_temp = round(today['temperature_2m_max'], 1)
    min_temp = round(today['temperature_2m_min'], 1)
    uv_index = round(today['uv_index_max'], 1)
    
    weather_desc, weather_emoji = get_weather_description(today['weather_code'])
    daylight = format_duration(today['daylight_duration'])
    
    # 2. The HTML Template (Using safe inline CSS for email clients)
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 20px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f4f7f6; color: #333333;">
        
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
            
            <div style="background-color: #1a73e8; padding: 30px 20px; text-align: center; color: #ffffff;">
                <h1 style="margin: 0; font-size: 24px; font-weight: 600; letter-spacing: 0.5px;">Daily Weather Briefing</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">{date_str}</p>
            </div>

            <div style="padding: 40px 20px; text-align: center; border-bottom: 1px solid #eeeeee;">
                <div style="font-size: 64px; line-height: 1; margin-bottom: 10px;">{weather_emoji}</div>
                <h2 style="margin: 0 0 5px 0; font-size: 28px; color: #202124;">{weather_desc}</h2>
                
                <div style="display: inline-block; margin-top: 20px;">
                    <span style="font-size: 48px; font-weight: bold; color: #ea4335;">{max_temp}&deg;C</span>
                    <span style="font-size: 24px; color: #70757a; margin: 0 15px;">/</span>
                    <span style="font-size: 48px; font-weight: bold; color: #4285f4;">{min_temp}&deg;C</span>
                </div>
            </div>

            <div style="padding: 30px 40px;">
                <h3 style="margin: 0 0 20px 0; font-size: 18px; color: #5f6368; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px;">Atmospheric Details</h3>
                
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f0f0f0; width: 50%;">
                            <strong style="color: #202124;">UV Index (Max):</strong>
                        </td>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f0f0f0; text-align: right; color: #d93025; font-weight: bold;">
                            {uv_index}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f0f0f0;">
                            <strong style="color: #202124;">Daylight Duration:</strong>
                        </td>
                        <td style="padding: 12px 0; border-bottom: 1px solid #f0f0f0; text-align: right; color: #5f6368;">
                            {daylight}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0;">
                            <strong style="color: #202124;">Coordinates:</strong>
                        </td>
                        <td style="padding: 12px 0; text-align: right; color: #5f6368;">
                            22.0&deg;N, 79.0&deg;E
                        </td>
                    </tr>
                </table>
            </div>

            <div style="background-color: #f8f9fa; padding: 20px; text-align: center; color: #80868b; font-size: 12px;">
                <p style="margin: 0;">This is an automated report generated by your Data Pipeline.</p>
                <p style="margin: 5px 0 0 0;">Source: Open-Meteo API</p>
            </div>

        </div>
    </body>
    </html>
    """
    return html_template




# ==========================================
# Unit 4: The Secure SMTP Mailer
# ==========================================
def send_weather_report_email(html_content: str, recipient_email: str) -> bool:
    """
    Sends an HTML-formatted email using Gmail's SMTP server.
    Requires environment variables for authentication.
    
    Args:
        html_content (str): The HTML string to be sent as the email body.
        recipient_email (str): The destination email address.
        
    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    # 1. Fetch credentials securely from the environment
    # In a local setup, you would set these in your terminal or a .env file
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_APP_PASSWORD")
    
    
    if not sender_email or not sender_password:
        print("Auth Error: Email credentials are missing from environment variables.")
        return False

    # 2. Construct the Email Message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Your Daily Weather Briefing"
    msg['From'] = sender_email
    msg['To'] = recipient_email

    # Attach the HTML content to the email container
    mime_html = MIMEText(html_content, 'html')
    msg.attach(mime_html)

    # 3. Establish Secure Connection and Send
    try:
        # Port 465 is the standard for secure SMTP over SSL
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            
        print(f"Success: Weather report securely dispatched to {recipient_email}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("SMTP Error: Authentication failed. Check your App Password.")
        return False
    except Exception as e:
        print(f"System Error: Failed to dispatch email due to: {e}")
        return False

# # --- Testing the Unit ---
# if __name__ == "__main__":
    # Dummy HTML for standalone testing
    # test_html = "<html><body><h1>Test Pipeline Active</h1></body></html>"
    # target_inbox = "" # Replace with your actual email
    
    # send_weather_report_email(test_html, target_inbox)