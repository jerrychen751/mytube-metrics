# Standard Library Imports
from typing import Any, Dict, Optional

# Local App Imports
from metrics.utils.date_helper import isostr_to_datetime
from metrics.utils.types import ApiResponse

class Playlists:
    def __init__(self, client: Any) -> None:
        """
        Initializes the Playlists resource handler.

        Args:
            client (Any): The YouTubeClient instance for making API requests.
        """
        self._client = client

    def list(self, part: str = "id,snippet,contentDetails,status",
                      mine: bool = False,
                      playlist_ids: Optional[str] = None,
                      channel_id: Optional[str] = None,
                      max_results: int = 50,
                      page_token: Optional[str] = None
                    ) -> Optional[ApiResponse]:
        """
        List raw data obtained from YouTube Data API regarding playlists (up to 50 playlists).
        Corresponds to the playlists.list endpoint.

        Args:
            part (str): Comma-separated list of playlist resource properties.
            mine (bool): When mine=True, retrieves authenticated user's playlists.
            playlist_ids (Optional[str]): Comma-separated list of playlist ids to retrieve data for.
            channel_id (Optional[str]): The ID of the channel for which to retrieve playlists.
            max_results (int): The number of items to return in response (1-50).
            page_token (Optional[str]): The specific page token for pagination.

        Returns:
            Optional[ApiResponse]: The JSON response from the API as a dictionary, or None if an error occurs.
        """
        # Build params dictionary
        params: Dict[str, Any] = {
            "part": part,
            "maxResults": max_results,
        }

        if mine:
            params["mine"] = "true"
            use_oauth = True
        elif playlist_ids:
            params["id"] = playlist_ids
            use_oauth = False
        elif channel_id:
            params["channelId"] = channel_id
            use_oauth = False
        else:
            raise ValueError("Must provide either mine=True, playlist ids, or a specific channel id.")
        
        if page_token:
            params["pageToken"] = page_token

        # Make API request to playlists endpoint
        return self._client._make_request(
            endpoint_path="playlists",
            params=params,
            use_oauth=use_oauth
        )
    
    @staticmethod
    def process_raw_playlist(raw_playlist_data: ApiResponse) -> Optional[Dict[str, Any]]:
        """
        Process the response from the YouTube Data API for playlists resource.

        Args:
            raw_playlist_data (ApiResponse): Response from the YouTube Data API to list playlists data.

        Returns:
            A dictionary mapping playlist IDs to all playlist-specific data. None if there is an error.
        """
        if "items" not in raw_playlist_data:
            return None
        
        processed_playlists = {}
        for playlist_resource in raw_playlist_data.get("items", []):
            playlist_id = playlist_resource.get("id", "")

            snippet = playlist_resource.get("snippet", {})
            status = playlist_resource.get("status", {})
            content_details = playlist_resource.get("contentDetails", {})

            data = {
                "id": playlist_id,
                "published_at": isostr_to_datetime(snippet.get("publishedAt", None)),
                "channel_id": snippet.get("channelId", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "playlist_title": snippet.get("title", ""),
                "thumbnail_url": snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                "privacy_status": status.get("privacyStatus", ""),
                "item_count": content_details.get("itemCount", 0),
            }
            processed_playlists[playlist_id] = data
            
        return processed_playlists
        
