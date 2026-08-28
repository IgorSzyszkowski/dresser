from dresser.get_weather import get_weather
from dresser.get_clothes import ClothingItem, Wardrabe
import pandas as pd
from math import prod

class Selector:
    city: str
    start_time: str
    end_time: str
    wardrabe: Wardrabe
    min_temperature: float
    precipitation_probability: float
    max_snow_depth: float

    def __init__(self, city: str, start_time: str, end_time: str):
        self.city = city
        self.start_time = start_time
        self.end_time = end_time
        self.wardrabe = Wardrabe()
        data_df = get_weather(city, start_time, end_time)
        self.calculate_weather_attributes(data_df)

    def calculate_weather_attributes(self, data: pd.DataFrame) -> None:
        self.min_temperature = data["apparent_temperature"].min()
        self.max_snow_depth = data["snow_depth"].max()
        self.precipitation_probability = 1 - prod([(1 - (num / 100)) for num in data["precipitation_probability"]])

    def __str__(self) -> str:
        return (
            f"Selector for {self.city} ({self.start_time} - {self.end_time}):\n"
            f"  • Min. temperature: {self.min_temperature}°C\n"
            f"  • Precipitation probability: {self.precipitation_probability * 100}%\n"
            f"  • Max. snow depth: {self.max_snow_depth * 100}cm"
        )

    def select_clothes(self) -> dict[str, ClothingItem | list[ClothingItem]]:
        result_dict = {}
        all_items = self.wardrabe.items
        waterproof_items = self.wardrabe.items_waterproof(all_items, True)
        not_waterproof_items = self.wardrabe.items_waterproof(all_items, False)
        snowproof_items = self.wardrabe.items_snowproof(all_items, True)
        not_snowproof_items = self.wardrabe.items_snowproof(all_items, False)
        for category in ["top_base", "bottoms"]:
            category_items = self.wardrabe.items_by_category(all_items, category)
            self.assign_item(result_dict, category_items, category)
        top_mid_items = self.wardrabe.items_by_category(waterproof_items, "top_mid") if self.precipitation_probability >= 0.3 else self.wardrabe.items_by_category(not_waterproof_items, "top_mid")
        self.assign_item(result_dict, top_mid_items, "top_mid")
        outer_items = self.wardrabe.items_by_category(waterproof_items, "outerwear") if self.precipitation_probability >= 0.3 else self.wardrabe.items_by_category(not_waterproof_items, "outerwear")
        self.assign_item(result_dict, outer_items, "outerwear")
        footwear_items = self.wardrabe.items_by_category(snowproof_items, "footwear") if self.max_snow_depth >= 0.03 else self.wardrabe.items_by_category(not_snowproof_items, "footwear")
        if len(footwear_items) == 1:
            result_dict["footwear"] = footwear_items[0]
        else:
            self.assign_item(result_dict, footwear_items, "footwear")
        result_dict["accessories"] = []
        accessories = self.wardrabe.items_by_category(all_items, "accessories")
        for acc in filter(lambda x: x.min_temp <= self.min_temperature < x.max_temp, accessories):
            result_dict["accessories"].append(acc.name)
        return result_dict


    def assign_item(self, result_dict: dict[str, ClothingItem], items: list[ClothingItem], category: str):
        if result := next(filter(lambda x: x.min_temp <= self.min_temperature < x.max_temp, items), None):
            result_dict[category] = result