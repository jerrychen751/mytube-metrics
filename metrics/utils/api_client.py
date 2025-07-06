import os
import requests
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from .api_resources import Channels, Playlists, Subscriptions, Videos

from typing import Any

class YouTubeClient:
    """
    A client for interacting with the YouTube Data API v3 using the `requests` library. Manages authentication and raw API requests.
    """
    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, credentials: Credentials | None = None) -> None:
        """
        Initializes the YouTubeClient for handling API requests.

        This constructor sets up the client for one of two authentication modes:
        1. API Key Authentication: For accessing public data.
        2. OAuth 2.0 Authentication: For accessing user-specific data.

        A `ValueError` is raised if neither an API key nor a credentials object is provided,
        as this is essential for making authorized API calls.

        Args:
            credentials (Credentials, optional): Required for accessing private user data. Defaults to None.

        Raises:
            ValueError: If neither `api_key` nor `credentials` are provided.
        """
        # --- Initialize API Key / Credentials ---
        load_dotenv()
        self.api_key = os.getenv("API_KEY")
        self.credentials = credentials
        self.session = requests.Session()
            
        # --- Initialize Resource Handlers ---
        # self.channels = Channels(self)
        # self.playlists = Playlists(self)
        self.subscriptions = Subscriptions(self)
        # self.videos = Videos(self)
        
    def _make_request(self, endpoint_path: str, params: dict[str, str], use_oauth: bool = False) -> dict[str, Any] | None:
        """
        Make a request to a specific YouTube Data API endpoint.
        
        Args:
            endpoint_path (str): Path to the API endpoint.
            params (dict): A dictionary of parameters for API call.
            is_oauth (bool): If True, uses the OAuth token. If False, uses the API key.

        Returns:
            The JSON response from the API as a dictionary, or None if an error occurs.
        """
        url = f"{os.getenv("BASE_URL")}/{endpoint_path}"
        headers = {"Accept": "application/json"}
        request_params = params.copy() # avoid modifying original dictionary; shallow copy is fine b/c all values in dictionary are immutable

        # Add necessary parameters to GET request
        if use_oauth:
            if not self.credentials or not self.credentials.token:
                raise ValueError("Cannot make OAuth request without valid credentials.")
            
            headers["Authorization"] = f"Bearer {self.credentials.token}"
        else:
            if not self.api_key:
                raise ValueError("Cannot make public request without an API key.")

            request_params["key"] = self.api_key

        # Make GET request
        try:
            response = self.session.get(url=url, headers=headers, params=request_params)
            response.raise_for_status() # raise error early if 4xx or 5xx response code
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An API reqest error occurred: {e}")
            return None
    
    # --- TASK FUNCTIONS ---
    def stream_user_activities(self, access_token: str, pages: int = 1):
        """
        Acts as a generator to stream the authenticated user's activities, using an OAuth 2.0 access token.

        Args:
            access_token (str): OAuth 2.0 access token.
            pages (int): The number of pages to stream (maxResults=50 per page).

        Returns:
            A dictionary/JSON form of the activity resource.
        """
        if not access_token:
            print("No access token.")
            return

        params = {
            "part": "id,snippet,contentDetails",
            "mine": "true",
            "maxResults": 50,
        }
        headers={
            "Authorization": f"Bearer {access_token}"
        }

        next_page_token = None
        for _ in range(pages):
            if next_page_token:
                params["pageToken"] = next_page_token

            try:
                data = self._make_request("activities", params, headers)
                if "items" in data:
                    for item in data["items"]:
                        yield item

                next_page_token = data.get("nextPageToken") # pagination
                if not next_page_token:
                    break
            except requests.exceptions.HTTPError as e:
                print(f"An HTTP error occurred: {e}")
                print(f"Response content: {e.response.text}")
                break
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break