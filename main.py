from datetime import date

from app.state import (
    get_last_successful_date,
    save_successful_date
)

from app.downloader import download_hindu_pdf
from app.sender import send_pdf


def main():

    today = str(date.today())

    if get_last_successful_date() == today:

        print(
            "Today's newspaper already sent."
        )

        return

    pdf_path = download_hindu_pdf()

    send_pdf(pdf_path)

    save_successful_date(today)

    print(
        "Workflow completed successfully."
    )


if __name__ == "__main__":

    main()