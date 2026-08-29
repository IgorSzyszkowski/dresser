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


def get_weather(
    city_name: str, start: str = "", end: str = "", hours: float = 1
) -> tuple[pd.DataFrame, str, str]:
    """Fetches hourly weather forecast data from Open-Meteo for a specific city and date range.

    Validates the input date range (requires non-past dates, enforces a max 16-day
    forecast limit) and filters the resulting DataFrame to the half-open interval [start, end).
    If `start` or `end` are empty, defaults to current local time and calculates `end` using `hours`.

    Args:
        city_name (str): Name of the city to retrieve forecast data for.
        start (str, optional): Start date and time in a pandas-parseable format
            (e.g., "YYYY-MM-DD HH:MM"). Defaults to "" (current local time).
        end (str, optional): End date and time. Defaults to "" (calculated via `hours`).
        hours (float, optional): Time window duration in hours to add to `start`
            when `end` is not provided. Defaults to 1.

    Returns:
        tuple[pd.DataFrame, str, str]: A tuple containing:
            - pd.DataFrame: Hourly forecast data with columns `time`, `temperature_2m`,
              `precipitation_probability`, `apparent_temperature`, and `snow_depth`.
            - str: Effective start timestamp string used for the query.
            - str: Effective end timestamp string used for the query.

    Raises:
        ValueError: Raised under the following conditions:
            - Invalid date format in `start` or `end` parameters.
            - When `end` date is earlier than or equal to `start` date.
            - When `start` date is in the past (relative to local city time).
            - When `end` date exceeds the 16-day forecast limit from current time.
            - When the city cannot be found by the geocoding API.
    """
    session = requests_cache.CachedSession(cache_name=".cache", expire_after=3600)
    retry_session = retry(session, retries=5, backoff_factor=0.2)
    latitude, longitude, location_tz = get_location(city_name, retry_session)
    location_now = pd.Timestamp.now(tz=location_tz)

    if start == "":
        start = location_now.strftime("%Y-%m-%d %H:%M")
    if end == "":
        end = (pd.to_datetime(start) + pd.Timedelta(hours=hours)).strftime(
            "%Y-%m-%d %H:%M"
        )

    try:
        start_dt = pd.to_datetime(start)
        end_dt = pd.to_datetime(end)
    except ValueError, TypeError:
        raise ValueError(
            f"date format must be YYYY-MM-DD HH:MM:SS AM/PM, given start: {start}, end: {end}"
        )

    if end_dt <= start_dt:
        raise ValueError("start date must be earlier than end date")

    if start_dt.date() < location_now.date():
        raise ValueError("date is from the past")

    max_date = location_now + pd.Timedelta(days=15)
    if end_dt.date() > max_date.date():
        raise ValueError("The end date must be up to 16 days from now")

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": [
            "temperature_2m",
            "precipitation_probability",
            "apparent_temperature",
            "snow_depth",
        ],
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

    return df, start, end
