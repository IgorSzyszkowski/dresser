from math import prod

import pandas as pd

from dresser.get_clothes import ClothingItem, Wardrabe
from dresser.get_weather import get_weather


class Selector:
    """Selects suitable clothing items based on weather forecasts for a specified city and time window.

    Attributes:
        city (str): Name of the target city.
        start_time (str): Effective forecast start timestamp string.
        end_time (str): Effective forecast end timestamp string.
        hours (float): Time window duration in hours.
        wardrabe (Wardrabe): Instance of Wardrabe containing available clothing items.
        min_temperature (float): Minimum apparent temperature (°C) within the forecasted period.
        precipitation_probability (float): Combined probability of precipitation (0.0 to 1.0) over the time window.
        max_snow_depth (float): Maximum expected snow depth in meters.
    """

    city: str
    start_time: str
    end_time: str
    hours: float
    wardrabe: Wardrabe
    min_temperature: float
    precipitation_probability: float
    max_snow_depth: float

    def __init__(
        self, city: str, start_time: str = "", end_time: str = "", hours: float = 1
    ):
        """Initializes the Selector by fetching weather forecast data and populating weather attributes.

        Args:
            city (str): Name of the target city.
            start_time (str, optional): Start timestamp string in pandas-parseable format. Defaults to "".
            end_time (str, optional): End timestamp string. Defaults to "".
            hours (float, optional): Forecast duration in hours if end_time is omitted. Defaults to 1.
        """
        self.city = city
        self.hours = hours
        self.wardrabe = Wardrabe()
        data_df, self.start_time, self.end_time = get_weather(
            city, start_time, end_time, hours
        )
        self.calculate_weather_attributes(data_df)

    def calculate_weather_attributes(self, data: pd.DataFrame) -> None:
        """Calculates aggregated weather attributes from hourly forecast data.

        Computes the minimum apparent temperature, maximum snow depth, and overall
        combined probability of precipitation across all hourly entries.

        Args:
            data (pd.DataFrame): DataFrame containing hourly weather data with
                'apparent_temperature', 'snow_depth', and 'precipitation_probability' columns.
        """
        self.min_temperature = data["apparent_temperature"].min()
        self.max_snow_depth = data["snow_depth"].max()
        self.precipitation_probability = 1 - prod(
            [(1 - (num / 100)) for num in data["precipitation_probability"]]
        )

    def __str__(self) -> str:
        """Returns a human-readable summary of the weather parameters evaluated by Selector.

        Returns:
            str: Formatted string containing city name, time window, minimum temperature,
            precipitation probability, and max snow depth in centimeters.
        """
        return (
            f"Selector for {self.city} ({self.start_time} - {self.end_time}):\n"
            f"  • Min. temperature: {self.min_temperature}°C\n"
            f"  • Precipitation probability: {self.precipitation_probability * 100}%\n"
            f"  • Max. snow depth: {self.max_snow_depth * 100}cm"
        )

    def select_clothes(self) -> dict[str, ClothingItem | list[str]]:
        """Selects appropriate clothing items and accessories matching current forecast conditions.

        Evaluates temperature range, precipitation probability, and snow depth to choose base layer,
        bottoms, mid-layer, outerwear, footwear, and matching accessories.

        Returns:
            dict[str, ClothingItem | list[str]]: Dictionary mapping clothing categories
            ('top_base', 'bottoms', 'top_mid', 'outerwear', 'footwear', 'accessories') to
            matching ClothingItem instances or a list of accessory names.
        """
        result_dict: dict[str, ClothingItem | list[str]] = {}
        all_items = self.wardrabe.items
        waterproof_items = self.wardrabe.items_waterproof(all_items, True)
        not_waterproof_items = self.wardrabe.items_waterproof(all_items, False)
        snowproof_items = self.wardrabe.items_snowproof(all_items, True)
        not_snowproof_items = self.wardrabe.items_snowproof(all_items, False)

        for category in ["top_base", "bottoms"]:
            category_items = self.wardrabe.items_by_category(all_items, category)
            self.assign_item(result_dict, category_items, category)

        top_mid_items = (
            self.wardrabe.items_by_category(waterproof_items, "top_mid")
            if self.precipitation_probability >= 0.3
            else self.wardrabe.items_by_category(not_waterproof_items, "top_mid")
        )
        self.assign_item(result_dict, top_mid_items, "top_mid")

        outer_items = (
            self.wardrabe.items_by_category(waterproof_items, "outerwear")
            if self.precipitation_probability >= 0.3
            else self.wardrabe.items_by_category(not_waterproof_items, "outerwear")
        )
        self.assign_item(result_dict, outer_items, "outerwear")

        footwear_items = (
            self.wardrabe.items_by_category(snowproof_items, "footwear")
            if self.max_snow_depth >= 0.03
            else self.wardrabe.items_by_category(not_snowproof_items, "footwear")
        )
        if len(footwear_items) == 1:
            result_dict["footwear"] = footwear_items[0]
        else:
            self.assign_item(result_dict, footwear_items, "footwear")

        result_dict["accessories"] = []
        accessories = self.wardrabe.items_by_category(all_items, "accessories")
        result_dict["accessories"] = [
            acc.name
            for acc in accessories
            if acc.min_temp <= self.min_temperature < acc.max_temp
        ]

        return result_dict

    def assign_item(
        self,
        result_dict: dict[str, ClothingItem | list[str]],
        items: list[ClothingItem],
        category: str,
    ) -> None:
        """Finds and assigns the first clothing item matching the minimum apparent temperature.

        Args:
            result_dict (dict[str, ClothingItem]): Dictionary where the selected item will be stored.
            items (list[ClothingItem]): Candidate clothing items to filter from.
            category (str): Target category key to update in `result_dict`.
        """
        if result := next(
            filter(lambda x: x.min_temp <= self.min_temperature < x.max_temp, items),
            None,
        ):
            result_dict[category] = result
