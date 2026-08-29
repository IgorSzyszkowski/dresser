"""GUI module for the Dresser application using CustomTkinter."""

from datetime import datetime, timedelta

import customtkinter
from deep_translator import GoogleTranslator

from dresser.get_clothes import ClothingItem
from dresser.select_clothes import Selector


class App(customtkinter.CTk):
    """Main application window for selecting clothes based on location and time range."""

    def __init__(self) -> None:
        """Initialize the application layout, input fields, and UI components."""
        super().__init__()

        self.title("Dresser")
        self.geometry("1200x800")
        self.grid_columnconfigure((0, 1, 2), weight=1)

        self.label = customtkinter.CTkLabel(
            self,
            text="Dresser - clothes selector",
            font=("Arial", 60, "bold"),
            text_color="#ffffff",
        )
        self.label.grid(
            row=0, column=0, padx=20, pady=(20, 50), sticky="ew", columnspan=3
        )

        self.sub_label_1 = customtkinter.CTkLabel(
            self,
            text="city",
            font=("Arial", 36, "bold"),
            text_color="#ffffff",
            bg_color="#383838",
        )
        self.sub_label_1.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.sub_label_2 = customtkinter.CTkLabel(
            self,
            text="start time",
            font=("Arial", 36, "bold"),
            text_color="#ffffff",
            bg_color="#383838",
        )
        self.sub_label_2.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.sub_label_3 = customtkinter.CTkLabel(
            self,
            text="end time",
            font=("Arial", 36, "bold"),
            text_color="#ffffff",
            bg_color="#383838",
        )
        self.sub_label_3.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

        self.entry_city = customtkinter.CTkEntry(self, font=("Arial", 36, "bold"))
        self.entry_city.grid(row=2, column=0, padx=15, pady=5, sticky="ew")

        self.entry_start = customtkinter.CTkEntry(self, font=("Arial", 36, "bold"))
        self.entry_start.insert(
            0,
            datetime.now(tz=datetime.now().astimezone().tzinfo).strftime(
                r"%Y-%m-%d %H:%M"
            ),
        )
        self.entry_start.grid(row=2, column=1, padx=15, pady=5, sticky="ew")

        self.entry_end = customtkinter.CTkEntry(self, font=("Arial", 36, "bold"))
        self.entry_end.insert(
            0,
            (
                datetime.now(tz=datetime.now().astimezone().tzinfo) + timedelta(hours=1)
            ).strftime(r"%Y-%m-%d %H:%M"),
        )
        self.entry_end.grid(row=2, column=2, padx=15, pady=5, sticky="ew")

        self.submit_button = customtkinter.CTkButton(
            self,
            text="submit",
            font=("Arial", 44, "bold"),
            text_color="#ffffff",
            bg_color="#0a0245",
            command=self.button_callback,
        )
        self.submit_button.grid(row=3, column=1, pady=30, sticky="ew")

        self.result_label = customtkinter.CTkLabel(
            self,
            text="",
            font=("Arial", 50, "bold"),
            text_color="#ffffff",
            justify="left",
        )
        self.result_label.grid(
            row=4, column=0, pady=30, padx=30, columnspan=3, sticky="w"
        )

    def button_callback(self) -> None:
        """Handle submit action by processing user input and rendering clothing recommendations."""
        try:
            city, start, end = (
                self.entry_city.get(),
                self.entry_start.get(),
                self.entry_end.get(),
            )
            selector = Selector(city, start, end)
            clothes = selector.select_clothes()
            items_str = self.get_items_str(clothes)
            self.result_label.configure(text=items_str)
        except ValueError as e:
            self.result_label.configure(text=str(e))

    def get_items_str(
        self, clothes: dict[str, ClothingItem | list[str]], pl: bool = False
    ) -> str:
        """Format selected clothing items into a structured string representation.

        Args:
            clothes: Dictionary mapping clothing categories to items or accessory lists.
            pl: Whether to translate the output string to Polish.

        Returns:
            A formatted string listing recommended clothing items for each category.
        """
        translator = GoogleTranslator(source="en", target="pl")
        items_str = ""
        categories = ["top_base", "top_mid", "outerwear", "bottoms", "footwear"]

        for key in categories:
            item = clothes.get(key, None)
            name = item.name if isinstance(item, ClothingItem) else None
            items_str += (
                f"{key if key.count('_') == 0 else ' '.join(key.split('_'))}: {name}\n"
            )

        items_str += "accessories: "
        accessories = clothes.get("accessories", [])
        if isinstance(accessories, list) and accessories:
            items_str += ", ".join(accessories)
        else:
            items_str += f"{None}"

        return translator.translate(items_str) if pl else items_str
