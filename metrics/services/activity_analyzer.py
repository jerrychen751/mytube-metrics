from typing import Any, Dict, Generator, Optional
from collections import defaultdict

from django.contrib.auth.models import User

from metrics.utils.api_client import YouTubeClient
from metrics.utils.date_helper import isostr_to_datetime

def get_recommended_videos_context(user: User,
                                   page_token: Optional[str] = None,
                                   max_results: int = 50
                                   ) -> Dict[str, Any]:
    """
    Fetches and processes recommended video activities for the authenticated user.

    Args:
        user (User): The authenticated Django user object.
        page_token (Optional[str]): The `nextPageToken` from a previous API response for pagination.
        max_results (int): The maximum number of recommended activities to retrieve per request.

    Returns:
        Dict[str, Any]: A dictionary containing the processed recommended video data and pagination info.
                        - 'recommended_videos': A list of dictionaries, each representing a recommended video.
                        - 'next_page_token': The token for the next page of results, or None if no more pages.
    """
    creds = user.usercredential
    client = YouTubeClient(credentials=creds)

    # Fetch activities of type 'recommendation'
    response = client.activities.list(
        part="snippet,contentDetails",
        max_results=max_results,
        page_token=page_token,
    )

    recommended_videos = []
    if response and 'items' in response:
        for item in response['items']:
            if item.get('snippet', {}).get('type') == 'recommendation':
                snippet = item['snippet']
                content_details = item['contentDetails']

                recommended_resource = content_details.get('recommendation', {}).get('resourceId', {})
                seed_resource = content_details.get('recommendation', {}).get('seedResourceId', {})

                # Only process if the recommended resource is a video
                if recommended_resource.get('kind') == 'youtube#video':
                    recommended_video_id = recommended_resource.get('videoId')
                    recommended_video_title = snippet.get('title')
                    recommended_video_thumbnail = snippet.get('thumbnails', {}).get('medium', {}).get('url')
                    recommendation_reason = content_details.get('recommendation', {}).get('reason')

                    seed_video_id = None
                    seed_video_title = None
                    seed_video_thumbnail = None
                    if seed_resource.get('kind') == 'youtube#video':
                        seed_video_id = seed_resource.get('videoId')
                        # Fetch seed video thumbnail if available
                        if seed_video_id:
                            video_response = client.videos.list(video_ids=seed_video_id, part="snippet")
                            if video_response and 'items' in video_response and video_response['items']:
                                seed_video_snippet = video_response['items'][0].get('snippet', {})
                                seed_video_thumbnail = seed_video_snippet.get('thumbnails', {}).get('default', {}).get('url')
                                seed_video_title = seed_video_snippet.get('title')

                    recommended_videos.append({
                        'recommended_video_id': recommended_video_id,
                        'recommended_video_title': recommended_video_title,
                        'recommended_video_thumbnail': recommended_video_thumbnail,
                        'recommendation_reason': recommendation_reason,
                        'seed_video_id': seed_video_id,
                        'seed_video_title': seed_video_title,
                        'seed_video_thumbnail': seed_video_thumbnail,
                    })
    
    next_page_token = response.get('nextPageToken') if response else None

    return {
        'recommended_videos': recommended_videos,
        'next_page_token': next_page_token,
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