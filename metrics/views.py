from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from .models import UserCredential
from .utils.api_client import YouTubeClient
from .utils.auth_helper import OAuth

# --- Initial Login Page ---
def google_login(request):
    # Check if user is already logged in
    if request.user.is_authenticated:
        return redirect('dashboard') # refer to URL path by name (avoid hardcoding)

    # Check if user was redirected here after attempting to access a protected page
    if 'next' in request.GET:
        request.session['next'] = request.GET['next']
        
    # Check if user pressed "Login with Google" button in metrics/login.html
    if request.method == 'POST':
        oauth = OAuth()
        authorization_url, state = oauth.get_authorization_url()

        request.session['oauth_state'] = state

        return redirect(authorization_url)
    
    # Typical scenario (user navigates to login page via a GET request)
    return render(request, 'metrics/login.html')

# --- OAuth Flow (callback/) ---
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
import requests

def google_callback(request):
    state = request.session.pop('oauth_state', None)
    if not state:
        return redirect('login')

    oauth = OAuth()
    authorization_response = request.build_absolute_uri()
    credentials = oauth.fetch_credentials(state, authorization_response)
    
    # Use the credentials to get user info
    user_info_response = requests.get(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f'Bearer {credentials.token}'}
    )
    user_info = user_info_response.json()

    # Create or get the user in auth_user table
    user, created = User.objects.get_or_create(
        email=user_info['email'],
        defaults={
            'username': user_info['email'],
            'first_name': user_info.get('given_name', ''),
            'last_name': user_info.get('family_name', ''),
        }
    )

    # Log the user in (creates session for user in Django)
    login(request, user)

    # Save the credentials in metrics_usercredential table
    user_credential, created = UserCredential.objects.get_or_create(user=user)
    user_credential.access_token = credentials.token
    if credentials.refresh_token:
        user_credential.refresh_token = credentials.refresh_token
    user_credential.profile_picture_url = user_info.get('picture', '')
    user_credential.save() # commit changes to database

    next_url = request.session.pop('next', 'dashboard')
    return redirect(next_url)

# --- Dashboard Home Page (dashboard/) ---
@login_required # sends user to LOGIN_URL in settings.py if not already logged in
def dashboard(request):
    return render(request, 'metrics/dashboard.html')

# --- Subscription Insights (subscriptions/) ---
from google.auth.exceptions import RefreshError

@login_required
def subscriptions_list(request):
    user_credentials = request.user.usercredential
    
    try:
        client = YouTubeClient(credentials=user_credentials)
        
        page_num = int(request.GET.get('page', 1))
        subscription_generator = client.subscriptions.stream_user_subscriptions()

        # Get the paginated subscription data
        from .services.subscription_analyzer import get_paginated_subscriptions
        pagination_data = get_paginated_subscriptions(
            subscription_generator, 
            page_num=page_num,
        )

        # Get additional statistics on current page of subscriptions (25 max)
        subs_on_page = pagination_data.get('subscriptions', {}) # dictionaries mapping channel ids to channel data
        if subs_on_page:
            channel_ids = [channel_id for channel_id in subs_on_page]
            raw_channel_stats = client.channels.list(channel_ids=",".join(channel_ids))
            processed_channel_stats = client.channels.process_raw_stats(raw_channel_stats)

            for channel_id, channel_data in subs_on_page.items():
                if channel_id in processed_channel_stats:
                    channel_data.update(processed_channel_stats[channel_id])

        return render(request, 'metrics/subscriptions_list.html', pagination_data)
    except RefreshError:
        # If refresh token is expired or revoked, re-authenticate the user
        logout(request)
        return redirect('login')

# --- Content Affinity Analysis (content_affinity/) ---
@login_required
def content_affinity(request):
    user_credentials = request.user.usercredential

    try:
        from .services.content_analyzer import get_content_affinity_context

        context = get_content_affinity_context(request.user)
        
        client = YouTubeClient(credentials=user_credentials)

        raw_channel_data = client.channels.list(mine=True)
        processed_channel_data = client.channels.process_raw_stats(raw_channel_data)
        
        # Obtain user's primary channel's data from the dictionary of processed channels
        first_channel_data = next(iter(processed_channel_data.values()), None)
        liked_videos_playlist_id = first_channel_data.get('liked_videos_playlist_id', "") if first_channel_data else ""
        if liked_videos_playlist_id:
            # Create context dictionary
            raw_playlist_items = client.playlist_items.list(playlist_id=liked_videos_playlist_id)
            processed_playlist_items = client.playlist_items.process_raw_items(raw_playlist_items)

        return render(request, 'metrics/content_affinity.html', context)
    except RefreshError:
        logout(request)
        return redirect('login')


# --- Logout Page (logout/) ---

def user_logout(request):
    logout(request)
    return redirect('login')