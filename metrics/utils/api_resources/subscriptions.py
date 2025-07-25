# Standard Library Imports
from typing import Any, Dict, Generator, Optional

# Local App Imports
from metrics.utils.types import ApiResponse

class Subscriptions:
    def __init__(self, client: Any) -> None:
        """
        Initializes the Subscriptions resource handler.

        Args:
            client (Any): The YouTubeClient instance for making API requests.
        """
        self._client = client

    def list(self, part: str = "id,snippet,contentDetails",
             mine: bool = True, 
             channel_id: Optional[str] = None,
             max_results: int = 50,
             order: str = "alphabetical",
             page_token: Optional[str] = None
            ) -> Optional[ApiResponse]:
        """
        List a single page of raw data obtained from YouTube Data API regarding subscriptions.
        Corresponds to the subscriptions.list endpoint.

        Args:
            part (str): Comma-separated list of subscription resource properties. (e.g., 'snippet,contentDetails').
            mine (bool): Whether to retrieve the authenticated user's subscriptions or not.
            channel_id (Optional[str]): The ID of the channel for which to retrieve subscriptions. Cannot be used with `mine=True`.
            max_results (int): The maximum number of items to return per page (1-50).
            order (str): The order in which to retrieve the subscriptions. Accepts 'alphabetical', 'relevance', or 'unread'.
            page_token (Optional[str]): The `nextPageToken` or `prevPageToken` from a previous API response to retrieve a specific page of results.

        Returns:
            Optional[ApiResponse]: The JSON response from the API as a dictionary, or None if an error occurs.
        """
        # Build params dictionary
        params: Dict[str, Any] = {
            "part": part,
            "maxResults": max_results,
            "order": order,
        }

        if mine:
            params["mine"] = "true"
            use_oauth = True
        elif channel_id:
            params["channelId"] = channel_id
            use_oauth = False
        else:
            raise ValueError("Either 'mine=True' or 'channel_id' must be provided.")

        if page_token:
            params["pageToken"] = page_token

        # Make API request to list page of subscriptions
        return self._client._make_request(
            "subscriptions",
            params=params,
            use_oauth=use_oauth
        )

    def stream_user_subscriptions(self, part: str = "id,snippet,contentDetails", 
                                      order: str = "alphabetical"
                                      ) -> Generator[ApiResponse, None, None]:
        """
        Generator to list all of the authenticated user's subscription data.

        Args:
            part (str): Comma-separated list of one or more subscription resource properties.
                        (e.g., 'snippet,contentDetails').
            order (str): The order in which to retrieve the subscriptions. Accepts 'alphabetical', 'relevance', or 'unread'.

        Yields:
            ApiResponse: A dictionary representing a single subscription item. None if there is an error during listing.
        """
        next_page_token: Optional[str] = None
        while True:
            response = self.list(
                part=part,
                mine=True,
                max_results=50,
                order=order,
                page_token=next_page_token
            )

            if not response or 'items' not in response:
                break

            for item in response['items']:
                yield item

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
