from typing import Any, Optional, Generator, Dict

from requests.exceptions import HTTPError

from metrics.utils.types import ApiResponse
from metrics.utils.date_helper import is_valid_datetime_range

class Activities:
    def __init__(self, client: Any):
        self._client = client

    def list(self, part: str = "id,snippet,contentDetails",
             max_results: int = 50,
             occurred_after: Optional[str] = None,
             occurred_before: Optional[str] = None,
             page_token: Optional[str] = None
            ) -> Optional[ApiResponse]:
        """
        List a single page of raw data obtained from YouTube Data API regarding activities.
        Corresponds to the activities.list endpoint.

        Args:
            part (str): The `part` parameter specifies a comma-separated list of one or more activity resource properties that the API response will include.
                        Valid values are `id`, `snippet`, and `contentDetails`. Defaults to "id,snippet,contentDetails".
            max_results (int): The `maxResults` parameter specifies the maximum number of items that should be returned in each API response.
                               Acceptable values are 0 to 50, inclusive. Defaults to 50.
            occurred_after (Optional[str]): A datetime string (ISO 8601) to filter activities published after this time.
            occurred_before (Optional[str]): A datetime string (ISO 8601) to filter activities published before this time.
            page_token (Optional[str]): The `nextPageToken` or `prevPageToken` from a previous API response to retrieve a specific page of results.

        Returns:
            Optional[ApiResponse]: The JSON response from the API as a dictionary, or None if an error occurs.
        """
        if not is_valid_datetime_range(occurred_after, occurred_before):
            raise ValueError("Invalid datetime range: 'occurred_after' must be before 'occurred_before'.")

        params: Dict[str, Any] = {
            "part": part,
            "mine": "true",
            "maxResults": max_results,
        }

        if occurred_after:
            params['publishedAfter'] = occurred_after
        if occurred_before:
            params['publishedBefore'] = occurred_before
        if page_token:
            params["pageToken"] = page_token

        return self._client._make_request(
            "activities",
            params=params,
            use_oauth=True
        )

    def stream_user_activities(self, part: str = "id,snippet,contentDetails",
                               occurred_after: Optional[str] = None,
                               occurred_before: Optional[str] = None
                               ) -> Generator[ApiResponse, None, None]:
        """
        Streams the authenticated user's activities as a generator.

        Args:
            part (str): The `part` parameter specifies a comma-separated list of one or more activity resource properties that the API response will include.
                        Valid values are `id`, `snippet`, and `contentDetails`. Defaults to "id,snippet,contentDetails".
            occurred_after (Optional[str]): A datetime string (ISO 8601) to filter activities published after this time.
            occurred_before (Optional[str]): A datetime string (ISO 8601) to filter activities published before this time.

        Yields:
            ApiResponse: A dictionary/JSON form of the activity resource for each activity.

        Raises:
            ValueError: If the provided datetime range is invalid (occurred_after is not before occurred_before).
        """
        next_page_token: Optional[str] = None
        while True:
            response = self.list(
                part=part,
                max_results=50,
                occurred_after=occurred_after,
                occurred_before=occurred_before,
                page_token=next_page_token
            )

            if not response or 'items' not in response:
                break

            for item in response['items']:
                yield item

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        
