import requests
import json

def check_weather_api(url_endpoint: str) -> None:

    response = requests.get(url_endpoint)
    print(f"{response.status_code} - {response.ok}")
    print(response.json())

def main():

    meteo_endpoint: str = ""
    check_weather_api(meteo_endpoint)


if __name__ == "__main__":
    main()