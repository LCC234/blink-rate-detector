from scipy.spatial import distance as dist
import smtplib
from twilio.rest import Client
import logging
from dotenv import load_dotenv  
from os import getenv

load_dotenv()

# Define Constant
ALERT_CONFIRMATION_COUNT = 2 # number of warning alerts to send SMS and email alerts

# Twilio account information for sending SMS
TWILIO_ACCOUNT_SID = getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = getenv("TWILIO_PHONE_NUMBER")
YOUR_PHONE_NUMBER = getenv("YOUR_PHONE_NUMBER")

# Email account information for sending email
EMAIL_ADDRESS = getenv("EMAIL_ADDRESS")
RECIPIENT_EMAIL_ADDRESS = getenv("RECIPIENT_EMAIL_ADDRESS")
GMAIL_APP_PASSWORD = getenv("GMAIL_APP_PASSWORD")

def get_console_logging_handler():
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter('%(name)s: %(asctime)s - %(levelname)s - %(message)s'))
    return console_handler

# Variable
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)
logger.addHandler(get_console_logging_handler())



def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

def send_email(subject, body, image=None):
    # Create a connection to the Gmail SMTP server
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)

    # Login to your Gmail account
    server.login(EMAIL_ADDRESS, GMAIL_APP_PASSWORD)

    # Compose your email message
    to = RECIPIENT_EMAIL_ADDRESS
    message = f'Subject: {subject}\n\n{body}'

    # Send the email
    server.sendmail(EMAIL_ADDRESS, to, message)

    # Close the SMTP connection
    server.quit()

def send_sms(msg):
    message = client.messages.create(
        to=YOUR_PHONE_NUMBER,
        from_=TWILIO_PHONE_NUMBER,
        body=msg)
    print(f"SMS sent! Message SID: {message.sid}")

def add_to_low_blink_list(blink_rate, blink_list : list):
    blink_list.insert(0,blink_rate)
    if len(blink_list) > ALERT_CONFIRMATION_COUNT:
        blink_list.pop()
    return blink_list