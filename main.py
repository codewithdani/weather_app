from dotenv import load_dotenv
from pprint import pprint
import requests
import os

load_dotenv()
api_key = os.getenv("API_KEY")


def get_current_weather(city="Addis Ababa"):

    request_url = f'http://api.openweathermap.org/data/2.5/weather?appid={api_key}&q={city}&units=metric'

    weather_data = requests.get(request_url).json()

    return weather_data


if __name__ == "__main__":
    print('\n*** Get Current Weather Conditions ***\n')

    city = input('Please enter a city name: ')
  
    data = get_current_weather(city)

    print("\n")
    pprint(data)