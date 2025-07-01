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
    python src/mytube_metrics/main.py
    ```

## Project Structure

The `mytube_metrics` project is organized as follows:

```
/Users/jerry/Desktop/python/projects/mytube_metrics/
├───src/
│   └───mytube_metrics/
│       ├───api/
│       │   ├───__init__.py
│       │   └───client.py
│       ├───static/
│       │   ├───css/
│       │   └───js/
│       ├───templates/
│       ├───auth.py
│       ├───database.py
│       ├───main.py
│       ├───metric_analyzer.py
│       └───metric_visualizer.py
├───venv/ <-- ignore this folder, as it contains a ton of files from libraries
├───.env <-- ignore this folder as well, since it contains secrets
├───.gitignore
├───channel_endpoint.py
├───channel_example.json
├───diagram.puml
└───users.sql
```

-   **`src/mytube_metrics`**: The main application directory.
    -   **`api`**: Contains the YouTube Data API client.
        -   **`__init__.py`**: Initializes the `api` package.
        -   **`client.py`**: A client for interacting with the YouTube Data API.
    -   **`static`**: Contains static files, such as CSS and JavaScript.
    -   **`templates`**: Contains HTML templates for the web application.
    -   **`auth.py`**: Handles user authentication and authorization.
    -   **`database.py`**: Manages the connection to the MySQL database.
    -   **`main.py`**: The main entry point for the application.
    -   **`metric_analyzer.py`**: Analyzes the user's YouTube data and calculates various metrics.
    -   **`metric_visualizer.py`**: Creates visualizations of the user's YouTube data.
-   **`.env`**: Contains environment variables for the project.
-   **`.gitignore`**: Specifies which files and directories to ignore in Git.
-   **`channel_endpoint.py`**: A script for testing the YouTube Data API's `channels` endpoint.
-   **`channel_example.json`**: An example of the JSON response from the `channels` endpoint.
-   **`diagram.puml`**: A PlantUML diagram of the project's architecture.
-   **`users.sql`**: A SQL script for creating the `users` table in the database.

## User-Centric Functionalities

### 1. Authorization/Authentication
Users are able to log into the web app and securely authenticate their Google Account for the app to access (read-only) information about their YouTube profile.

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
Users should have a variety of options once they have logged into the app to check detailed information regarding their own YouTube account. They can be broadly divided into a few categories based on Google's YouTube Data API endpoints/resources. Each bullet point below the resource name specifies something that the user should be able to "do" with the web app / final project.

- **Activities** - why certain videos were recommended, what videos the user has liked, any recent subscriptions, comments
	- See which channels/creators the user has engaged with the most in recent time period.
	- Better understand the roots behind the videos which were recommended. (look into more)
		- (Look Familiar?) Due to x/y/z videos/channels/playlists you watched, these recent recommendations were made.
- **Channel** - channel stats, topics, ID of liked videos playlist + uploaded videos playlist --> goes to Playlists Resource
	- See channel stats of subscribed channels (view/sub/vid ct) as well as the predominant topics across subscriptions.
		- by channel ID
	- Analyze any overlaps between liked videos and subscriptions and potentially conduct analysis of the types of content the user likes.
- **Playlists/PlaylistItems** - general playlist info (with ids of specific videos) + related channel
	- View common threads across liked videos within liked videos playlist. Specifically, display most frequently occuring categories (categoryId) and potentially video tag frequencies.
	- Analyze common topics of videos within user-created playlists and suggest new editions for each playlist (since there is likely some distinction in specific topics)
- **Subscriptions** - who the user has subscribed to, number of items total from creator + number of new uploads since the user last checked
	- Subscription recommendation engine: suggest who to unsubscribe from if you haven't watched them in a long time or their channel is inactive, suggest subscriptions based on whether you've been consuming a lot of a specific channel's content recently
	- See how popular each channel you've subscribed to is (subscriber count, total views, video count)

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
		- trim trailing slash -> split on last "/" -> URL-decode percent-encoded chars -> replace underscores with spaces -> title-case

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
