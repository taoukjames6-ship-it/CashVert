"""
Unit & Currency Converter
A single-file BeeWare (Toga) app.
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN
import requests

# ---- Unit conversion data (offline, no API needed, no cost) ----
LENGTH_UNITS = {
    "Meters": 1.0,
    "Kilometers": 1000.0,
    "Miles": 1609.34,
    "Feet": 0.3048,
    "Inches": 0.0254,
}

WEIGHT_UNITS = {
    "Kilograms": 1.0,
    "Grams": 0.001,
    "Pounds": 0.453592,
    "Ounces": 0.0283495,
}

CATEGORIES = {
    "Length": LENGTH_UNITS,
    "Weight": WEIGHT_UNITS,
    "Currency": None,  # handled separately, uses a free live-rate API
}

CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "INR"]


class ConverterApp(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name)

        # --- Widgets ---
        self.category_select = toga.Selection(
            items=list(CATEGORIES.keys()),
            on_change=self.on_category_change,
            style=Pack(padding=5),
        )

        # Initialize with Length units (will be updated when category changes)
        self.from_select = toga.Selection(items=list(LENGTH_UNITS.keys()), style=Pack(padding=5))
        self.to_select = toga.Selection(items=list(LENGTH_UNITS.keys()), style=Pack(padding=5))

        self.value_input = toga.TextInput(placeholder="Enter a number", style=Pack(padding=5))

        self.convert_button = toga.Button(
            "Convert", on_press=self.do_convert, style=Pack(padding=10)
        )

        self.result_label = toga.Label("Result will appear here", style=Pack(padding=10))

        # --- Layout ---
        box = toga.Box(
            children=[
                toga.Label("Category:", style=Pack(padding=(10, 5, 0, 5))),
                self.category_select,
                toga.Label("From:", style=Pack(padding=(10, 5, 0, 5))),
                self.from_select,
                toga.Label("To:", style=Pack(padding=(10, 5, 0, 5))),
                self.to_select,
                toga.Label("Value:", style=Pack(padding=(10, 5, 0, 5))),
                self.value_input,
                self.convert_button,
                self.result_label,
            ],
            style=Pack(direction=COLUMN, padding=15),
        )

        self.main_window.content = box

        # Set sensible defaults so the UI is initialized and avoid None values
        # Set category to first key (Length), then populate units and set defaults
        first_category = list(CATEGORIES.keys())[0]
        self.category_select.value = first_category
        # Trigger the on_category_change handler to populate from/to lists
        self.on_category_change(None)

        self.main_window.show()

    def on_category_change(self, widget):
        category = self.category_select.value
        if category == "Currency":
            self.from_select.items = CURRENCIES
            self.to_select.items = CURRENCIES
        else:
            units = list(CATEGORIES[category].keys())
            self.from_select.items = units
            self.to_select.items = units

        # set the from/to default values to the first item if unset
        if not self.from_select.value and len(self.from_select.items) > 0:
            self.from_select.value = self.from_select.items[0]
        if not self.to_select.value and len(self.to_select.items) > 0:
            self.to_select.value = self.to_select.items[0]

    def do_convert(self, widget):
        try:
            value = float(self.value_input.value)
        except (TypeError, ValueError):
            self.result_label.text = "Please enter a valid number."
            return

        category = self.category_select.value
        from_unit = self.from_select.value
        to_unit = self.to_select.value

        if not from_unit or not to_unit:
            self.result_label.text = "Please select units."
            return

        if category == "Currency":
            self.result_label.text = "Fetching live rate..."
            try:
                # frankfurter.app is a free, no-API-key exchange rate service
                url = f"https://api.frankfurter.app/latest?amount={value}&from={from_unit}&to={to_unit}"
                response = requests.get(url, timeout=8)
                response.raise_for_status()
                data = response.json()
                converted = data["rates"][to_unit]
                self.result_label.text = f"{value} {from_unit} = {converted:.2f} {to_unit}"
            except Exception:
                self.result_label.text = "Couldn't fetch live rate. Check your internet connection."
        else:
            units = CATEGORIES[category]
            base_value = value * units[from_unit]
            converted = base_value / units[to_unit]
            self.result_label.text = f"{value} {from_unit} = {converted:.4f} {to_unit}"


def main():
    # Keep the bundle id consistent with pyproject.toml
    return ConverterApp("CashVert", "com.james.cashvert")


if __name__ == "__main__":
    main().main_loop()
