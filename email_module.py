import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
load_dotenv()


# ==========================================
# Unit 1: The Email Template Engine
# ==========================================

def generate_weather_email_html(username: str, weather: dict) -> str:
    """
    Generates a beautiful responsive HTML email template
    for daily weather updates.
    """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Daily Weather Update</title>
    </head>

    <body style="
        margin: 0;
        padding: 0;
        background-color: #eef2f7;
        font-family: Arial, sans-serif;
    ">

        <div style="
            max-width: 600px;
            margin: 30px auto;
            background-color: #ffffff;
            border-radius: 18px;
            overflow: hidden;
            box-shadow: 0 4px 18px rgba(0,0,0,0.08);
        ">

            <!-- Header -->
            <div style="
                background: linear-gradient(135deg, #4facfe, #00c6fb);
                color: white;
                text-align: center;
                padding: 35px 20px;
            ">
                <h1 style="
                    margin: 0;
                    font-size: 32px;
                    font-weight: bold;
                ">
                    🌤️ Daily Weather Update
                </h1>

                <p style="
                    margin-top: 10px;
                    font-size: 16px;
                    opacity: 0.95;
                ">
                    Personalized forecast just for you
                </p>
            </div>

            <!-- Greeting -->
            <div style="padding: 30px 25px 10px 25px;">
                <h2 style="
                    margin: 0;
                    color: #202124;
                    font-size: 24px;
                ">
                    Hey {username} 👋
                </h2>

                <p style="
                    color: #5f6368;
                    font-size: 16px;
                    margin-top: 10px;
                    line-height: 1.6;
                ">
                    Here's your weather forecast for
                    <strong>{weather['city']}</strong>.
                    Hope you have an amazing day ahead ☀️
                </p>
            </div>

            <!-- Weather Card -->
            <div style="
                margin: 20px 25px;
                background-color: #f8fbff;
                border-radius: 16px;
                padding: 25px;
                border: 1px solid #dbe7f3;
            ">

                <div style="text-align: center;">
                    <h2 style="
                        margin: 0;
                        font-size: 30px;
                        color: #1a73e8;
                    ">
                        {weather['condition']}
                    </h2>

                    <p style="
                        margin-top: 12px;
                        font-size: 42px;
                        color: #202124;
                        font-weight: bold;
                    ">
                        {weather['max_temp']}°C
                    </p>

                    <p style="
                        margin-top: -10px;
                        color: #5f6368;
                        font-size: 16px;
                    ">
                        Min Temp: {weather['min_temp']}°C
                    </p>
                </div>

                <!-- Info Grid -->
                <table width="100%" cellpadding="10" cellspacing="0" style="
                    margin-top: 20px;
                    border-collapse: collapse;
                ">
                    <tr>
                        <td style="
                            background-color: #ffffff;
                            border-radius: 12px;
                            text-align: center;
                            border: 1px solid #e5e7eb;
                        ">
                            <p style="margin: 0; font-size: 14px; color: #5f6368;">
                                🌅 Sunrise
                            </p>

                            <p style="
                                margin: 8px 0 0 0;
                                font-size: 18px;
                                font-weight: bold;
                                color: #202124;
                            ">
                                {weather['sunrise']}
                            </p>
                        </td>

                        <td width="10"></td>

                        <td style="
                            background-color: #ffffff;
                            border-radius: 12px;
                            text-align: center;
                            border: 1px solid #e5e7eb;
                        ">
                            <p style="margin: 0; font-size: 14px; color: #5f6368;">
                                🌇 Sunset
                            </p>

                            <p style="
                                margin: 8px 0 0 0;
                                font-size: 18px;
                                font-weight: bold;
                                color: #202124;
                            ">
                                {weather['sunset']}
                            </p>
                        </td>
                    </tr>
                </table>

                <!-- UV Index -->
                <div style="
                    margin-top: 20px;
                    background-color: #ffffff;
                    border: 1px solid #e5e7eb;
                    border-radius: 12px;
                    padding: 18px;
                    text-align: center;
                ">
                    <p style="
                        margin: 0;
                        font-size: 15px;
                        color: #5f6368;
                    ">
                        ☀️ UV Index
                    </p>

                    <p style="
                        margin: 10px 0 0 0;
                        font-size: 28px;
                        font-weight: bold;
                        color: #f29900;
                    ">
                        {weather['uv_index']}
                    </p>
                </div>
            </div>

            <!-- Friendly Message -->
            <div style="
                padding: 10px 25px 30px 25px;
                text-align: center;
            ">
                <p style="
                    color: #5f6368;
                    font-size: 15px;
                    line-height: 1.7;
                    margin: 0;
                ">
                    Stay prepared and enjoy your day 🌈<br>
                    More exciting automation features coming soon 🚀
                </p>
            </div>

            <!-- Footer -->
            <div style="
                background-color: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #80868b;
                font-size: 12px;
                border-top: 1px solid #e5e7eb;
            ">
                <p style="margin: 0;">
                    This is an automated report generated by weather Data Pipeline.
                </p>

                <p style="margin: 5px 0 0 0;">
                    Source: Open-Meteo API
                </p>

                <p style="margin: 10px 0 0 0;">
                    Built with ❤️ by Yash
                </p>
            </div>

        </div>
    </body>
    </html>
    """

    return html




# ==========================================
# Unit 2: The Secure SMTP Mailer
# ==========================================
def send_weather_report_email(server, html_content: str, recipient_email: str, city: str) -> bool:
    """
    Sends an HTML-formatted email using an existing Gmail SMTP server connection.
    
    Args:
        server (smtplib.SMTP_SSL): An already authenticated SMTP server instance.
        html_content (str): The HTML string to be sent as the email body.
        recipient_email (str): The destination email address.
        city (str): The city name for the subject line.
        
    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    # 1. Fetch credentials (we only need the email here for the 'From' field)
    sender_email = os.environ.get("SENDER_EMAIL")
    
    if not sender_email:
        print("Auth Error: SENDER_EMAIL is missing from environment variables.")
        return False

    # 2. Construct the Email Message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"🌤️ Weather Update for {city}"
    msg['From'] = f"Weather Bot <{sender_email}>"
    msg['To'] = recipient_email

    # Attach the HTML content to the email container
    mime_html = MIMEText(html_content, 'html')
    msg.attach(mime_html)

    # 3. Send using the OPEN connection passed into the function
    try:
        # Notice we are using the 'server' that was passed in, without logging in again!
        server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"Success: Weather report securely dispatched to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"System Error: Failed to dispatch email to {recipient_email} due to: {e}")
        return False
