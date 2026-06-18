from datetime import datetime
from zoneinfo import ZoneInfo

from app.downloader import download_hindu_pdf
from app.sender import send_pdf
from app.state import (
    get_last_successful_date,
    save_successful_date
)


def main():

    india_now = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    today = str(
        india_now.date()
    )

    print(
        f"Today: {today}"
    )

    #
    # Check Neon state
    #

    last_successful_date = (
        get_last_successful_date()
    )

    print(
        "Last successful date:",
        last_successful_date
    )

    #
    # Already sent today?
    #

    if last_successful_date == today:

        print(
            "Today's newspaper already sent."
        )

        return

    #
    # Download newspaper
    #

    print(
        "Starting newspaper download..."
    )

    try:

        pdf_path = download_hindu_pdf()

    except Exception as e:

        print(
            f"Download skipped: {e}"
        )

        return

    print(
        f"Downloaded: {pdf_path}"
    )

    #
    # Send Telegram
    #

    print(
        "Sending Telegram message..."
    )

    send_pdf(pdf_path)

    #
    # Save date ONLY after
    # successful Telegram delivery
    #

    save_successful_date(
        today
    )

    print(
        "Workflow completed successfully."
    )


if __name__ == "__main__":

    try:

        main()

    except Exception as e:

        print(
            f"ERROR: {e}"
        )

        raise