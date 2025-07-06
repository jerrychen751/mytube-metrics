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

from ..utils.api_client import YouTubeClient
from ..utils.auth_helper import OAuth

class MetricAnalyzer:
    pass

    # if it's private, within query parameters mine=True & access_token=OAUTH