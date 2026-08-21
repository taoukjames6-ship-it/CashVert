"""
Unit & Currency Converter
A single-file BeeWare (Toga) app.

HOW TO RUN (for testing on your computer, no App Store needed):
1. Install Python 3.9+ from python.org (free)
2. Open a terminal and run:
       pip install toga requests
3. Save this file as: converter_app.py
4. Run it with:
       python converter_app.py

That's it — a window will open with the app running on your desktop.
Packaging it for iPhone/Android later is a separate step (see notes at
the bottom of this file).
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
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

    def do_convert(self, widget):
        try:
            value = float(self.value_input.value)
        except (TypeError, ValueError):
            self.result_label.text = "Please enter a valid number."
            return

        category = self.category_select.value
        from_unit = self.from_select.value
        to_unit = self.to_select.value

        if category == "Currency":
            self.result_label.text = "Fetching live rate..."
            try:
                # frankfurter.app is a free, no-API-key exchange rate service
                url = f"https://api.frankfurter.app/latest?amount={value}&from={from_unit}&to={to_unit}"
                response = requests.get(url, timeout=8)
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
    return ConverterApp("Unit & Currency Converter", "com.example.converter")


if __name__ == "__main__":
    main().main_loop()

# ---------------------------------------------------------------------
# NOTES ON ADS & PUBLISHING (read this before promising yourself revenue):
#
# 1. Apple doesn't run an in-app ad network anymore — iAd shut down in
#    2016. The two realistic options for ads are Google AdMob or Meta
#    Audience Network, and both require adding their native SDK to the
#    compiled iOS project. BeeWare/Toga has no official plugin for this,
#    so it would mean editing the generated Xcode project by hand —
#    a real coding task, not something this single Python file can do.
#
# 2. Publishing to the Apple App Store requires an Apple Developer
#    account, which costs $99/year — there's no free tier. That's a
#    hard cost you can't dodge if the goal is the iPhone App Store.
#
# 3. If "no money at all" is a firm constraint, Android is the cheaper
#    path (one-time $25 Google Play registration fee, not annual), or
#    you could skip app stores altogether and run this as a free website
#    (Toga can also target the web) with Google AdSense.
# ---------------------------------------------------------------------
