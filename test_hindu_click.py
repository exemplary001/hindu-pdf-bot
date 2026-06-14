from playwright.sync_api import sync_playwright


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    context = browser.new_context()

    page = context.new_page()

    page.goto(
        "https://www.indiags.com/epaper-pdf-download"
    )

    page.wait_for_timeout(
        10000
    )

    titles = page.locator(
        "div.card-d-s-title"
    )

    count = titles.count()

    target_index = None

    for i in range(count):

        text = titles.nth(i).inner_text().strip()

        print(
            f"{i}: {text}"
        )

        if text == "The Hindu":

            target_index = i

            break

    if target_index is None:

        raise Exception(
            "The Hindu card not found."
        )

    print(
        f"\nFound The Hindu at index {target_index}"
    )

    read_buttons = page.locator(
        "a.btn-read"
    )

    with context.expect_page() as page2_info:

        read_buttons.nth(
            target_index
        ).click()

    page2 = page2_info.value

    page2.wait_for_load_state()

    print(
        "\nSUCCESS"
    )

    print(
        page2.url
    )

    input(
        "\nPress Enter..."
    )

    browser.close()