"""
Responsible for analyzing user content affinity, such as:
    - Determining frequently-occurring topics in liked videos.
    - Analyzing the reasoning YouTube uses to recommend videos on home page.
"""

from typing import Dict, Any, Optional

from metrics.utils.api_client import YouTubeClient
from metrics.utils.types import ApiResponse
from django.contrib.auth.models import User

def get_content_affinity_context(user: User) -> Dict[str, Any]:
    """
    Build context for `content_affinity` function in `views.py`.

    Resulting context dictionary will contain dictionaries containing:
        - topics mapped to their frequencies for videos within liked-videos playlist
        - video categories mapped to their frequencies for videos within liked-videos playlist
        - recommended video id mapped to its relevant information (e.g., title, image url, reason for recommendation)
    """
    # Obtain creds from database
    creds = user.usercredential
    client = YouTubeClient(credentials=creds)

    # Initialize context dictionary
    context = {}

    # Determine topic frequencies
    liked_videos_playlist_id = client.channels.get_liked_playlist_id()
    if liked_videos_playlist_id:
        video_data = client.playlist_items.list_all(liked_videos_playlist_id)
        topic_freqs = get_topic_freqs_in_playlistitems(video_data)
        context["topic_freqs"] = topic_freqs

    # 

def get_topic_freqs_in_playlistitems(all_playlistitems: Dict[str, ApiResponse]) -> Dict[str, int]:
    """
    Take all the listed playlistitems and obtain the frequency of topics within that playlist.

    Args:
        all_playlistitems (Dict[int, ApiResponse]): A paginated dictionary of raw API responses from the PlaylistItems resource.

    Returns:
        Optional[Dict[str, int]]: A dictionary with topic keys and a counter value for how many times that topic has appeared in the liked videos playlist.
    """
    from metrics.utils.topic_helper import parse_topic_urls

    video_ids = []
    for api_response in all_playlistitems.values():
        items = api_response['items']
        for item in items:
            if item['resourceId']['kind'] == "youtube#video":
                video_ids.append(item['resourceId']['videoId'])

    