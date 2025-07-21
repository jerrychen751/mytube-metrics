"""
Responsible for analyzing user content affinity, such as:
    - Determining frequently-occurring topics in liked videos.
    - Analyzing the reasoning YouTube uses to recommend videos on home page.
"""

# Standard Library Imports
from collections import Counter
from typing import Any, Dict

# Third-Party Imports
from django.contrib.auth.models import User

# Local App Imports
from metrics.utils.api_client import YouTubeClient
from metrics.utils.topic_helper import parse_topic_urls
from .visualizer import create_plotly_chart_dict

def get_content_affinity_context(user: User) -> Dict[str, Any]:
    """
    Build context for the `content_affinity` view.

    This function currently analyzes the user's "Liked Videos" playlist to determine
    the frequency of different video topics and categories.

    The resulting context dictionary contains:
        - 'topic_freqs': A dictionary mapping topic names to their frequency.
        - 'category_freqs': A dictionary mapping category names to their frequency.
    """
    # Obtain creds from database
    creds = user.usercredential
    client = YouTubeClient(credentials=creds)

    # Initialize context dictionary
    context = {}

    liked_videos_playlist_id = client.channels.get_liked_playlist_id()
    if liked_videos_playlist_id:
        # Determine topic frequencies and create bar chart
        topic_freqs = get_topic_freqs_in_playlist(client, liked_videos_playlist_id)
        if topic_freqs:
            context["topic_freqs"] = topic_freqs
            context["topic_freq_chart_dict"] = create_plotly_chart_dict(
                freq_data=topic_freqs,
                data_name="Topic",
                chart_type='bar',
                chart_title="Topic Frequencies"
            )

        # Determine video category frequencies and create donut chart
        category_freqs = get_category_freqs_in_playlist(client, liked_videos_playlist_id)
        if category_freqs:
            context["category_freqs"] = category_freqs
            context["category_freq_chart_dict"] = create_plotly_chart_dict(
                freq_data=category_freqs,
                data_name="Category",
                chart_type='donut',
                chart_title="Category Distribution"
            )

        # 

    return context


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

def get_category_freqs_in_playlist(client: YouTubeClient, playlist_id: str) -> Dict[str, int]:
    """
    Take a playlist ID and obtain the frequency of video categories within that playlist.

    Args:
        client (YouTubeClient): The YouTubeClient instance for making API requests.
        playlist_id (str): The ID of the playlist to analyze.

    Returns:
        A dictionary with category names as keys and their frequency count as values. Returns None if an error occurred or the user has no liked videos.
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

    category_ids = []
    chunk_size = 50  # Max number of video IDs per API call

    for i in range(0, len(video_ids), chunk_size):
        video_id_chunk = video_ids[i:i + chunk_size]
        video_ids_str = ",".join(video_id_chunk)
        
        video_responses = client.videos.list_video(part="snippet", video_ids=video_ids_str, max_results=chunk_size)
        
        if video_responses and 'items' in video_responses:
            for video_item in video_responses['items']:
                category_id = video_item.get('snippet', {}).get('categoryId')
                if category_id:
                    category_ids.append(category_id)

    if not category_ids:
        return {}

    # Match category ID to the category title
    unique_category_ids = list(set(category_ids))
    category_id_str = ",".join(unique_category_ids)
    
    category_responses = client.videos.list_video_category(part="snippet", category_ids=category_id_str)
    
    category_id_to_name = {}
    if category_responses and 'items' in category_responses:
        for category_item in category_responses['items']:
            cat_id = category_item.get('id')
            cat_name = category_item.get('snippet', {}).get('title')
            if cat_id and cat_name:
                category_id_to_name[cat_id] = cat_name

    # Count the frequency of each category name
    category_frequencies = Counter()
    for cat_id in category_ids:
        if cat_id in category_id_to_name:
            category_frequencies.update([category_id_to_name[cat_id]])

    return dict(category_frequencies)

