# Standard Library Imports
import os
from typing import Any

# Third-Party Imports
import requests
from dotenv import load_dotenv
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials

# Local App Imports
from metrics.models import UserCredential
from .api_resources import (Activities, Channels, PlaylistItems, Playlists,
                          Subscriptions, Videos)
from .types import ApiResponse

class YouTubeClient:
    """
    A client for interacting with the YouTube Data API v3. Manages authentication and raw API requests.
    """
    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, credentials: UserCredential | None = None) -> None:
        """
        Initializes the YouTubeClient.
        """
        load_dotenv()
        self.api_key = os.getenv("API_KEY")
        
        if not credentials:
            raise ValueError("UserCredential object is required for YouTubeClient.")

        self.credentials = Credentials(
            token=credentials.access_token,
            refresh_token=credentials.refresh_token,
            token_uri=os.getenv("TOKEN_URI"),
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
            scopes=os.getenv("SCOPES", "").split(',')
        )
        
        # Use an AuthorizedSession that automatically handles token refreshes
        self.auth_session = AuthorizedSession(self.credentials)
        self.session = requests.Session()
            
        # --- Initialize Resource Handlers ---
        self.channels = Channels(self)
        self.playlists = Playlists(self)
        self.subscriptions = Subscriptions(self)
        self.videos = Videos(self)
        self.playlist_items = PlaylistItems(self)
        self.activities = Activities(self)
        
    def _make_request(self, endpoint_path: str, params: dict[str, str], use_oauth: bool = False) -> ApiResponse | None:
        """
        Make a request to a specific YouTube Data API endpoint.
        
        Args:
            endpoint_path (str): Path to the API endpoint.
            params (dict): A dictionary of parameters for API call.
            use_oauth (bool): If True, uses the OAuth token. If False, uses the API key.

        Returns:
            The JSON response from the API as a dictionary, or None if an error occurs.
        """
        url = f"{self.BASE_URL}/{endpoint_path}"
        request_params = params.copy()

        session = self.auth_session if use_oauth else self.session
        
        if not use_oauth:
            if not self.api_key:
                raise ValueError("Cannot make public request without an API key.")
            request_params["key"] = self.api_key

        try:
            response = session.get(url=url, params=request_params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # If the authorized session failed, the credentials might be invalid.
            # The user may need to re-authenticate.
            print(f"An API request error occurred: {e}")
            if response:
                print(f"Response: {response.text}")
            return None