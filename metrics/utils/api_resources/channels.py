from metrics.utils.date_helper import isostr_to_datetime
from urllib.parse import unquote

from typing import Any, Optional, Dict
from metrics.utils.types import ApiResponse

class Channels:
    def __init__(self, client: Any) -> None:
        """
        Initializes the Channels resource handler.

        Args:
            client (Any): The YouTubeClient instance for making API requests.
        """
        self._client = client

    def list(self, part: str = "id,snippet,contentDetails,statistics,topicDetails",
             mine: bool = False,             
             channel_ids: Optional[str] = "",
             max_results: int = 50,
             page_token: Optional[str] = None
            ) -> Optional[ApiResponse]:
        """
        List raw data obtained from YouTube Data API regarding channels (up to 50 channels).
        Corresponds to the channels.list endpoint.

        Args:
            part (str): Comma-separated list of channel resource properties.
            mine (bool): When mine=True, retrieves authenticated user's channels.
            channel_ids (Optional[str]): Comma-separated list of channel ids to retrieve data for.
            max_results (int): The number of items to return in response (1-50).
            page_token (Optional[str]): The specific page.
        """
        # Build params dictionary
        params: Dict[str: Any] = {
            "part": part,
            "maxResults": max_results,
        }

        if mine:
            params["mine"] = "true"
            use_oauth = True
        elif channel_ids: # up to 50 specified channel ids
            params["id"] = channel_ids
            use_oauth = False
        else:
            raise ValueError("Either mine=True or channel ids must be provided.")

        if page_token:
            params["pageToken"] = page_token

        # Make API request to list page of channels
        return self._client._make_request(
            endpoint_path="channels",
            params=params,
            use_oauth=use_oauth
        )

    @staticmethod
    def process_raw_stats(raw_channel_data: ApiResponse) -> Optional[Dict[str, Any]]:
        """
        Process the response from the YouTube Data API for channels resource.

        Args:
            raw_channel_data (ApiResponse): Response from the YouTube Data API to list channels data.

        Returns:
            A dictionary mapping channel IDs to all channel-specific data. None if there is an error.
        """
        if 'items' not in raw_channel_data:
            return None

        channel_data = {}
        for channel_resource in raw_channel_data.get('items', []):
            channel_id = channel_resource.get('id', "")

            snippet = channel_resource.get('snippet', {})
            content_details = channel_resource.get('contentDetails', {})
            statistics = channel_resource.get('statistics', {})
            topic_details = channel_resource.get('topicDetails', {})
            
            # Parse topic URLs
            topic_urls = topic_details.get('topicCategories', [])
            parsed_topics = []
            for url in topic_urls:
                topic = unquote(url.split('/')[-1]).replace('_', ' ')
                if '(sociology)' in topic.lower():
                    topic = topic.lower().replace(' (sociology)', '')
                parsed_topics.append(topic.title())

            data = {
                "channel_name": snippet.get('title', ""),
                "channel_description": snippet.get('description', ""),
                "channel_publication_date": isostr_to_datetime(snippet.get('publishedAt', None)),
                "channel_pfp_url": snippet.get('default', {}).get('url', ""),
                "liked_videos_playlist_id": content_details.get('relatedPlaylists', {}).get('likes', ""),
                "uploads_playlist_id": content_details.get('relatedPlaylists', {}).get('uploads', ""),
                "view_count": statistics.get('viewCount', 0),
                "subscriber_count": statistics.get('subscriberCount', 0),
                "video_count": statistics.get('videoCount', 0),
                "subscriber_count_hidden": statistics.get('hiddenSubscriberCount', False),
                "topics": parsed_topics
            }

            channel_data[channel_id] = data
            
        return channel_data