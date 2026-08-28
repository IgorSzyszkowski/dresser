from dresser.get_weather import get_weather
from dresser.get_clothes import ClothingItem, Wardrabe
import pandas as pd
from math import prod

class Selector:
    city: str
    start_time: str
    end_time: str
    min_temperature: float
    precipitation_probability: float
    max_snow_depth: float

    def __init__(self, city: str, start_time: str, end_time: str):
        self.city = city
        self.start_time = start_time
        self.end_time = end_time
        data_df = get_weather(city, start_time, end_time)
        print(data_df)
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
            f"  • Max. snow depth: {self.max_snow_depth} cm"
        )