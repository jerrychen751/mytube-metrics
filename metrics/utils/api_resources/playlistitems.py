from typing import Any, Optional, Dict
from metrics.utils.date_helper import isostr_to_datetime
from metrics.utils.types import ApiResponse

class PlaylistItems:
    def __init__(self, client: Any) -> None:
        """
        Initializes the PlaylistItems resource handler.

        Args:
            client (Any): The YouTubeClient instance for making API requests.
        """
        self._client = client

    def list(self, part: str = "id,snippet,contentDetails,status",
             playlist_id: str = "",
             max_results: int = 50,
             page_token: Optional[str] = None
            ) -> Optional[ApiResponse]:
        """
        List raw data obtained from YouTube Data API regarding playlist items (up to 50 items).
        Corresponds to the playlistItems.list endpoint.

        Args:
            part (str): Comma-separated list of playlistItem resource properties.
            playlist_id (str): The ID of the playlist for which to retrieve items.
            max_results (int): The number of items to return in response (1-50).
            page_token (Optional[str]): The specific page token for pagination.

        Returns:
            Optional[ApiResponse]: The JSON response from the API as a dictionary, or None if an error occurs.
        """
        if not playlist_id:
            raise ValueError("playlist_id must be provided.")

        params: Dict[str, Any] = {
            "part": part,
            "playlistId": playlist_id,
            "maxResults": max_results,
        }

        if page_token:
            params["pageToken"] = page_token

        # Make API request to playlistItems endpoint
        return self._client._make_request(
            endpoint_path="playlistItems",
            params=params,
            use_oauth=True # playlistItems always require OAuth
        )

    @staticmethod
    def process_raw_items(raw_playlist_items_data: ApiResponse) -> Optional[Dict[str, Any]]:
        """
        Process the response from the YouTube Data API for playlistItems resource.

        Args:
            raw_playlist_items_data (ApiResponse): Response from the YouTube Data API to list playlist items data.

        Returns:
            A dictionary mapping video IDs to all playlist item-specific data. None if there is an error.
        """
        if "items" not in raw_playlist_items_data:
            return None

        processed_items = {}
        for item_resource in raw_playlist_items_data.get("items", []):
            video_id = item_resource.get("snippet", {}).get("resourceId", {}).get("videoId", "")
            if not video_id:
                continue

            snippet = item_resource.get("snippet", {})
            content_details = item_resource.get("contentDetails", {})
            status = item_resource.get("status", {})

            data = {
                "id": item_resource.get("id", ""),
                "video_id": video_id,
                "published_at": isostr_to_datetime(snippet.get("publishedAt", None)),
                "channel_id": snippet.get("channelId", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "thumbnail_url": snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                "playlist_id": snippet.get("playlistId", ""),
                "position": snippet.get("position", 0),
                "video_published_at": isostr_to_datetime(content_details.get("videoPublishedAt", None)),
                "privacy_status": status.get("privacyStatus", ""),
            }
            processed_items[video_id] = data
            
        return processed_items
