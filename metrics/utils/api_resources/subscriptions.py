from typing import Dict, Any, Optional, Generator

class Subscriptions:
    def __init__(self, client: Any) -> None:
        self._client = client

    def list(self, part: str = "id,snippet,contentDetails", mine: bool = False, channel_id: Optional[str] = None, 
            max_results: int = 50, order: str = "alphabetical", page_token: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        List raw data obtained from YouTube Data API regarding subscriptions.
        Corresponds to the subscriptions.list endpoint.

        Args:
            part (str): Comma-separated list of one or more subscription resource properties. (e.g., 'snippet,contentDetails').
            mine (bool): Set to True to retrieve the authenticated user's subscriptions.
            channel_id (Optional[str]): The ID of the channel for which to retrieve subscriptions. Cannot be used with `mine=True`.
            max_results (int): The maximum number of items to return per page (1-50).
            order (str): The order in which to retrieve the subscriptions. Accepts 'alphabetical', 'relevance', or 'unread'.
            page_token (Optional[str]): The `nextPageToken` or `prevPageToken` from a previous API response to retrieve a specific page of results.

        Returns:
            Optional[Dict[str, Any]]: The JSON response from the API as a dictionary, or None if an error occurs.
        """
        # Build params dictionary
        params: Dict[str, Any] = {
            "part": part,
            "maxResults": max_results,
            "order": order,
        }
        use_oauth = False

        if mine:
            params["mine"] = "true"
            use_oauth = True
        elif channel_id:
            params["channelId"] = channel_id
        else:
            raise ValueError("Either 'mine=True' or 'channel_id' must be provided.")

        if page_token:
            params["pageToken"] = page_token

        return self._client._make_request("subscriptions", params=params, use_oauth=use_oauth)

    def list_all_user_subscriptions(self, part: str = "id,snippet,contentDetails", 
                                    order: str = "alphabetical") -> Generator[Dict[str, Any], None, None]:
        """
        Generator to list all of the authenticated user's subscriptions, handling pagination.

        Args:
            part (str): Comma-separated list of one or more subscription resource properties.
                        (e.g., 'snippet,contentDetails').
            order (str): The order in which to retrieve the subscriptions. Accepts 'alphabetical', 'relevance', or 'unread'.

        Yields:
            Dict[str, Any]: A dictionary representing a single subscription item.
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
