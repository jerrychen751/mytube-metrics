from metrics.utils.date_helper import isostr_to_datetime

from typing import Generator, List, Tuple, Any
from metrics.utils.types import ApiResponse

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
