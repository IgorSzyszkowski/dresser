import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ClothingItem:
    """Represents a single clothing item with its environmental and temperature attributes.

    Attributes:
        name (str): Display name of the clothing item.
        category (str): Category classification (e.g., 'top_base', 'outerwear', 'footwear').
        min_temp (float): Minimum suitable operating temperature in Celsius.
        max_temp (float): Maximum suitable operating temperature in Celsius.
        waterproof (bool): Indicates if the item offers water resistance/waterproofing.
        snowproof (bool): Indicates if the item offers snow resistance.
        sun_protection (bool): Indicates if the item provides UV/sun protection.
    """

    name: str
    category: str
    min_temp: float
    max_temp: float
    waterproof: bool
    snowproof: bool
    sun_protection: bool


class Wardrabe:
    """Manages a collection of clothing items loaded from storage and provides filtering utilities.

    Attributes:
        items (list[ClothingItem]): The list of all available clothing items loaded into the wardrobe.
    """

    items: list[ClothingItem]

    def __init__(self) -> None:
        """Initializes the Wardrabe instance by loading items from the local configuration file."""
        self.items = self._get_items()

    def _get_items(self) -> list[ClothingItem]:
        """Reads and deserializes clothing items from the 'wardrabe.json' file.

        Returns:
            list[ClothingItem]: A list of instantiated ClothingItem objects.

        Raises:
            FileNotFoundError: If 'wardrabe.json' does not exist in the script's directory.
            json.JSONDecodeError: If the JSON file contains invalid syntax.
        """
        path = Path(__file__).parent / "wardrabe.json"
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return [ClothingItem(**item) for item in data]

    def items_by_category(
        self, clothes: list[ClothingItem], category: str
    ) -> list[ClothingItem]:
        """Filters a list of clothing items by a specific category.

        Args:
            clothes (list[ClothingItem]): The collection of clothing items to filter.
            category (str): The category name to match (e.g., 'outerwear').

        Returns:
            list[ClothingItem]: A list of items matching the specified category.
        """
        return [item for item in clothes if item.category == category]

    def items_waterproof(
        self, clothes: list[ClothingItem], waterproof: bool
    ) -> list[ClothingItem]:
        """Filters a list of clothing items based on their waterproof attribute.

        Args:
            clothes (list[ClothingItem]): The collection of clothing items to filter.
            waterproof (bool): If True, returns items where `waterproof` is True;
                if False, returns items where `waterproof` is False.

        Returns:
            list[ClothingItem]: Filtered list of clothing items matching the waterproof criteria.
        """
        return [
            item
            for item in clothes
            if (item.waterproof if waterproof else (not item.waterproof))
        ]

    def items_snowproof(
        self, clothes: list[ClothingItem], snowproof: bool
    ) -> list[ClothingItem]:
        """Filters a list of clothing items based on their snowproof attribute.

        Args:
            clothes (list[ClothingItem]): The collection of clothing items to filter.
            snowproof (bool): If True, returns items where `snowproof` is True;
                if False, returns items where `snowproof` is False.

        Returns:
            list[ClothingItem]: Filtered list of clothing items matching the snowproof criteria.
        """
        return [
            item
            for item in clothes
            if (item.snowproof if snowproof else (not item.snowproof))
        ]
