from metrics.utils.types import ApiResponse

from typing import Any, Optional, Dict, List

class Videos:
    def __init__(self, client: Any) -> None:
        self._client = client

    def list_video(self, part: str = "id,snippet,status,contentDetails,statistics,topicDetails",
             user_rating: Optional[str] = None,             
             video_ids: Optional[str] = None,
             max_results: int = 50,
             page_token: Optional[str] = None
            ) -> Optional[ApiResponse]:
        """
        List raw data obtained from YouTube Data API regarding videos (up to 50 videos).
        Corresponds to the videos.list endpoint.

        Args:
            part (str): Comma-separated list of video resource properties.
            video_ids (Optional[str]): Comma-separated list of video ids to retrieve data for.
            user_rating (Optional[str]): Acceptable values are either `dislike` or `like`. Returns all liked/disliked videos. Requires user authentication.
            max_results (int): The number of items to return in response (1-50).
            page_token (Optional[str]): The specific page.
        """
        # Build params dictionary
        params: Dict[str: Any] = {
            "part": part,
            "maxResults": max_results,
        }

        if user_rating and (user_rating == "like" or user_rating == "dislike"):
            params["myRating"] = user_rating
            use_oauth = True
        elif video_ids: # up to 50 specified video ids
            params["id"] = video_ids
            use_oauth = False
        else:
            raise ValueError("Either user rating string or video id must be provided.")

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
        Fetches all videos items given a long list of video ids, handling pagination.

        Args:
            video_ids (List[str]): The ID of the playlist for which to retrieve all items.

        Returns:
            Dict[int, ApiResponse]: A dictionary with keys of page numberings (50 entries per page) and values containing all the raw Video resources listed from the API.
            Returns an empty list if an error occurs.
        """
        all_videos = {}
        video_ids = ",".join(video_ids)
        page_token = None
        page_num = 0
        while True:
            api_response = self.list_video(video_ids=video_ids, page_token=page_token)
            if api_response:
                all_videos[page_num] = api_response
                page_token = api_response.get('items', {}).get('nextPageToken', None)
            
            if not page_token or not api_response:
                break
                    
        return all_videos
    
    def list_all_user_rated(self, user_rating: str) -> Dict[int, ApiResponse]:
        """
        Fetches all video items given a user rating.

        Args:
            user_rating (str): Either `like` or `dislike`.

        Returns:
            Dict[int, ApiResponse]: A dictionary with keys of page numberings (50 entries per page) and values containing all the raw Video resources listed from the API.
            Returns an empty list if an error occurs.
        """
        all_videos = {}
        page_token = None
        page_num = 0
        while True:
            api_response = self.list_video(user_rating=user_rating, page_token=page_token)
            if api_response:
                all_videos[page_num] = api_response
                page_token = api_response.get('items', {}).get('nextPageToken', None)
            
            if not page_token or not api_response:
                break
                    
        return all_videos
    
    def list_video_category(self, part: str = "snippet",
                            id: str = "",
                            max_results: int = 50,
                            page_token: Optional[str] = None
                            ) -> Dict[int, ApiResponse]:
        """
        List raw data obtained from YouTube Data API regarding videos (up to 50 videos).
        Corresponds to the videos.list endpoint.

        Args:
            part (str): Comma-separated list of video resource properties.
            id (Optional[str]):       
        """
        # Build params dictionary
        params: Dict[str: Any] = {
            "part": part,
            "id": id,
            "maxResults": max_results
        }

        if not id:
            raise ValueError("Video category id must be provided.")
        if page_token:
            params["pageToken"] = page_token

        # Make API request to list page of channels
        return self._client._make_request(
            endpoint_path="videoCategories",
            params=params
        )
    
