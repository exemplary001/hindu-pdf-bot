from dotenv import load_dotenv
import os

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

CHECK_INTERVAL_MINUTES = int(
    os.getenv("CHECK_INTERVAL_MINUTES", 15)
)

START_HOUR = int(
    os.getenv("START_HOUR", 10)
)

END_HOUR = int(
    os.getenv("END_HOUR", 14)
)

HEADLESS = (
    os.getenv("HEADLESS", "true").lower()
    == "true"
)

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN"
)

TELEGRAM_CHAT_IDS = os.getenv(
    "TELEGRAM_CHAT_IDS",
    ""
)

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)