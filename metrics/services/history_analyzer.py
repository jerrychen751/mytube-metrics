from typing import Any, Dict, Generator, Optional
from collections import defaultdict
import json

from django.contrib.auth.models import User

from metrics.utils.api_client import YouTubeClient
from metrics.utils.date_helper import isostr_to_datetime

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

def process_takeout_data(file_content: str) -> Dict[str, Any]:
    """
    Processes the content of a YouTube Takeout JSON file.

    Args:
        file_content (str): The content of the uploaded JSON file as a string.

    Returns:
        Dict[str, Any]: A dictionary containing the processed data.
    """
    try:
        data = json.loads(file_content)
        # For now, just return a confirmation. More detailed analysis will go here.
        return {'status': 'success', 'message': 'Takeout data processed successfully.', 'data_length': len(data)}
    except json.JSONDecodeError:
        return {'status': 'error', 'message': 'Invalid JSON file.'}
    except Exception as e:
        return {'status': 'error', 'message': f'An error occurred: {str(e)}'}
