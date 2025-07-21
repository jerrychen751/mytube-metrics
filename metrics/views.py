# Standard Library Imports
import zipfile

# Third-Party Imports
import requests
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from google.auth.exceptions import RefreshError

# Local App Imports
from .models import UserCredential
from .services.activity_analyzer import get_recommended_videos_context
from .services.content_analyzer import get_content_affinity_context
from .services.history_analyzer import process_takeout_data
from .services.subscription_analyzer import get_subscription_list_context
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
    user, _ = User.objects.get_or_create(
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
@login_required
def subscriptions_list(request):
    try:
        page_num = int(request.GET.get('page', 1))
        context = get_subscription_list_context(request.user, page_num)
        return render(request, 'metrics/subscriptions_list.html', context)
    except RefreshError:
        # If refresh token is expired or revoked, re-authenticate the user
        logout(request)
        return redirect('login')

# --- Content Affinity Analysis (content_affinity/) ---
@login_required
def content_affinity(request):
    try:
        context = get_content_affinity_context(request.user)
        return render(request, 'metrics/content_affinity.html', context)
    except RefreshError:
        logout(request)
        return redirect('login')

# --- Logout Page (logout/) ---
def user_logout(request):
    logout(request)
    return redirect('login')

# --- Recommended Videos Page (recommended-videos/) ---
@login_required
def recommended_videos(request):
    try:
        # Clear recommended video IDs from session when the page is loaded
        request.session.pop('recommended_video_ids', None)
        return render(request, 'metrics/recommended_videos.html')
    except RefreshError:
        logout(request)
        return redirect('login')

# --- AJAX Endpoint for Recommended Videos ---
@login_required
def get_recommended_videos_ajax(request): # called by activities.js
    try:
        context = get_recommended_videos_context(request)
        return JsonResponse(context) # send jSON data back to activities.js
    except RefreshError:
        logout(request)
        return redirect('login')
    
# --- Viewing Habit Evolution (viewing-evolution/) ---
@login_required
def viewing_evolution(request):
    try:
        if request.method == 'POST' and 'takeout-zip' in request.FILES:
            # InMemoryUploadedFile object from Django, or TemporaryUploadedFile if file is large
            uploaded_zip = request.FILES['takeout-zip']

            try:
                with zipfile.ZipFile(uploaded_zip.read(), 'r') as zf: # no need for 'rb'
                    # .read() returns a `bytes` object; io.BytesIO creates in-memory binary stream

                    # Find the watch history file
                    watch_history_file = None
                    for file_name in zf.namelist():
                        if 'watch-history.json' in file_name:
                            watch_history_file = file_name # full path to watch-history.json file
                            break
                    
                    if watch_history_file:
                        with zf.open(watch_history_file) as json_file:
                            # `json_file` is a ZipExtFile object which behaves like a regular file
                            # `.read()` decompresses binary data --> `.decode()` converts binary into Unicode string
                            # UTF-8 is format for storing Unicode as bytes
                            file_content = json_file.read().decode('utf-8') # string
                            analysis_results = process_takeout_data(file_content)
                            context = {'analysis_results': analysis_results}
                        return render(request, 'metrics/viewing_evolution.html', context)
                    
                    # No watch-history.json file found
                    context = {'error': 'watch-history.json not found in the uploaded .zip file.'}
                    return render(request, 'metrics/viewing_evolution.html', context)

            except zipfile.BadZipFile: # if zipfile.ZipFile() cannot interpret uploaded file, catch error
                context = {'error': 'Invalid .zip file.'}
                return render(request, 'metrics/viewing_evolution.html', context)
        
        return render(request, 'metrics/viewing_evolution.html')
    except RefreshError:
        logout(request)
        return redirect('login')