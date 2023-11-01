from dotenv import load_dotenv
import requests
import os

load_dotenv()
api_key = os.getenv("API_KEY")


def get_current_weather(city):

    request_url = f'http://api.openweathermap.org/data/2.5/weather?appid={api_key}&q={city}&units=metric'

    data = requests.get(request_url).json()

    return data