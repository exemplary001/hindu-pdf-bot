from playwright.sync_api import sync_playwright

URL = "https://www.indiags.com/epaper-pdf-download"

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False  # so you can see what's happening
    )

    page = browser.new_page()

    print(f"Opening {URL}")
    page.goto(URL, wait_until="networkidle")

    print("\n=== PAGE TITLE ===")
    print(page.title())

    print("\n=== LINKS ===")

    links = page.locator("a")

    for i in range(min(links.count(), 300)):
        try:
            link = links.nth(i)

            text = link.inner_text().strip()
            href = link.get_attribute("href")

            if text:
                print(f"\n[{i}]")
                print(f"TEXT : {text}")
                print(f"HREF : {href}")

        except Exception:
            pass

    print("\n=== BUTTONS ===")

    buttons = page.locator("button")

    for i in range(min(buttons.count(), 100)):
        try:
            btn = buttons.nth(i)

            text = btn.inner_text().strip()

            if text:
                print(f"\n[{i}] {text}")

        except Exception:
            pass

    print("\n=== KEYWORDS FOUND ===")

    keywords = [
        "hindu",
        "read",
        "newspaper",
        "quiz",
        "unlock",
        "download",
        "pdf"
    ]

    page_text = page.locator("body").inner_text().lower()

    for keyword in keywords:
        print(
            f"{keyword}: "
            f"{'FOUND' if keyword in page_text else 'NOT FOUND'}"
        )

    input(
        "\nPress ENTER to close browser..."
    )

    browser.close()