# Gemini Code Assistant Guidelines for mytube_metrics

This document provides guidelines for using the Gemini Code Assistant to contribute to the `mytube_metrics` project. By following these guidelines, you can ensure that your contributions are consistent with the project's goals and coding standards.

When making code changes, always keep a copy of the previous file states in memory, so that if I tell you to revert, all of the latest changes can be undone.

## Project Overview

### Motivation/Use Case
In the age of information, people are not only defined by those around them, but also the social media content they consume.

Many YouTube users spend a considerable amount of their time consuming a diverse array of videos, but they rarely gain structured insight into their viewing habits. There is no easy way to answer questions such as:
- What percentage of my watch history falls into educational content vs. entertainment?
- Which channels or creators do I spend the most time watching?
- How has my viewing profile evolved over the past month or year?

`mytube_metrics` is a web application that allows users to gain insights into their YouTube viewing habits. The application provides users with a variety of metrics and visualizations that help them understand what they watch, who they watch, and how their viewing habits have changed over time.

## Getting Started

To get started with the `mytube_metrics` project, you will need to:

1.  **Clone the repository:**
    ```
    git clone https://github.com/your-username/mytube_metrics.git
    ```
2.  **Install the required dependencies:**
    ```
    pip install -r requirements.txt
    ```
3.  **Set up the database:**
    - Create a MySQL database named `mytube_metrics_db`.
    - Create a user named `mytube_user` with a password.
    - Grant the `mytube_user` all privileges on the `mytube_metrics_db` database.
4.  **Set up the environment variables:**
    - Create a `.env` file in the root directory of the project.
    - Add the following environment variables to the `.env` file:
        ```
        CLIENT_ID=<your-client-id>
        CLIENT_SECRET=<your-client-secret>
        AUTH_URI=https://accounts.google.com/o/oauth2/auth
        TOKEN_URI=https://oauth2.googleapis.com/token
        REDIRECT_URI=http://127.0.0.1:8000/callback
        SCOPES="https://www.googleapis.com/auth/youtube.readonly openid https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"
        DB_PASSWORD=<your-database-password>
        ```
5.  **Run the application:**
    ```
    python manage.py runserver
    ```

## Project Structure

The `mytube_metrics` project is organized as follows:

```
/Users/jerry/Desktop/python/projects/mytube_metrics/
├───.DS_Store
├───.gitignore
├───GEMINI.md
├───manage.py
├───.git/...
├───metrics/
│   ├───__init__.py
│   ├───admin.py
│   ├───apps.py
│   ├───models.py
│   ├───tests.py
│   ├───urls.py
│   ├───views.py
│   ├───__pycache__/
│   ├───migrations/
│   │   ├───__init__.py
│   │   ├───0001_initial.py
│   │   ├───0002_alter_usercredential_refresh_token.py
│   │   ├───0003_usercredential_profile_picture_url.py
│   │   └───__pycache__/
│   ├───services/
│   │   ├───content_analyzer.py
│   │   ├───subscription_analyzer.py
│   │   └───visualizer.py
│   ├───templates/
│   │   └───metrics/
│   │       ├───base.html
│   │       ├───content_affinity.html
│   │       ├───dashboard.html
│   │       ├───login.html
│   │       └───subscriptions_list.html
│   └───utils/
│       ├───__pycache__/
│       ├─��─api_client.py
│       ├───auth_helper.py
│       ├───date_helper.py
│       └───api_resources/
│           ├───__init__.py
│           ├───activities.py
│           ├───channels.py
│           ├───playlistitems.py
│           ├───playlists.py
│           ├───subscriptions.py
│           └───videos.py
├───mytube_metrics/
│   ├───__init__.py
│   ├───asgi.py
│   ├───settings.py
│   ├───urls.py
│   ├───wsgi.py
│   └───__pycache__/
└───venv/
    ├───bin/...
    ├───include/...
    └───lib/...
```

-   **`metrics`**: The main Django application.
    -   **`services`**: Contains modules for analyzing and visualizing YouTube data.
        -   **`content_analyzer.py`**: Analyzes user content affinity (e.g., liked videos).
        -   **`subscription_analyzer.py`**: Analyzes YouTube subscription data.
        -   **`visualizer.py`**: Creates visualizations from analyzed data.
    -   **`templates`**: Contains HTML templates for the web application, organized by app.
    -   **`utils`**: Contains utility functions and API resource handlers.
        -   **`api_client.py`**: A client for interacting with the YouTube Data API.
        -   **`auth_helper.py`**: Handles user authentication and authorization.
        -   **`date_helper.py`**: Provides helper functions for date and time manipulation.
        -   **`api_resources`**: Contains modules for interacting with specific YouTube Data API resources.
            -   **`activities.py`**: Handles YouTube Activities API requests.
            -   **`channels.py`**: Handles YouTube Channels API requests.
            -   **`playlistitems.py`**: Handles YouTube PlaylistItems API requests.
            -   **`playlists.py`**: Handles YouTube Playlists API requests.
            -   **`subscriptions.py`**: Handles YouTube Subscriptions API requests.
            -   **`videos.py`**: Handles YouTube Videos API requests.
-   **`mytube_metrics`**: The main Django project configuration.
    -   **`settings.py`**: Contains the settings for the Django project.
    -   **`urls.py`**: Contains the URL patterns for the Django project.
-   **`.env`**: Contains environment variables for the project.
-   **`.gitignore`**: Specifies which files and directories to ignore in Git.
-   **`manage.py`**: A command-line utility for interacting with the Django project.

## User-Centric Functionalities

### 1. Authorization/Authentication
Users are able to log into the web app and securely authenticate their Google Account for the app to access (read-only) information about their YouTube profile. This functionality is fully implemented.

**Specific Implementation**
The following scopes/permissions are being asked for:
```
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]
```

At a high level:
1. The user clicks on a button like "Login with Google" and their browser is redirected to authorization_url.
2. After the user lands on Google's "consent screen", they are interacting with Google. After they have finished logging in, Google redirects the user's browser to the specified `self.active_redirect_uri` in `OAuth` object.
3. A Python web framework like Django must receive the incoming request from the user's browser (when they're returning to a specific page on the web app via redirect URI) to obtain the authorization_response (full URL of redirect back will contain authorization code used to obtain creds).
4. Use the authorization response containing authorization code to fetch token, allowing for the extraction of credentails from flow object. Return credentials to be used and also store access/refresh token in backend MySQL database.

### 2. FrontEnd Web Interface
Users have a variety of options once they have logged into the app to check detailed information regarding their own YouTube account. They can be broadly divided into a few categories based on Google's YouTube Data API endpoints/resources.

#### Current Implementation Status
- **✅ Subscriptions Analysis**: Users can view a paginated list of their subscriptions. For each subscription on the current page, they can see the channel's title, profile picture, subscription date, and key statistics (total videos, new videos since last check, subscriber count, total views).
- **✅ Content Affinity Analysis**: Users can analyze their "Liked Videos" playlist to see the most frequently occurring video topics and categories, providing insight into their content preferences.

#### Future Development Goals
The following features are planned for future development:

- **Activities**:
	- See which channels/creators the user has engaged with the most in a recent time period.
	- Better understand the roots behind the videos which were recommended (e.g., "Recommended because you watched video X").
- **Channel**:
	- Analyze the predominant topics across all subscribed channels.
	- Analyze overlaps between liked videos and subscriptions to provide deeper insights into content preferences.
- **Playlists/PlaylistItems**:
	- Extend content analysis (topics, categories, tags) to all user-created playlists, not just "Liked Videos".
	- Provide suggestions for new videos to add to existing playlists based on their existing content.
- **Subscriptions**:
	- **Subscription Recommendation Engine**: Suggest channels to unsubscribe from (due to inactivity or lack of engagement) and new channels to subscribe to based on viewing habits.

### 3. Backend Resource Requests

#### User-Related Playlists: Liked Videos, Uploads, and User-Created Playlists
Process for obtaining and using playlist IDs for different types of user-related playlists:

 **1. Liked Videos and Uploads Playlists - Obtain Playlist ID**
- Make a `GET` request to the `channels` endpoint.
- Set the `part` parameter to `contentDetails`.
- Set the `mine` parameter to `true` to specify the authenticated user's channel.
- The API response will contain a `contentDetails.relatedPlaylists` object.
	- The `likes` property of this object contains the playlist ID for the user's liked videos.
	- The `uploads` property contains the playlist ID for the user's uploaded videos.

**2. User-Created Playlists**
- Make a `GET` request to the `playlists` endpoint.
- Set the `part` parameter to `snippet,contentDetails`.
- Set the `mine` parameter to `true`.
- The API response will contain a list of playlist resources, each with its own `id`.

**3. Working with Playlist IDs using the `playlistItems` Resource**
- Make a `GET` request to the `playlistItems` endpoint.
- Set the `part` parameter to `snippet,contentDetails`.
- Set the `playlistId` parameter to the ID you obtained in the previous steps.
- The API response will contain a list of `playlistItem` resources, each representing a video in the playlist.


## Development Guidelines

When contributing to the `mytube_metrics` project, please follow these guidelines:

-   **Coding Style**: Follow the PEP 8 style guide for Python code.
-   **Testing**: Write unit tests for all new code and ensure that all existing tests pass.
-   **Documentation**: Add docstrings to all new functions and classes.
-   **Commit Messages**: Write clear and concise commit messages that describe the changes you have made.

## API Usage

The `mytube_metrics` project uses the YouTube Data API to access user data. The following API endpoints are used:

-   **`activities`**: Returns a list of the user's activities, such as likes, comments, and subscriptions.
-   **`channels`**: Returns information about a specific channel.
-   **`playlists`**: Returns a list of the user's playlists.
-   **`playlistItems`**: Returns a list of the videos in a specific playlist.
-   **`subscriptions`**: Returns a list of the user's subscriptions.
-   **`videos`**: Returns information about a specific video.

For more information about the YouTube Data API, please refer to the [official documentation](https://developers.google.com/youtube/v3/docs).

### Resources

**Parts of an HTTP Request**
- part
- channelId
- maxResults (Optional, default 5, max 50)
- key (API/OAuth)

Underneath each resource/endpoint name are the part query params.

Max 50 items per request; pageinate with `nextPageToken`.

#### Activities
- id - str
- snippet - object
	- publishedAt - datetime
	- channelId - str (channel performing activity)
	- channelTitle - str (name of yt channel performing activity)
	- title - str (resource name associated with activity)
	- type - str <-- dictates specific child attributes
		- `channelItem`
		- `like`
		- `playlistItem`
		- `promotedItem`
		- `recommendation`
		- `social`
		- `subscription`
		- `upload`
- contentDetails - object
	- upload - object
		- videoId - str
	- like - object
		- resourceId - object
			- videoId - str
	- favorite - object
		- resourceId - object
			- videoId - str
	- comment - object
		- resourceId - object
			- videoId - str
			- channelId - str (channel receiving the comment)
	- subscription - object
		- resourceId - object
			- channelId - str (channel who the user subscribed to)
	- playlistItem - object
		- resourceId - object
			- videoId - str (video added to playlist)
			- playlistId - str (playlist)
			- playlistItemId - str (uniquely identify the item within the playlist)
	- recommendation - object
		- resourceId - object
			- kind - str (e.g., youtube#video, youtube#channel)
			- videoId - str (only present if the recommended resource is a video)
			- channelId - str (only present if the recommended resource is a channel)
		- reason - str (videoFavorited, videoLiked, or videoWatched)
		- seedResourceId - object (what resource interaction caused YouTube to make the recommendation)
			- kind - str (youtube#video/channel/playlist)
			- videoId - str
			- channelId - str
			- playlistId - str

#### Channels
- id - str (yt channel id)
- snippet - object
	- title - str (public display name of yt channel)
	- description - str (public channel intro blurb)
	- publishedAt - datetime (ISO 8601 format; time channel was created)
	- thumbnail
- contentDetails - object
	- relatedPlaylists
		- likes (string for id of liked videos playlist; private to each user, requires OAuth 2.0)
		- uploads (string for id of channel's public videos containing every single video they've uploaded)
	- relatedPlaylists.uploads
- statistics - object
	- viewCount - unsigned long int (total views across all videos in all formats)
	- subscriberCount - unsigned long, rounded to 3 sig figs
	- videoCount (number of public videos)
- topicDetails - object
	- topicCategories - list of strings (wikipedia article URLs)
		- trim trailing slash -> split on last "/" -> URL-decode percent-encoded chars -> replace underscores with spaces -> remove " (sociology)" -> title-case

#### Playlists
- id - str (yt playlist id)
- snippet - object
	- publishedAt - datetime (ISO 8601)
	- channelId - str (channel which published the playlist; would be the authenticated user's channel if obtaining user-created playlists)
	- channelTitle - str
	- title - str (of playlist)
	- check out thumbnails for the playlist image
- status - object
	- privacyStatus - str (either private, public or unlisted)
- contentDetails - object
	- itemCount - unsigned int

#### PlaylistItems
- id - str
- snippet - object
	- publishedAt - datetime
	- channelId - str
	- title - str
	- description - str
	- thumbnails - object
	- channelTitle - str
	- videoOwnerChannelTitle - str
	- videoOwnerChannelId - str
	- playlistId - str
	- position - int
	- resourceId - object
		- kind - str
		- videoId - str
- contentDetails - object
	- videoId - str
	- videoPublishedAt - datetime
- status - object
	- privacyStatus - str

#### Subscriptions
- id - str
- snippet - object
	- publishedAt - datetime
	- title - str (channel title, the one being subscribed to)
	- description - str (channel description)
	- resourceId - object
		- kind - str (always youtube#channel)
		- channelId - str (channel being subscribed to)
	- channelId - str (user/subscriber's channel)
	- thumbnails - object
- contentDetails - object
	- totalItemCount - int (number of videos uploaded to subscribed channel)
	- newItemCount - int (number of new items uploaded to the subscribed channel since user last checked)

#### Videos
- id - str (yt video id)
- snippet - object
	- publishedAt - datetime
	- channelId - str
	- title - str
	- description - str
	- thumbnails - object
	- channelTitle - str
	- tags - list[str]
	- categoryId - str
	- liveBroadcastContent - str
	- defaultLanguage - str
	- localized - object
		- title - str
		- description - str
	- defaultAudioLanguage - str
- contentDetails - object
	- duration - str
	- dimension - str
	- definition - str
	- caption - str
	- licensedContent - bool
	- regionRestriction - object
	- contentRating - object
	- projection - str
	- hasCustomThumbnail - bool
- status - object
	- uploadStatus - str
	- failureReason - str
	- rejectionReason - str
	- privacyStatus - str
	- publishAt - datetime
	- license - str
	- embeddable - bool
	- publicStatsViewable - bool
	- madeForKids - bool
	- selfDeclaredMadeForKids - bool
- statistics - object
	- viewCount - unsigned long
	- likeCount - unsigned long
	- favoriteCount - unsigned long
	- commentCount - unsigned long
- player - object
	- embedHtml - str
	- embedHeight - long
	- embedWidth - long
- topicDetails - object
	- topicIds - list[str]
	- relevantTopicIds - list[str]
	- topicCategories - list[str]
- recordingDetails - object
	- recordingDate - datetime
- fileDetails - object
	- fileName - str
	- fileSize - unsigned long
	- fileType - str
	- container - str
	- videoStreams - list[object]
	- audioStreams - list[object]
	- durationMs - unsigned long
	- bitrateBps - unsigned long
	- creationTime - str

## Database Schema

The `mytube_metrics` project uses a MySQL database to store user data. The database schema is as follows:

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    access_token VARCHAR(255) NOT NULL,
    refresh_token VARCHAR(255) NOT NULL
);
```

## Future Ideas

-   **Data Portability API**: Explore the use of the Data Portability API to access additional user data, such as watch history and search history.
-   **Recommendation Engine**: Create a recommendation engine that suggests new videos and channels to the user based on their viewing habits.
-   **Sentiment Analysis**: Perform sentiment analysis on video comments to determine the overall sentiment of a video.
-   **Machine Learning**: Use machine learning to build predictive models that can identify trends in the user's viewing habits.
-   **Google Takeout**: Explore using Google Takeout data to analyze watch and search history.
-   **Playlist Management**: Create a new watch-later playlist that is cleaned up automatically.
