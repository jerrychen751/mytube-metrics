from metrics.utils.types import ApiResponse

from typing import Any, Optional, Dict, List

class Videos:
    """
    Provides methods for interacting with the YouTube Data API's "videos" and "videoCategories" resources.
    """
    def __init__(self, client: Any) -> None:
        self._client = client

    def list_video(self, part: str = "id,snippet,status,contentDetails,statistics,topicDetails",
             user_rating: Optional[str] = None,             
             video_ids: Optional[str] = None,
             chart: Optional[str] = None,
             video_category_id: Optional[str] = None,
             max_results: int = 50,
             page_token: Optional[str] = None
            ) -> Optional[ApiResponse]:
        """
        Retrieves a list of videos based on specified criteria. Corresponds to the `videos.list` endpoint.

        Args:
            part (str): A comma-separated list of one or more video resource properties.
            video_ids (Optional[str]): A comma-separated list of video IDs to retrieve.
            user_rating (Optional[str]): Retrieves videos rated by the authenticated user. 
                                     Acceptable values are "like" or "dislike". Requires OAuth.
            chart (Optional[str]): Identifies the chart that you want to retrieve. Acceptable values are "mostPopular".
            video_category_id (Optional[str]): The video category ID for which you want to retrieve popular videos.
            max_results (int): The maximum number of items to return (1-50).
            page_token (Optional[str]): The token for a specific page of results.

        Returns:
            Optional[ApiResponse]: The raw JSON response from the API, or None if an error occurs.
        """
        # Build params dictionary
        params: Dict[str, Any] = {
            "part": part,
            "maxResults": max_results,
        }
        use_oauth = False

        if user_rating and (user_rating == "like" or user_rating == "dislike"):
            params["myRating"] = user_rating
            use_oauth = True
        elif video_ids: # up to 50 specified video ids
            params["id"] = video_ids
        elif chart:
            params["chart"] = chart
            if video_category_id:
                params["videoCategoryId"] = video_category_id
        else:
            raise ValueError("Either user_rating, video_ids, or chart must be provided.")

        if page_token:
            params["pageToken"] = page_token

        # Make API request to list page of channels
        return self._client._make_request(
            endpoint_path="videos",
            params=params,
            use_oauth=use_oauth
        )
    
    def list_all_video_id(self, video_ids: List[str]) -> Dict[int, ApiResponse]:
        """
        Fetches all video resources for a given list of video IDs, handling pagination automatically.

        Args:
            video_ids (List[str]): A list of video IDs to retrieve.

        Returns:
            Dict[int, ApiResponse]: A dictionary where keys are page numbers and values are the raw
                                    API responses for each page of results. Returns an empty dict on error.
        """
        all_videos = {}
        video_ids_str = ",".join(video_ids)
        page_token = None
        page_num = 0
        while True:
            api_response = self.list_video(video_ids=video_ids_str, page_token=page_token)
            if api_response:
                all_videos[page_num] = api_response
                page_token = api_response.get('nextPageToken')
                page_num += 1
            else:
                break
            
            if not page_token:
                break
                    
        return all_videos
    
    def list_all_user_rated(self, user_rating: str) -> Dict[int, ApiResponse]:
        """
        Fetches all videos rated by the authenticated user, handling pagination automatically.

        Args:
            user_rating (str): The rating type to filter by. Acceptable values are "like" or "dislike".

        Returns:
            Dict[int, ApiResponse]: A dictionary where keys are page numbers and values are the raw
                                    API responses for each page of results. Returns an empty dict on error.
        """
        all_videos = {}
        page_token = None
        page_num = 0
        while True:
            api_response = self.list_video(user_rating=user_rating, page_token=page_token)
            if api_response:
                all_videos[page_num] = api_response
                page_token = api_response.get('nextPageToken')
                page_num += 1
            else:
                break
            
            if not page_token:
                break
                    
        return all_videos
    
    def list_video_category(self, part: str = "snippet",
                            category_ids: Optional[str] = None,
                            region_code: Optional[str] = None,
                            max_results: int = 50,
                            page_token: Optional[str] = None
                            ) -> Optional[ApiResponse]:
        """
        Retrieves a list of video categories based on specified criteria. Corresponds to the `videoCategories.list` endpoint.

        Args:
            part (str): A comma-separated list of one or more videoCategory resource properties.
            category_ids (Optional[str]): A comma-separated list of video category IDs to retrieve.
            region_code (Optional[str]): Instructs the API to return the list of video categories available in the specified country.
            max_results (int): The maximum number of items to return (1-50).
            page_token (Optional[str]): The token for a specific page of results.

        Returns:
            Optional[ApiResponse]: The raw JSON response from the API, or None if an error occurs.
        """
        params: Dict[str, Any] = {
            "part": part,
            "maxResults": max_results,
        }
        if category_ids:
            params["id"] = category_ids
        elif region_code:
            params["regionCode"] = region_code
        else:
            raise ValueError("Either category_ids or region_code must be provided.")

        if page_token:
            params["pageToken"] = page_token

        return self._client._make_request(
            endpoint_path="videoCategories",
            params=params
        )

    def list_all_video_categories(self, category_ids: List[str]) -> Dict[int, ApiResponse]:
        """
        Fetches all video category resources for a given list of category IDs, handling pagination automatically.

        Args:
            category_ids (List[str]): A list of video category IDs to retrieve.

        Returns:
            Dict[int, ApiResponse]: A dictionary where keys are page numbers and values are the raw
                                    API responses for each page of results. Returns an empty dict on error.
        """
        all_categories = {}
        category_ids_str = ",".join(category_ids)
        page_token = None
        page_num = 0
        while True:
            api_response = self.list_video_category(category_ids=category_ids_str, page_token=page_token)
            if api_response:
                all_categories[page_num] = api_response
                page_token = api_response.get('nextPageToken')
                page_num += 1
            else:
                break
            
            if not page_token:
                break
                    
        return all_categories
    
