import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

def get_openmeteo_api_data(url: str, params: dict) -> None:

    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    responses = openmeteo.weather_api(url=url, params=params)

    # Examples
    # Process first location. Add for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds}")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temp_2m = hourly.Variables(0).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
    )}

    hourly_data["temperature_2m"] = hourly_temp_2m

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    print(hourly_dataframe)

def main() -> None:

    # set api endpoint and parameters
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": 52.52,
        "longitude": 13.41,
        "start_date": "2025-02-11",
        "end_date": "2025-02-25",
        "hourly": "temperature_2m"
    }
    get_openmeteo_api_data(url=url, params=params)

if __name__ == "__main__":
    main()