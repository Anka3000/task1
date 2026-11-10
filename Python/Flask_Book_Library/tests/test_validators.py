"""Testy jednostkowe walidacji danych wejściowych (ochrona przed stored XSS).

Uruchomienie (w katalogu Flask_Book_Library):
    python -m unittest discover -s tests -v
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from project.validators import (  # noqa: E402
    validate_text, validate_year, validate_age, validate_book_type,
)
from project.books.models import Book  # noqa: E402
from project.customers.models import Customer  # noqa: E402


XSS_PAYLOADS = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert(1)>",
    "<svg/onload=alert(1)>",
    "\"><script>alert(1)</script>",
    "Harry Potter<script>",
    "javascript:alert(1)//",
    "<iframe src=javascript:alert(1)>",
    "Tom &amp; Jerry",
]

VALID_TEXTS = [
    "Harry Potter",
    "Pan Tadeusz",
    "Zażółć gęślą jaźń",
    "J.R.R. Tolkien",
    "O'Brien",
    "Kraków-Podgórze",
    "Catch-22: A Novel (1st edition)",
    "Who Moved My Cheese?",
]


class ValidateTextTests(unittest.TestCase):
    def test_accepts_valid_text(self):
        for text in VALID_TEXTS:
            with self.subTest(text=text):
                self.assertEqual(validate_text(text, 'Name'), text)

    def test_strips_whitespace(self):
        self.assertEqual(validate_text("  Dune  ", 'Name'), "Dune")

    def test_rejects_xss_payloads(self):
        for payload in XSS_PAYLOADS:
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    validate_text(payload, 'Name')

    def test_rejects_empty_and_whitespace(self):
        for value in ["", "   "]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_text(value, 'Name')

    def test_rejects_too_long_text(self):
        validate_text("a" * 64, 'Name')
        with self.assertRaises(ValueError):
            validate_text("a" * 65, 'Name')

    def test_rejects_non_string(self):
        for value in [None, 123, ["a"]]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_text(value, 'Name')


class ValidateNumbersTests(unittest.TestCase):
    def test_year(self):
        self.assertEqual(validate_year("1999"), 1999)
        self.assertEqual(validate_year(2020), 2020)
        for value in ["abc", "<script>", -5, 0, 99999, None, True]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_year(value)

    def test_age(self):
        self.assertEqual(validate_age("30"), 30)
        for value in ["abc", "<b>1</b>", 0, -1, 200, None]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_age(value)

    def test_book_type(self):
        for value in ["2days", "5days", "10days"]:
            self.assertEqual(validate_book_type(value), value)
        for value in ["7days", "<script>alert(1)</script>", "", None]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_book_type(value)


class BookModelTests(unittest.TestCase):
    def test_creates_valid_book(self):
        book = Book(name="Pan Tadeusz", author="Adam Mickiewicz", year_published="1834", book_type="5days")
        self.assertEqual(book.name, "Pan Tadeusz")
        self.assertEqual(book.year_published, 1834)

    def test_rejects_xss_in_name(self):
        with self.assertRaises(ValueError):
            Book(name="<script>alert('XSS')</script>", author="Test", year_published=2020, book_type="2days")

    def test_rejects_xss_in_author(self):
        with self.assertRaises(ValueError):
            Book(name="Test", author="<img src=x onerror=alert(1)>", year_published=2020, book_type="2days")

    def test_rejects_xss_on_edit(self):
        book = Book(name="Dune", author="Frank Herbert", year_published=1965, book_type="10days")
        with self.assertRaises(ValueError):
            book.name = "<script>alert(1)</script>"
        self.assertEqual(book.name, "Dune")


class CustomerModelTests(unittest.TestCase):
    def test_creates_valid_customer(self):
        customer = Customer(name="Jan Kowalski", city="Kraków", age="25")
        self.assertEqual(customer.city, "Kraków")
        self.assertEqual(customer.age, 25)

    def test_rejects_xss_in_name_and_city(self):
        with self.assertRaises(ValueError):
            Customer(name="<script>alert(1)</script>", city="Warszawa", age=30)
        with self.assertRaises(ValueError):
            Customer(name="Jan", city="<svg/onload=alert(1)>", age=30)


if __name__ == '__main__':
    unittest.main()
