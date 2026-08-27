import pandas as pd
import requests
import requests_cache
from retry_requests import retry


def get_location(city_name: str, session: requests.Session) -> tuple[float, float, str]:
    """Retrieves geographic coordinates and timezone for a given city.

    Uses the free Open-Meteo Geocoding API.

    Args:
        city_name (str): Name of the target city (e.g., "Krasnystaw").
        session (requests.Session): HTTP session used to make the request.

    Returns:
        tuple[float, float, str]: A tuple containing:
            - Latitude (float),
            - Longitude (float),
            - Timezone identifier string (e.g., "Poland/Warsaw").

    Raises:
        ValueError: If the city is not found in the API database.
    """
    geo_URL = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"

    response = session.get(geo_URL).json()

    if "results" in response:
        location = response["results"][0]
        timezone = location.get("timezone", "UTC")
        coords = location["latitude"], location["longitude"], timezone
    else:
        raise ValueError(f"city {city_name} not found")

    return coords


def get_data(city_name, start: str, end: str) -> pd.DataFrame:
    """Fetches hourly weather forecast data from Open-Meteo for a specific city and date range.

    Validates the input date range (requires non-past dates, enforces a max 16-day 
    forecast limit) and filters the resulting DataFrame to the half-open interval [start, end).

    Args:
        city_name (str): Name of the city to retrieve forecast data for.
        start (str): Start date and time in a pandas-parseable format 
            (e.g., "YYYY-MM-DD HH:MM:SS AM/PM" or "YYYY-MM-DD HH:MM").
        end (str): End date and time.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing columns for local timestamps (`time`), 
            temperature at 2 meters (`temperature_2m`), and precipitation 
            probability (`precipitation_probability`).

    Raises:
        ValueError: Raised under the following conditions:
            - Invalid date format in `start` or `end` parameters.
            - When `end` date is earlier than or equal to `start` date.
            - When `start` date is in the past (relative to local city time).
            - When `end` date exceeds the 16-day forecast limit from the current time.
            - When the city cannot be found by the geocoding API.
    """
    try:
        start_dt = pd.to_datetime(start)
        end_dt = pd.to_datetime(end)
    except (ValueError, TypeError):
        raise ValueError(
            f"date format must be YYYY-MM-DD HH:MM:SS AM/PM, given start: {start}, end: {end}"
        )
    if end_dt <= start_dt:
        raise ValueError("start date must be earlier than end date")

    session = requests_cache.CachedSession(cache_name=".cache", expire_after=3600)
    retry_session = retry(session, retries=5, backoff_factor=0.2)
    latitude, longitude, location_tz = get_location(city_name, retry_session)
    location_now = pd.Timestamp.now(tz=location_tz)
    if start_dt.date() < location_now.date():
        raise ValueError("date is from the past")

    max_date = location_now + pd.Timedelta(days=15)
    if end_dt.date() > max_date.date():
        raise ValueError("The end date must be up to 16 days from now")
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "precipitation_probability", "apparent_temperature", "snowfall", "snow_depth"],
        "timezone": "auto",
        "start_date": start_dt.strftime(r"%Y-%m-%d"),
        "end_date": end_dt.strftime(r"%Y-%m-%d"),
    }
    response = retry_session.get(url, params=params)
    response.raise_for_status()
    response = response.json()
    df = pd.DataFrame(response["hourly"])
    df["time"] = pd.to_datetime(df["time"])
    df = df[(start_dt.floor("h") <= df["time"]) & (df["time"] < end_dt)]
    return df