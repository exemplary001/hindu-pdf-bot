from datetime import date

from app.state import (
    get_last_successful_date,
    save_successful_date
)

print(
    "Before:",
    get_last_successful_date()
)

save_successful_date(
    str(date.today())
)

print(
    "After:",
    get_last_successful_date()
)