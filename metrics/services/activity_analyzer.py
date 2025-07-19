from typing import Any, Dict, Optional
import random

from metrics.utils.api_client import YouTubeClient
from .content_analyzer import get_category_freqs_in_playlist

def get_recommended_videos_context(request: Any,
                                   max_results: int = 10,
                                   ) -> Dict[str, Any]:
    """
    Fetches a random popular video based on weighted category frequencies,
    ensuring no duplicates across requests in the same session.

    Args:
        request (Any): The Django request object, used to access the user and session.
        max_results (int): The number of videos to fetch per request.

    Returns:
        Dict[str, Any]: A dictionary with recommended videos and a next page token.
    """
    user = request.user
    creds = user.usercredential
    client = YouTubeClient(credentials=creds)

    # --- Session and Duplicate Handling ---
    MAX_IDS_TO_REMEMBER = 500
    recommended_video_ids_list = request.session.get('recommended_video_ids', [])

    # Cap the list to prevent unbounded growth
    if len(recommended_video_ids_list) > MAX_IDS_TO_REMEMBER:
        recommended_video_ids_list = recommended_video_ids_list[-MAX_IDS_TO_REMEMBER:] # list of unique video ids

    recommended_video_ids = set(recommended_video_ids_list)

    # --- Category to ID Mapping ---
    all_categories_response = client.videos.list_video_category(part="snippet", region_code="US")
    category_name_to_id = {
        item['snippet']['title']: item['id']
        for item in all_categories_response.get('items', [])
    }

    # --- Fetching Logic ---
    recommended_videos = []
    valid_category_ids = set(["1", "2", "10", "15", "17", "20", "22", "23", "24", "25", "26", "28", "29"]) # YouTube does not enable retrieval of other category ids for some reason
    valid_categories = {cat for cat, id in category_name_to_id.items() if id in valid_category_ids}

    category_freqs = get_category_frequencies(client)
    if not category_freqs:
        return {
            'recommended_videos': [],
            'next_page_token': None
        }

    # Filter out invalid categories from the frequencies
    category_freqs = {cat: freq for cat, freq in category_freqs.items() if cat in valid_categories}
    if not category_freqs:
        return {
            'recommended_videos': [],
            'next_page_token': None
        }

    category_names = list(category_freqs.keys())
    category_weights = list(category_freqs.values())

    while len(recommended_videos) < max_results:
        # Choose a new category for each video we are trying to find
        chosen_category_name = random.choices(category_names, weights=category_weights)[0]

        # Fetch popular videos for the chosen category
        chosen_category_id = category_name_to_id.get(chosen_category_name)
        response = client.videos.list_video(
            part="snippet",
            chart='mostPopular',
            video_category_id=chosen_category_id,
        )

        if response and response.get('items'):
            # Try to add the first unique video found from this category
            for item in response.get('items', []):
                video_id = item.get('id')
                if video_id not in recommended_video_ids:
                    recommended_video_ids.add(video_id)

                    # Truncate video title if excessively long
                    recommended_video_title = item.get('snippet', {}).get('title')
                    if len(recommended_video_title) > 70:
                        recommended_video_title = recommended_video_title[:70] + "..."

                    # Process video data
                    recommended_videos.append({
                        'recommended_video_id': video_id,
                        'recommended_video_title': recommended_video_title,
                        'recommended_video_thumbnail': item.get('snippet', {}).get('thumbnails', {}).get('medium', {}).get('url'),
                        'recommendation_reason': f"Popular in {chosen_category_name}",
                    })
                    # Break after adding one video, to pick a new category for the next video
                    break

            # Break from the outer loop if max_results is met by adding video
            if len(recommended_videos) >= max_results:
                break
    
    # Store the updated list of IDs back in the session
    request.session['recommended_video_ids'] = list(recommended_video_ids)
    request.session.modified = True

    next_page_token_for_client = "continue" if recommended_videos else None

    return {
        'recommended_videos': recommended_videos,
        'next_page_token': next_page_token_for_client
    }

def get_category_frequencies(client: YouTubeClient) -> Optional[Dict[str, int]]:
    """
    Choose a specific video category from the categories which the user has liked in the past according to the frequency that they appear within the user's liked videos.
    
    Args:
        client (YouTubeClient): YouTubeClient object to make API calls.

    Returns:
        A dictionary of category names and their frequencies, or None.
    """
    liked_videos_playlist_id = client.channels.get_liked_playlist_id()
    category_freqs = get_category_freqs_in_playlist(client, liked_videos_playlist_id)
    if not category_freqs:
        return None

    return category_freqs

