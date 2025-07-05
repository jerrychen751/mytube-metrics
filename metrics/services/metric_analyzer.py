import os
import json
import pickle
import requests
from dotenv import load_dotenv

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from typing import Generator

from mytube_metrics.youtube_api.client import YouTubeClient
from ..utils.auth_helper import OAuth

class MetricAnalyzer:
    def __init__(self, client: YouTubeClient) -> None:
        self.client = client



    def list_my_subscriptions(self, max_results=10):
        creds = self.client.get_credentials()
        # build() returns a Resource that implements __enter__/__exit__ → calls close()
        with build("youtube", "v3", credentials=creds) as youtube:
            try:
                request = youtube.subscriptions().list(
                    part="snippet,contentDetails",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                return response.get("items", [])
            except HttpError as e:
                print(f"HTTP {e.resp.status}: {e.content}")
                return []


    # if it's private, within query parameters mine=True & access_token=OAUTH
