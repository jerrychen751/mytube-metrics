from metrics.utils.date_helper import isostr_to_datetime

from typing import Generator, Dict, Any, List, Tuple

def get_paginated_subscriptions(
    subscription_generator: Generator[Dict[str, Any], None, None], 
    page_num: int = 1, 
    items_per_page: int = 25
) -> Dict[str, Any]:
    """
    Consumes a generator of raw subscription data and processes it into a paginated list of dictionaries formatted for the template.

    Args:
        subscription_generator: The generator yielding raw subscription items from the API.
        page_number: The page number to retrieve (1-indexed).
        items_per_page: The number of items to display per page.

    Returns:
        A dictionary containing the list of processed subscriptions for the current page and pagination context.
    """
    start_idx = (page_num - 1) * items_per_page
    end_idx = start_idx + items_per_page
    
    processed_subs = []
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
            processed_sub = {
                'channel_title': snippet.get('title', 'N/A'),
                'channel_id': snippet.get('resourceId', {}).get('channelId', ''),
                'profile_picture_url': snippet.get('thumbnails', {}).get('default', {}).get('url'),
                'published_at': isostr_to_datetime(snippet.get('publishedAt', None)),
                'total_item_count': content_details.get('totalItemCount', 0),
                'new_item_count': content_details.get('newItemCount', 0),
                'channel_id': snippet.get('resourceId', {}).get('channelId')
            }
            processed_subs.append(processed_sub)

    return {
        'subscriptions': processed_subs,
        'subbed_channel_info': "placeholder",
        'has_next_page': has_next_page,
        'next_page_number': page_num + 1,
        'previous_page_number': page_num - 1,
        'has_previous_page': page_num > 1
    }
