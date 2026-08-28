import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ClothingItem:
    name: str
    category: str
    min_temp: float
    max_temp: float
    waterproof: bool
    snowproof: bool
    sun_protection: bool


class Wardrabe:
    items: list[ClothingItem]

    def __init__(self):
        self.items = self._get_items()

    def _get_items(self) -> list[ClothingItem]:
        path = Path(__file__).parent / "wardrabe.json"
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return [ClothingItem(**item) for item in data]

    def items_by_category(self, clothes: list[ClothingItem], category: str) -> list[ClothingItem]:
        return [item for item in clothes if item.category == category]

    def items_waterproof(self, clothes: list[ClothingItem], waterproof: bool) -> list[ClothingItem]:
        return [item for item in clothes if (item.waterproof if waterproof else (not item.waterproof))]

    def items_snowproof(self, clothes: list[ClothingItem], snowproof: bool) -> list[ClothingItem]:
            return [item for item in clothes if (item.snowproof if snowproof else (not item.snowproof))]