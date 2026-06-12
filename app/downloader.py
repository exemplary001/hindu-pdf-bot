from pathlib import Path
from datetime import date
from urllib.parse import urljoin

import requests
from playwright.sync_api import sync_playwright


DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


def download_hindu_pdf():

    today = date.today().isoformat()

    filename = f"hindu_{today}.pdf"
    filepath = DOWNLOAD_DIR / filename

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        context = browser.new_context()

        #
        # PAGE 1
        #

        page1 = context.new_page()

        print("Opening Indiags...")

        page1.goto(
            "https://www.indiags.com/epaper-pdf-download",
            wait_until="networkidle",
            timeout=60000
        )

        #
        # STEP 1
        # THE HINDU READ
        #

        with context.expect_page() as page2_info:

            page1.locator(
                "xpath=/html/body/div[2]/div[4]/div[5]/div[2]/a"
            ).click()

        page2 = page2_info.value
        page2.wait_for_load_state()

        print("Page2:", page2.url)

        #
        # STEP 2
        # READ NEWSPAPER
        #

        with context.expect_page() as page3_info:

            page2.locator(
                "xpath=/html/body/div/div[28]/button"
            ).click()

        page3 = page3_info.value
        page3.wait_for_load_state()

        print("Page3:", page3.url)

        #
        # STEP 3
        # UNLOCK QUIZ
        #

        with context.expect_page() as page4_info:

            page3.locator(
                "xpath=/html/body/div[2]/div/div[2]/a"
            ).click()

        page4 = page4_info.value
        page4.wait_for_load_state()

        print("Page4:", page4.url)

        #
        # WAIT 15 SEC
        #

        print("Waiting 15 seconds...")

        page4.wait_for_timeout(15000)

        #
        # DOWNLOAD BUTTON
        #

        download_button = page4.locator(
            "xpath=/html/body/div[6]/a"
        )

        download_button.wait_for(
            state="visible",
            timeout=60000
        )

        href = download_button.get_attribute(
            "href"
        )

        if not href:

            raise Exception(
                "Download PDF href not found."
            )

        pdf_page_url = urljoin(
            "https://www.indiags.com",
            href
        )

        print("PDF Page URL:")
        print(pdf_page_url)

        #
        # OPEN PDF PAGE
        #

        pdf_page = context.new_page()

        pdf_page.goto(
            pdf_page_url,
            wait_until="networkidle",
            timeout=60000
        )

        #
        # EXTRACT EMBED SRC
        #

        embed = pdf_page.locator(
            "embed[type='application/pdf']"
        )

        embed.wait_for(
            state="visible",
            timeout=30000
        )

        pdf_src = embed.get_attribute(
            "src"
        )

        if not pdf_src:

            raise Exception(
                "PDF embed src not found."
            )

        #
        # BUILD ACTUAL PDF URL
        #

        pdf_url = urljoin(
            pdf_page.url,
            pdf_src
        )

        print("Actual PDF URL:")
        print(pdf_url)

        #
        # DOWNLOAD PDF
        #

        response = requests.get(
            pdf_url,
            timeout=120
        )

        response.raise_for_status()

        with open(filepath, "wb") as f:

            f.write(response.content)

        print(
            f"Saved PDF: {filepath}"
        )

        browser.close()

        return filepath