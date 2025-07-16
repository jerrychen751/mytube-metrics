from typing import Generator, Any, Dict

from django.contrib.auth.models import User

from metrics.utils.api_client import YouTubeClient
from metrics.utils.types import ApiResponse
from metrics.utils.date_helper import isostr_to_datetime

def get_subscription_list_context(user: User, page_num: int) -> Dict[str, Any]:
    """
    Build context for the `subscriptions_list` view.

    This function fetches a paginated list of the user's subscriptions,
    enriches it with detailed channel statistics, and provides pagination context.

    Args:
        user (User): The authenticated Django user object.
        page_num (int): The page number to retrieve.

    Returns:
        A dictionary containing the processed subscription data for the
        requested page and all necessary pagination context, including:
        - 'subscriptions': A dictionary of subscription data for the current page.
        - 'has_next_page': A boolean indicating if there is a next page.
        - 'next_page_number': The number of the next page.
        - 'has_previous_page': A boolean indicating if there is a previous page.
        - 'previous_page_number': The number of the previous page.
    """
    # Obtain creds from database
    creds = user.usercredential
    client = YouTubeClient(credentials=creds)

    # Get the paginated subscription data
    subscription_generator = client.subscriptions.stream_user_subscriptions()
    pagination_data = get_paginated_subscriptions(
        subscription_generator,
        page_num=page_num,
    )

    # Get additional statistics on current page of subscriptions (25 max)
    subs_on_page = pagination_data.get('subscriptions', {})
    if subs_on_page:
        channel_ids = list(subs_on_page.keys())
        raw_channel_stats = client.channels.list(channel_ids=",".join(channel_ids))
        processed_channel_stats = client.channels.process_raw_stats(raw_channel_stats)

        # Update subscription data with channel statistics
        for channel_id, channel_data in subs_on_page.items():
            if channel_id in processed_channel_stats:
                channel_data.update(processed_channel_stats[channel_id])

    return pagination_data

def get_paginated_subscriptions(
    subscription_generator: Generator[ApiResponse, None, None], 
    page_num: int = 1, 
    items_per_page: int = 25
) -> ApiResponse:
    """
    Paginates subscription data from a generator and formats it for display.

    This function consumes a generator that yields raw subscription data from the YouTube API.
    It processes the data, extracts relevant fields, and returns a paginated list of
    subscriptions, along with context for pagination controls (e.g., next/previous page).

    Args:
        subscription_generator (Generator[ApiResponse, None, None]): A generator that yields
            raw subscription item dictionaries from the YouTube API.
        page_num (int, optional): The page number to retrieve (1-indexed). Defaults to 1.
        items_per_page (int, optional): The number of items to display per page.
            Defaults to 25.

    Returns:
        ApiResponse: A dictionary containing the processed subscriptions for the
        requested page and pagination context. The dictionary has the following keys:
            - 'subscriptions' (Dict[str, Dict[str, Any]]): A dictionary of processed
              subscription data, with channel IDs as keys.
            - 'has_next_page' (bool): True if there is a next page, False otherwise.
            - 'next_page_number' (int): The number of the next page.
            - 'previous_page_number' (int): The number of the previous page.
            - 'has_previous_page' (bool): True if there is a previous page, False otherwise.
    """
    start_idx = (page_num - 1) * items_per_page
    end_idx = start_idx + items_per_page
    
    processed_subs = {}
    has_next_page = False
    
    # Iterate through the generator with an index to track page progress
    for i, sub in enumerate(subscription_generator):
        # Stop by page/inde
        if i >= end_idx:
            has_next_page = True
            break

        # If curr idx is in the range of the current page, process the item
        if i >= start_idx:
            snippet = sub.get('snippet', {})
            content_details = sub.get('contentDetails', {})

            # Build processed subscription dictionary
            channel_id = snippet.get('resourceId', {}).get('channelId', '')
            subscription_data = {
                'channel_title': snippet.get('title', 'N/A'),
                'channel_id': snippet.get('resourceId', {}).get('channelId'),
                'profile_picture_url': snippet.get('thumbnails', {}).get('default', {}).get('url'),
                'published_at': isostr_to_datetime(snippet.get('publishedAt', None)),
                'total_item_count': content_details.get('totalItemCount', 0),
                'new_item_count': content_details.get('newItemCount', 0)
            }

            processed_subs[channel_id] = subscription_data

    return {
        'subscriptions': processed_subs,
        'has_next_page': has_next_page,
        'next_page_number': page_num + 1,
        'previous_page_number': page_num - 1,
        'has_previous_page': page_num > 1
    }
