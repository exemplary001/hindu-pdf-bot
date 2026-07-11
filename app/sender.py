from pathlib import Path

import requests

from app.config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_IDS
)


class TelegramTooLargeError(Exception):
    pass


def send_pdf(pdf_path: Path):

    url = (
        f"https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}"
        f"/sendDocument"
    )

    chat_ids = [
        chat_id.strip()
        for chat_id in TELEGRAM_CHAT_IDS.split(",")
        if chat_id.strip()
    ]

    for chat_id in chat_ids:

        print(
            f"Sending PDF to chat {chat_id}..."
        )

        with open(pdf_path, "rb") as pdf:

            response = requests.post(
                url,
                data={
                    "chat_id": chat_id,
                    "caption":
                        "📰 Today's Hindu Newspaper"
                },
                files={
                    "document": (
                        pdf_path.name,
                        pdf,
                        "application/pdf"
                    )
                },
                timeout=300
            )

        print(
            f"Response status code: {response.status_code}"
        )

        print(
            response.text
        )

        if response.status_code == 413:

            raise TelegramTooLargeError(
                "Telegram upload limit exceeded."
            )

        response.raise_for_status()

        print(
            f"Successfully sent to {chat_id}"
        )

    print(
        "\nAll Telegram deliveries completed."
    )