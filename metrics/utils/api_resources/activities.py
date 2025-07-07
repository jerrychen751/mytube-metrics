class Activities:
    def __init__(self):
        pass

    def stream_user_activities(self, access_token: str, pages: int = 1):
        """
        Acts as a generator to stream the authenticated user's activities, using an OAuth 2.0 access token.

        Args:
            access_token (str): OAuth 2.0 access token.
            pages (int): The number of pages to stream (maxResults=50 per page).

        Returns:
            A dictionary/JSON form of the activity resource.
        """
        if not access_token:
            print("No access token.")
            return

        params = {
            "part": "id,snippet,contentDetails",
            "mine": "true",
            "maxResults": 50,
        }
        headers={
            "Authorization": f"Bearer {access_token}"
        }

        next_page_token = None
        for _ in range(pages):
            if next_page_token:
                params["pageToken"] = next_page_token

            try:
                data = self._make_request("activities", params, headers)
                if "items" in data:
                    for item in data["items"]:
                        yield item

                next_page_token = data.get("nextPageToken") # pagination
                if not next_page_token:
                    break
            except requests.exceptions.HTTPError as e:
                print(f"An HTTP error occurred: {e}")
                print(f"Response content: {e.response.text}")
                break
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break