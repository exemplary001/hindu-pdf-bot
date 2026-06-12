from pathlib import Path

from app.sender import send_pdf

send_pdf(
    Path(
        "downloads/hindu_2026-06-12.pdf"
    )
)