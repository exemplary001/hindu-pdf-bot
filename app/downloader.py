import re
import requests
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import fitz
from playwright.sync_api import sync_playwright

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


def extract_date_from_pdf(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""

    # First 3 pages are checked
    if len(doc) > 0:
        for page_num in range(min(3, len(doc))):
            text += doc[page_num].get_text() + "\n"

    doc.close()

    text_upper = text.upper()

    # Format: JUNE 18, 2026
    match = re.search(
        r"(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s+(\d{1,2}),?\s+(\d{4})",
        text_upper,
    )

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
        "DECEMBER": 12,
    }

    if match:
        month_name, day, year = match.groups()
        return datetime(int(year), month_map[month_name], int(day)).date()

    # Format: 19 JUNE 2026 / 19 JUNE, 2026
    match = re.search(
        r"(\d{1,2})\s+(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER),?\s+(\d{4})",
        text_upper,
    )

    if match:
        day, month_name, year = match.groups()
        return datetime(int(year), month_map[month_name], int(day)).date()

    return None


def download_hindu_pdf(newspaper_name="The Hindu"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        try:
            context = browser.new_context(
                viewport={"width": 1366, "height": 768},
                accept_downloads=True,
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/137.0.0.0 Safari/537.36"
                ),
            )

            # --- PAGE 1 ---
            page1 = context.new_page()
            print("Opening Indiags...")

            for attempt in range(3):
                try:
                    page1.goto(
                        "https://www.indiags.com/epaper-pdf-download",
                        wait_until="domcontentloaded",
                        timeout=60000,
                    )
                    page1.locator("div.ep-card").first.wait_for(
                        state="visible", timeout=30000
                    )
                    break
                except Exception as e:
                    print(f"Page load failed (attempt {attempt + 1}/3): {e}")
                    if attempt == 2:
                        raise
                    page1.wait_for_timeout(5000)

            # --- STEP 1: FIND NEWSPAPER CARD ---
            print(f"Looking for {newspaper_name}...")
            cards = page1.locator("div.ep-card")
            card_count = cards.count()
            print(f"Found {card_count} newspaper cards.")

            target_card = None
            for i in range(card_count):
                card = cards.nth(i)
                title = (card.locator("p.ttl").text_content() or "").strip()
                print(f"{i}: {title}")

                if title.casefold() == newspaper_name.casefold():
                    target_card = card
                    print(f"Found {newspaper_name} at index {i}")
                    break

            if target_card is None:
                raise Exception(f"{newspaper_name} not found on the page.")

            href = target_card.locator("a.ep-read").get_attribute("href")
            print(f"Read href: {href}")

            target_card.locator("a.ep-read").click()
            page1.wait_for_load_state("domcontentloaded")

            page2 = page1
            print("Page2:", page2.url)

            # --- STEP 2: READ NEWSPAPER ---
            download_link = page2.locator(
                "a.ep-cta-btn:has-text('Download Newspaper')"
            )
            download_link.wait_for(state="visible", timeout=30000)
            download_link.click()

            page2.wait_for_load_state("domcontentloaded")
            page2.wait_for_timeout(1000)

            page3 = page2
            print("Page3:", page3.url)

            # --- STEP 3: UNLOCK VIA QUIZ ---
            unlock_link = page3.locator("a.pm-cta:has-text('Unlock via Quiz')")
            unlock_link.wait_for(state="visible", timeout=30000)
            unlock_link.click()

            page3.wait_for_load_state("domcontentloaded")
            page3.wait_for_timeout(1000)

            page4 = page3
            print("Page4:", page4.url)

            # --- WAIT 15 SECONDS ---
            print("Waiting 15 seconds...")
            for i in range(15, 0, -1):
                print(
                    f"\r{i:2d} seconds remaining...",
                    end="",
                    flush=True,
                )
                page4.wait_for_timeout(1000)

            print("\rDone!                      \n")

            # --- DOWNLOAD PDF ---
            download_button = page4.locator("#manualDownloadBtn")
            download_button.wait_for(state="visible", timeout=60000)

            print("Downloading PDF...")
            href = download_button.get_attribute("href")
            print("Download URL:", href)

            temp_filepath = DOWNLOAD_DIR / "temp_download.pdf"

            if temp_filepath.exists():
                temp_filepath.unlink()

            print("Downloading PDF using requests...")
            cookies = context.cookies()

            cookie_header = "; ".join(
                f"{cookie['name']}={cookie['value']}" for cookie in cookies
            )

            response = requests.get(
                href,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/137.0.0.0 Safari/537.36"
                    ),
                    "Referer": page4.url,
                    "Cookie": cookie_header,
                },
                timeout=120,
                allow_redirects=True,
            )

            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "").lower()

            if "pdf" not in content_type:
                raise Exception(
                    f"Expected a PDF but got {content_type}."
                )

            if not response.content.startswith(b"%PDF"):
                raise Exception(
                    "Downloaded file does not appear to be a valid PDF."
                )

            with open(temp_filepath, "wb") as f:
                f.write(response.content)

            print(f"Saved PDF: {temp_filepath}")
            print(f"Downloaded {len(response.content) / (1024 * 1024):.2f} MB")

            # --- VERIFY & COMPRESS ---
            pdf_content = temp_filepath.read_bytes()
            paper_date = extract_date_from_pdf(pdf_content)

            if not paper_date:
                raise Exception(
                    f"Could not determine date from PDF: {temp_filepath.name}"
                )

            today_ist = datetime.now(ZoneInfo("Asia/Kolkata")).date()

            print(f"Paper date: {paper_date}")
            print(f"Today's date: {today_ist}")

            if paper_date != today_ist:
                raise Exception(
                    f"Paper date mismatch. Expected {today_ist}, got {paper_date}"
                )

            print("Paper date verified.")

            filename = response.headers.get(
                "Content-Disposition",
                f'attachment; filename="{newspaper_name}.pdf"',
                )

            match = re.search(r'filename="?([^"]+)"?', filename)

            if match:
                final_filename = match.group(1)
            else:
                final_filename = f"{newspaper_name}.pdf"

            final_filepath = DOWNLOAD_DIR / final_filename

            
            if final_filepath.exists():
                final_filepath.unlink()
            
            temp_filepath.rename(final_filepath)
            filepath = final_filepath

            print(f"Renamed PDF to: {filepath.name}")

            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"PDF size: {size_mb:.2f} MB")

            if size_mb > 40:
                print("PDF size exceeds 40 MB. Compressing...")
                filepath = compress_pdf(filepath)
            else:
                print("PDF size is within limits. No compression needed.")

            return filepath

        finally:
            browser.close()


def compress_pdf(input_path: Path) -> Path:
    output_path = input_path.with_name(input_path.stem + "_compressed.pdf")

    doc = fitz.open(input_path)
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()

    original = input_path.stat().st_size / (1024 * 1024)
    compressed = output_path.stat().st_size / (1024 * 1024)
    saved = original - compressed
    percent_saved = (saved / original) * 100 if original > 0 else 0

    print(f"Original PDF: {original:.2f} MB")
    print(f"Compressed PDF: {compressed:.2f} MB")
    print(f"Space saved: {saved:.2f} MB ({percent_saved:.2f}%)")

    return output_path