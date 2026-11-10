"""Walidacja danych wejściowych na poziomie modeli domenowych.

Każda wartość tekstowa trafiająca do bazy musi przejść przez whitelistę znaków,
dzięki czemu nie da się zapisać znaczników HTML/JavaScript (ochrona przed
stored XSS). Funkcje rzucają ValueError, gdy dane są niepoprawne.
"""
import re
from datetime import date

MAX_TEXT_LENGTH = 64

# Dozwolone: litery (także polskie i inne Unicode), cyfry, spacja oraz . , ' - : ! ? ( )
# Niedozwolone są m.in. < > " ; & / \ = ` – czyli znaki potrzebne do wstrzyknięcia HTML/JS.
SAFE_TEXT_PATTERN = re.compile(r"^[^\W_](?:[^\W_]|[ .,'\-:!?()])*$")

ALLOWED_BOOK_TYPES = {"2days", "5days", "10days"}


def validate_text(value, field_name, max_length=MAX_TEXT_LENGTH):
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a text value")
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name} cannot be empty")
    if len(value) > max_length:
        raise ValueError(f"{field_name} cannot be longer than {max_length} characters")
    if not SAFE_TEXT_PATTERN.match(value):
        raise ValueError(
            f"{field_name} contains forbidden characters "
            "(allowed: letters, digits, spaces and . , ' - : ! ? ( ))"
        )
    return value


def validate_int(value, field_name, min_value, max_value):
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be an integer")
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be an integer")
    if not min_value <= number <= max_value:
        raise ValueError(f"{field_name} must be between {min_value} and {max_value}")
    return number


def validate_year(value, field_name="Year published"):
    return validate_int(value, field_name, 1, date.today().year)


def validate_age(value, field_name="Age"):
    return validate_int(value, field_name, 1, 120)


def validate_book_type(value, field_name="Book type"):
    if value not in ALLOWED_BOOK_TYPES:
        raise ValueError(f"{field_name} must be one of: {', '.join(sorted(ALLOWED_BOOK_TYPES))}")
    return value
