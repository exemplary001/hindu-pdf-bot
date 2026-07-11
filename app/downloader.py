from pathlib import Path
from datetime import date, datetime
from zoneinfo import ZoneInfo
from urllib.parse import urljoin
from urllib.parse import unquote
import re

import requests
from playwright.sync_api import sync_playwright

import fitz
import tempfile


DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

def extract_date_from_pdf(pdf_bytes):

    with tempfile.NamedTemporaryFile(
        suffix=".pdf",
        delete=True
    ) as temp_pdf:

        temp_pdf.write(pdf_bytes)
        temp_pdf.flush()

        doc = fitz.open(
            temp_pdf.name
        )

        text = ""

        #
        # First page is enough
        #

        if len(doc) > 0:

            text = ""

            for page_num in range(
                min(3, len(doc))
            ):
                text += (
                    doc[page_num]
                    .get_text()
                    + "\n"
                )

        doc.close()

    text_upper = text.upper()

    #
    # JUNE 18, 2026
    #

    match = re.search(
        r"(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s+(\d{1,2}),?\s+(\d{4})",
        text_upper
    )

    if match:

        month_name, day, year = match.groups()

        month_map = {

            "JANUARY": 1,
            "FEBRUARY": 2,
            "MARCH": 3,
            "APRIL": 4,
            "MAY": 5,
            "JUNE": 6,
            "JULY": 7,
            "AUGUST": 8,
            "SEPTEMBER": 9,
            "OCTOBER": 10,
            "NOVEMBER": 11,
            "DECEMBER": 12

        }

        return datetime(
            int(year),
            month_map[month_name],
            int(day)
        ).date()

    #
    # 19 JUNE 2026
    # 19 JUNE, 2026
    #

    match = re.search(
        r"(\d{1,2})\s+(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER),?\s+(\d{4})",
        text_upper
    )

    if match:

        day, month_name, year = match.groups()

        month_map = {

            "JANUARY": 1,
            "FEBRUARY": 2,
            "MARCH": 3,
            "APRIL": 4,
            "MAY": 5,
            "JUNE": 6,
            "JULY": 7,
            "AUGUST": 8,
            "SEPTEMBER": 9,
            "OCTOBER": 10,
            "NOVEMBER": 11,
            "DECEMBER": 12

        }

        return datetime(
            int(year),
            month_map[month_name],
            int(day)
        ).date()

    return None

def download_hindu_pdf(newspaper_name="The Hindu"):

    today = date.today().isoformat()

    safe_name = (
        newspaper_name
        .lower()
        .replace(" ", "_")
    )

    filename = f"{safe_name}_{today}.pdf"
    filepath = DOWNLOAD_DIR / filename

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/137.0.0.0 Safari/537.36"
            )
        )

        #
        # PAGE 1
        #

        page1 = context.new_page()

        print("Opening Indiags...")

        for attempt in range(3):
            try:

                page1.goto(
                    "https://www.indiags.com/epaper-pdf-download",
                    wait_until="domcontentloaded",
                    timeout=60000
                )

                page1.locator(
                    "div.card-d-s-title"
                ).first.wait_for(
                    state="visible",
                    timeout=30000
                )

                break

            except Exception as e:

                print(
                    f"Page load failed (attempt {attempt + 1}/3): {e}"
                )

                if attempt == 2:

                    raise

                page1.wait_for_timeout(5000)

        #
        # STEP 1
        # FIND THE HINDU CARD
        #

        print(
            f"Looking for {newspaper_name}..."
        )

        titles = page1.locator(
            "div.card-d-s-title"
        )

        card_count = titles.count()

        print(
            f"Found {card_count} newspaper cards."
        )

        target_index = None

        for i in range(card_count):

            text = titles.nth(i).inner_text().strip()

            print(
                f"{i}: {text}"
            )

            if text.strip().lower() == newspaper_name.lower():

                target_index = i

                break

        if target_index is None:

            raise Exception(
                f"{newspaper_name} card not found."
            )

        print(
            f"Found {newspaper_name} at index {target_index}"
        )

        read_buttons = page1.locator(
            "a.btn-read"
        )

        with context.expect_page() as page2_info:

            read_buttons.nth(
                target_index
            ).click()

        page2 = page2_info.value

        page2.wait_for_load_state()

        print(
            "Page2:",
            page2.url
        )

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
            wait_until="load",
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
        # VERIFY PAPER DATE
        #

        pdf_filename = unquote(
            pdf_url.split("/")[-1]
        )

        print(
            f"PDF filename: {pdf_filename}"
        )

        #
        # Extract date from filename
        #
        # Supports:
        # 18~06~2026
        # 18_06_2026
        # 18-06-2026
        # 18.06.2026
        # 2026_06_18
        #

        date_patterns = [

            r"(\d{2})[~_.-](\d{2})[~_.-](\d{4})",

            r"(\d{4})[~_.-](\d{2})[~_.-](\d{2})",

        ]

        match = None

        for pattern in date_patterns:

            match = re.search(
                pattern,
                pdf_filename
            )

            if match:

                break

        pdf_content = None

        #
        # DATE FOUND IN FILENAME
        #

        if match:

            groups = match.groups()

            if len(groups[0]) == 4:

                year, month, day = groups
            
            else:

                day, month, year = groups
            
            paper_date = datetime(
                int(year),
                int(month),
                int(day)
            ).date()
        
        #
        # FALLBACK TO PDF TEXT
        #

        else:

            print(
                "No date found in filename."
            )

            print(
                "Falling back to PDF text extraction..."
            )

            response = requests.get(
                pdf_url,
                timeout=120
            )

            response.raise_for_status()

            pdf_content = response.content

            paper_date = extract_date_from_pdf(
                pdf_content
            )

            if not paper_date:

                raise Exception(
                    f"Could not determine date from filename or PDF: {pdf_filename}"
                )

        today_ist = datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).date()

        print(
            f"Paper date: {paper_date}"
        )

        print(
            f"Today's date: {today_ist}"
        )

        if paper_date != today_ist:

            raise Exception(
                f"Paper date mismatch. "
                f"Expected {today_ist}, "
                f"got {paper_date}"
            )

        print(
            "Paper date verified."
        )

        #
        # DOWNLOAD PDF only if not already downloaded
        #

        if pdf_content is None:

            response = requests.get(
                pdf_url,
                timeout=120
            )

            response.raise_for_status()

            pdf_content = response.content
        
        with open(filepath, "wb") as f:

            f.write(pdf_content)

        print(
            f"Saved PDF: {filepath}"
        )

        size_mb = filepath.stat().st_size / (1024 * 1024)

        print(
            f"PDF size: {size_mb:.2f} MB"
        )

        if size_mb > 40:

            print("PDF size exceeds 40 MB. Compressing...")

            filepath = compress_pdf(filepath)
        
        else:

            print("PDF size is within limits. No compression needed.")

        browser.close()

        return filepath

def compress_pdf(input_path: Path) -> Path:

    output_path = input_path.with_name(
        input_path.stem + "_compressed.pdf"
    )

    doc = fitz.open(input_path)

    doc.save(
        output_path,
        garbage=4,
        deflate=True,
        clean=True
    )

    doc.close()

    original = input_path.stat().st_size / (1024 * 1024)
    compressed = output_path.stat().st_size / (1024 * 1024)
    saved = original - compressed
    percent_saved = (saved / original) * 100 if original > 0 else 0

    print(f"Original PDF: {original:.2f} MB")
    print(f"Compressed PDF: {compressed:.2f} MB")
    print(f"Space saved: {saved:.2f} MB ({percent_saved:.2f}%)")

    return output_path