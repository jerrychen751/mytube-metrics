from typing import Any, Dict, Generator, Optional
from collections import defaultdict

from django.contrib.auth.models import User

from metrics.utils.api_client import YouTubeClient
from metrics.utils.date_helper import isostr_to_datetime

def get_recommended_videos_context(request: Any, 
                                   page_token: Optional[str] = None,
                                   max_results: int = 9, 
                                   top_n_categories: int = 3
                                   ) -> Dict[str, Any]:
    """
    Fetches a cyclical, proportional mix of popular videos using a session-based approach.

    Args:
        request (Any): The Django request object, used to access the user and session.
        page_token (Optional[str]): A custom token encoding the next category index and its page token.
        max_results (int): The number of videos to fetch per request.
        top_n_categories (int): The number of top categories to cycle through.

    Returns:
        Dict[str, Any]: A dictionary with recommended videos and a custom next page token.
    """
    user = request.user
    creds = user.usercredential
    client = YouTubeClient(credentials=creds)

    # --- Session Initialization ---
    if 'recommendation_profile' not in request.session or not request.session['recommendation_profile']['categories']:
        # 1. Get liked videos playlist ID
        liked_videos_playlist_id = client.channels.get_liked_playlist_id()
        if not liked_videos_playlist_id:
            return {'recommended_videos': [], 'next_page_token': None}

        # 2. Get category frequencies
        from .content_analyzer import get_category_freqs_in_playlist
        category_freqs = get_category_freqs_in_playlist(client, liked_videos_playlist_id)
        if not category_freqs:
            return {'recommended_videos': [], 'next_page_token': None}

        # 3. Map category names to IDs
        all_categories_response = client.videos.list_video_category(part="snippet", region_code="US")
        category_name_to_id = {
            item['snippet']['title']: item['id']
            for item in all_categories_response.get('items', [])
            if item.get('snippet', {}).get('assignable')
        }

        # 4. Store top categories and their pagination state in the session
        sorted_categories = sorted(category_freqs.items(), key=lambda item: item[1], reverse=True)
        top_categories = [
            {
                "name": name,
                "id": category_name_to_id[name],
                "next_page_token": "start" # Use "start" to indicate it hasn't been fetched yet
            }
            for name, _ in sorted_categories[:top_n_categories]
            if name in category_name_to_id
        ]
        
        request.session['recommendation_profile'] = {
            "categories": top_categories,
            "current_category_index": 0
        }

    # --- Fetching Logic ---
    profile = request.session['recommendation_profile']
    if not profile['categories']:
        return {'recommended_videos': [], 'next_page_token': None}

    # Determine which category to fetch from
    category_index = profile['current_category_index']
    current_category = profile['categories'][category_index]
    
    # Use the stored page token, which could be None (for subsequent pages) or "start"
    page_token_for_api = current_category['next_page_token'] if current_category['next_page_token'] != "start" else None

    # Fetch popular videos for the current category
    response = client.videos.list_video(
        part="snippet,contentDetails,statistics",
        chart='mostPopular',
        video_category_id=current_category['id'],
        max_results=max_results,
        page_token=page_token_for_api
    )

    recommended_videos = []
    next_page_token_from_api = None

    if response and 'items' in response:
        for item in response['items']:
            recommended_videos.append({
                'recommended_video_id': item.get('id'),
                'recommended_video_title': item.get('snippet', {}).get('title'),
                'recommended_video_thumbnail': item.get('snippet', {}).get('thumbnails', {}).get('medium', {}).get('url'),
                'recommendation_reason': f"Popular in {current_category['name']}",
            })
        next_page_token_from_api = response.get('nextPageToken')

    # --- Update Session State for Next Call ---
    profile['categories'][category_index]['next_page_token'] = next_page_token_from_api
    profile['current_category_index'] = (category_index + 1) % len(profile['categories'])
    request.session.modified = True

    # --- Determine if scrolling can continue ---
    # We can continue if at least one category in our profile still has a page token.
    can_continue = any(cat.get('next_page_token') for cat in profile['categories'])
    next_page_token_for_client = "continue" if can_continue else None

    return {
        'recommended_videos': recommended_videos,
        'next_page_token': next_page_token_for_client
    }

def stream_recommended_activities(user: User) -> Generator[Dict[str, Any], None, None]:
    """
    Streams all recommended video activities for the authenticated user as a generator.

    Args:
        user (User): The authenticated Django user object.

    Yields:
        Dict[str, Any]: A dictionary representing a single recommended video activity.
    """
    next_page_token: Optional[str] = None
    while True:
        context = get_recommended_videos_context(user, page_token=next_page_token, max_results=50)
        
        for video in context['recommended_videos']:
            yield video
        
        next_page_token = context['next_page_token']
        if not next_page_token:
            break

def get_engagement_evolution_context(user: User) -> Dict[str, Any]:
    """
    Analyzes the evolution of user engagement (e.g., liked videos, subscriptions) over time.

    Args:
        user (User): The authenticated Django user object.

    Returns:
        Dict[str, Any]: A dictionary containing data for engagement evolution.
                        - 'likes_by_month': A dictionary where keys are 'YYYY-MM' and values are counts of liked videos.
                        - 'subscriptions_by_month': A dictionary where keys are 'YYYY-MM' and values are counts of new subscriptions.
    """
    creds = user.usercredential
    client = YouTubeClient(credentials=creds)

    likes_by_month = defaultdict(int)
    subscriptions_by_month = defaultdict(int)
    channel_likes = defaultdict(int)
    channel_subscriptions = defaultdict(int)

    for activity in client.activities.stream_user_activities(part="snippet,contentDetails"):
        activity_type = activity.get('snippet', {}).get('type')
        published_at_str = activity.get('snippet', {}).get('publishedAt')

        if published_at_str:
            published_date = isostr_to_datetime(published_at_str)
            month_year = published_date.strftime('%Y-%m')

            if activity_type == 'like':
                likes_by_month[month_year] += 1
                channel_id = activity.get('contentDetails', {}).get('like', {}).get('resourceId', {}).get('channelId')
                if channel_id:
                    channel_likes[channel_id] += 1
            elif activity_type == 'subscription':
                subscriptions_by_month[month_year] += 1
                channel_id = activity.get('contentDetails', {}).get('subscription', {}).get('resourceId', {}).get('channelId')
                if channel_id:
                    channel_subscriptions[channel_id] += 1
    
    # Sort the data by month
    sorted_likes = dict(sorted(likes_by_month.items()))
    sorted_subscriptions = dict(sorted(subscriptions_by_month.items()))

    # Fetch channel titles for top channels
    top_liked_channels = sorted(channel_likes.items(), key=lambda item: item[1], reverse=True)[:5] # Top 5
    top_subscribed_channels = sorted(channel_subscriptions.items(), key=lambda item: item[1], reverse=True)[:5] # Top 5

    channel_ids = list(set([cid for cid, _ in top_liked_channels] + [cid for cid, _ in top_subscribed_channels]))
    channel_titles = {}
    if channel_ids:
        channels_response = client.channels.list(channel_ids=','.join(channel_ids), part="snippet")
        if channels_response and 'items' in channels_response:
            for item in channels_response['items']:
                channel_titles[item['id']] = item['snippet']['title']

    processed_top_liked_channels = [{'title': channel_titles.get(cid, cid), 'count': count} for cid, count in top_liked_channels]
    processed_top_subscribed_channels = [{'title': channel_titles.get(cid, cid), 'count': count} for cid, count in top_subscribed_channels]

    return {
        'likes_by_month': sorted_likes,
        'subscriptions_by_month': sorted_subscriptions,
        'top_liked_channels': processed_top_liked_channels,
        'top_subscribed_channels': processed_top_subscribed_channels,
    }