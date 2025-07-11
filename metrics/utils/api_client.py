import os
import requests
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import AuthorizedSession

from metrics.models import UserCredential
from .api_resources import Channels, Playlists, Subscriptions, Videos, PlaylistItems

from typing import Any
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
        self.playlist_items = PlaylistItems(self)
        """
        Initializes the YouTubeClient.

        Args:
            credentials (UserCredential | None): The user's credentials for OAuth authentication.
        """

    