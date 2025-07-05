import os
from dotenv import load_dotenv

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

from . import database_helper as database

class OAuth:
    def __init__(self) -> None:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        load_dotenv()
        self.scopes = os.getenv("SCOPES", "").split(',')
        self.active_redirect_uri = os.getenv("REDIRECT_URI")

    # --- OAUTH2 FLOW ---
    def build_client_config(self) -> dict[str, dict[str, str]]:
        """
        Read OAuth 2.0 client parameters from environment variables and builds the Google client_config dict for InstalledAppFlow.
        
        Returns:
            A dict matching the client_config format expected by google-auth-oauthlib.
        """
        # Safety
        required = [
            "CLIENT_ID",
            "CLIENT_SECRET",
            "AUTH_URI",
            "TOKEN_URI",
            "REDIRECT_URI"
        ]

        missing = [param for param in required if not os.getenv(param)]
        if missing:
            raise RuntimeError(f"Missing required client parameters in environment: {', '.join(missing)}.")
        
        # Build client config dict
        return {
            "web": {
                "client_id": os.getenv("CLIENT_ID"),
                "client_secret": os.getenv("CLIENT_SECRET"),
                "auth_uri": os.getenv("AUTH_URI"),
                "token_uri": os.getenv("TOKEN_URI"),
                "redirect_uris": [self.active_redirect_uri]
            }
        }

    def get_authorization_url(self) -> tuple[str, str]:
        """
        Obtain unique URL that the user will visit for authentication.

        Returns:
            A tuple containing the authorization URL and the state parameter.
        """
        client_config = self.build_client_config()
        flow = Flow.from_client_config(
            client_config=client_config,
            scopes=self.scopes,
            redirect_uri=self.active_redirect_uri
        )

        authorization_url, state = flow.authorization_url(
            access_type="offline",
            prompt="select_account",
            include_granted_scopes="true"
        )

        return authorization_url, state

    def fetch_credentials(self, state: str, authorization_response: str) -> Credentials:
        """
        Takes the redirect URL returned by Google (authorization_response) and returns credentials by extracting the authorization code within the URL and making a secure request to the token endpoint.

        Also saves both access and refresh tokens to MySQL database for user.
        """
        client_config = self.build_client_config()
        flow = Flow.from_client_config(
            client_config=client_config,
            scopes=self.scopes,
            state=state,
            redirect_uri=self.active_redirect_uri
        )
        flow.fetch_token(authorization_response=authorization_response) # checks the state in authorization_response after auth to the argument passed (state from get_authorization_url)
        
        credentials = flow.credentials
        return credentials