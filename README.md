# Dresser

**Dresser** is a weather-based clothing selector. Give it a city and a time window, and it fetches the forecast, analyzes the conditions, and recommends what to wear from your own wardrobe — base layer, mid layer, outerwear, bottoms, footwear, and accessories.

## Features

- **Live forecasts** via the [Open-Meteo](https://open-meteo.com/) API — no API key required.
- **Geocoding** — resolves a city name to coordinates and timezone automatically.
- **Smart outfit selection** based on minimum apparent temperature, combined precipitation probability, and maximum snow depth over the window.
- **Personal wardrobe** defined in a simple JSON file.
- **Desktop GUI** built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).
- **Optional Polish translation** of the output via `deep-translator`.
- **HTTP caching and retries** (`requests-cache` + `retry-requests`) for fast, resilient forecast lookups.

## How it works

1. **`get_location`** resolves the city name to latitude, longitude, and timezone.
2. **`get_weather`** validates the requested time window (not in the past, within 16 days) and downloads hourly forecast data filtered to that window.
3. **`Selector`** aggregates the hourly data into `min_temperature`, `precipitation_probability`, and `max_snow_depth`.
4. **`Selector.select_clothes()`** filters your wardrobe by those numbers (waterproofing if precipitation risk ≥ 30%, snowproofing if snow depth ≥ 3 cm) and returns one item per category, plus matching accessories.
5. The **GUI** collects a city, start time, and end time, runs the selection, and displays the result.

## Requirements

- Python **>= 3.14**
- Dependencies (installed automatically): `customtkinter`, `deep-translator`, `numpy`, `pandas`, `requests`, `requests-cache`, `retry-requests`

## Installation

This project uses [uv](https://docs.astral.sh/uv/) with the `uv_build` backend.

```bash
git clone <repository-url>
cd dresser
uv sync
```

Alternatively, with plain `pip`:

```bash
pip install -e .
```

## Usage

### Run the GUI

```bash
uv run dresser
```

Or, without the console script:

```bash
python -m dresser
```

The window lets you enter:

| Field       | Format              | Notes                                   |
|-------------|---------------------|------------------------------------------|
| City        | e.g. `Krasnystaw`   | Any city known to Open-Meteo's geocoder |
| Start time  | `YYYY-MM-DD HH:MM`  | Defaults to the current local time      |
| End time    | `YYYY-MM-DD HH:MM`  | Defaults to start time + 1 hour         |

Click **submit** to see the recommended outfit for that window.

### Use the selector programmatically

```python
from dresser.select_clothes import Selector

selector = Selector("Krasnystaw", "2026-09-01 08:00", "2026-09-01 18:00")
print(selector)  # weather summary
outfit = selector.select_clothes()
print(outfit)
```

## Configuring your wardrobe

Clothing items are loaded from `dresser/wardrabe.json`, a list of objects matching the `ClothingItem` fields:

```json
[
  {
    "name": "Merino Wool T-Shirt",
    "category": "top_base",
    "min_temp": 10,
    "max_temp": 30,
    "waterproof": false,
    "snowproof": false,
    "sun_protection": false
  },
  {
    "name": "Rain Shell Jacket",
    "category": "outerwear",
    "min_temp": -5,
    "max_temp": 15,
    "waterproof": true,
    "snowproof": false,
    "sun_protection": false
  }
]
```

| Field            | Type    | Meaning                                                        |
|-------------------|---------|------------------------------------------------------------------|
| `name`            | string  | Display name                                                     |
| `category`        | string  | One of `top_base`, `top_mid`, `outerwear`, `bottoms`, `footwear`, `accessories` |
| `min_temp`        | float   | Lower bound (°C) of the item's comfortable temperature range     |
| `max_temp`        | float   | Upper bound (°C, exclusive) of that range                        |
| `waterproof`      | bool    | Whether the item repels rain                                     |
| `snowproof`       | bool    | Whether the item is suitable for snow                            |
| `sun_protection`  | bool    | Whether the item offers UV protection                            |

## Project structure

```
dresser/
├── __main__.py        # Entry point, launches the GUI
├── get_weather.py      # Geocoding + Open-Meteo forecast fetching
├── get_clothes.py      # ClothingItem model + Wardrabe loader/filters
├── select_clothes.py   # Selector: turns weather into an outfit
├── gui.py               # CustomTkinter application window
└── wardrabe.json        # Your personal clothing inventory
```

## Development

```bash
uv sync --group dev
uv run pytest        # run tests
uv run ruff check .  # lint
uv run mypy .         # type-check
```

## License

MIT License, Copyright (c) 2026 Igor Szyszkowski. See [LICENSE](LICENSE) for details.

## Author

Igor Szyszkowski — igo.szyszkowski@gmail.com