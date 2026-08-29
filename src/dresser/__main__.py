"""Main entry point for the Dresser application.

Launches the Graphical User Interface (GUI) for selecting outfits based on weather forecasts.
"""

from dresser.gui import App


def main() -> None:
    """Initializes and runs the Dresser CustomTkinter GUI application."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
