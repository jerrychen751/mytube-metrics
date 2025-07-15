"""
Responsible for analyzing user content affinity, such as:
    - Determining frequently-occurring topics in liked videos.
    - Analyzing the reasoning YouTube uses to recommend videos on home page.
"""

from typing import Dict, Any, Optional
from collections import Counter

from metrics.utils.api_client import YouTubeClient
from metrics.utils.types import ApiResponse
from metrics.utils.topic_helper import parse_topic_urls

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
        topic_freqs = get_topic_freqs_in_playlist(client, liked_videos_playlist_id)
        context["topic_freqs"] = topic_freqs

    # 


def get_topic_freqs_in_playlist(client: YouTubeClient, playlist_id: str) -> Dict[str, int]:
    """
    Take a playlist ID and obtain the frequency of topics within that playlist.

    Args:
        client (YouTubeClient): The YouTubeClient instance for making API requests.
        playlist_id (str): The ID of the playlist to analyze.

    Returns:
        A dictionary with topic keys and a counter value for how many times that topic has appeared in the video playlist.
    """
    all_playlistitems = client.playlist_items.list_all(playlist_id)
    video_ids = []
    for api_response in all_playlistitems.values():
        items = api_response.get('items', [])
        for item in items:
            video_id = item.get('contentDetails', {}).get('videoId')
            if video_id:
                video_ids.append(video_id)

    if not video_ids:
        return {}

    topic_frequencies = Counter()
    chunk_size = 50  # Max number of video IDs per API call

    for i in range(0, len(video_ids), chunk_size):
        video_id_chunk = video_ids[i:i + chunk_size]
        video_ids_str = ",".join(video_id_chunk)
        
        # Fetch video details for the chunk of video IDs
        video_responses = client.videos.list_video(part="topicDetails", video_ids=video_ids_str, max_results=chunk_size)
        
        if video_responses and 'items' in video_responses:
            for video_item in video_responses['items']:
                topic_details = video_item.get('topicDetails', {})
                topics = parse_topic_urls(topic_details)
                topic_frequencies.update(topics)

    return dict(topic_frequencies)

    