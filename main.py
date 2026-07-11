from datetime import datetime
from zoneinfo import ZoneInfo

from app.downloader import download_hindu_pdf
from app.sender import (
    send_pdf,
    TelegramTooLargeError
)
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

    last_successful = (
        get_last_successful_date()
    )

    print(
        "Last successful timestamp:",
        last_successful
    )

    if last_successful :

        try:

            last_dt = datetime.fromisoformat(
                last_successful
            )

            if str(last_dt.date()) == today:

                print(
                    f"Today's newspaper already sent at "
                    f"{last_dt.strftime('%I:%M:%S %p IST')}"
                )

                return
                
        
        except ValueError:
        
            #
            # Legacy date-only time format
            #

            if last_successful == today:

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

        pdf_path = download_hindu_pdf(
            newspaper_name="The Hindu"
        )

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

    try:
        
        send_pdf(pdf_path)

    except TelegramTooLargeError:

        print(
            "Main edition too large."
        )

        print(
            "Downloading The Hindu in School..."
        )

        try:

            fallback_pdf = download_hindu_pdf(
                newspaper_name="The Hindu in School"
            )

            print(
                f"Downloaded: {fallback_pdf}"
            )

            send_pdf(fallback_pdf)
        
        except Exception as e:

            print(
                f"Fallback download failed: {e}"
            )

            return

    #
    # Save date ONLY after
    # successful Telegram delivery
    #

    save_successful_date(
        india_now.isoformat()
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