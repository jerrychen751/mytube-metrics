# Built-in libaries
import time
import os
import json
from pprint import pprint

# Third party libraries
import requests
import pandas as pd
from dotenv import load_dotenv



load_dotenv()


# Make API call
base_url = "https://www.googleapis.com/youtube/v3/channels"
parameters = {
    "part": "snippet,statistics,contentDetails",
    "id": os.getenv("CHANNEL_ID"),
    "key": os.getenv("API_KEY"),
}

try:
    response = requests.get(base_url, params=parameters)
    response.raise_for_status()

    channel_info = response.json()

    with open("channel_example.json", "w", encoding="utf-8") as file:
        json.dump(channel_info, file, ensure_ascii=False, indent=4)

    pprint(channel_info)

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")


