import mysql.connector
from google.oauth2.credentials import Credentials
import os
from dotenv import load_dotenv

load_dotenv()

# --- Database Connection ---
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="mytube_user",
        password=os.getenv("DB_PASSWORD"),
        database="mytube_metrics_db"
    )

# --- Credential Management ---
def save_user_credentials(credentials: Credentials, user_id: int | None) -> None:
    """
    Save credentials of a new user or update for an existing user in database.
    """
    db = get_db_connection()
    cursor = db.cursor()

    if user_id:
        sql = """
            UPDATE users SET
            access_token = %s, refresh_token = %s
            WHERE id = %s
        """
        values = (
            credentials.token, credentials.refresh_token, user_id
        )
    else:
        sql = """
            INSERT INTO users (access_token, refresh_token)
            VALUES (%s, %s)
        """
        values = (
            credentials.token, credentials.refresh_token
        )
    
    cursor.execute(sql, values)
    cursor.close()
    db.close()

def get_user_credentials(user_id: int) -> Credentials | None:
    """
    Retrieve credentials from database and returns a Credentials object.

    Returns:
        Credentials object for specified user. Returns `None` if missing.
    """
    db = get_db_connection()
    cursor = db.cursor(dictionary=True) # allows for access using column names, rather than relying on tuple ordering

    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id)) # returns result set of matches; cursor positioned before first row of this new result set
    user_data = cursor.fetchone() # advance one row and retrieve it

    cursor.close()
    db.close()

    if not user_data or not user_data.get("access_token"):
        return None
    
    return Credentials(
        token=user_data["access_token"],
        refresh_token=user_data["refresh_token"],
        token_uri=os.getenv("TOKEN_URI"),
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        scopes=os.getenv("SCOPES")
    )
