import json
import os
import zipfile
import shutil

from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import UserCredential
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
    try:
        page_num = int(request.GET.get('page', 1))
        from .services.subscription_analyzer import get_subscription_list_context
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
        from .services.content_analyzer import get_content_affinity_context
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
        from .services.activity_analyzer import get_recommended_videos_context
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
            uploaded_file = request.FILES['takeout-zip']

            if not uploaded_file.name.endswith('.zip'):
                return JsonResponse({'status': 'error', 'message': 'Only .zip files are allowed.'}, status=400)

            # Define a temporary directory for uploads
            temp_dir = os.path.join('/tmp', 'takeout_uploads') # Using /tmp for temporary files
            os.makedirs(temp_dir, exist_ok=True)
            temp_zip_path = os.path.join(temp_dir, uploaded_file.name)
            extracted_path = os.path.join(temp_dir, uploaded_file.name + '_extracted')

            try:
                # Save the uploaded zip file temporarily
                with open(temp_zip_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                # Extract the zip file
                with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extracted_path)

                # Locate watch-history.json within the extracted files
                watch_history_json_path = None
                for root, _, files in os.walk(extracted_path):
                    for file in files:
                        if file.lower() == 'watch-history.json':
                            watch_history_json_path = os.path.join(root, file)
                            break
                    if watch_history_json_path:
                        break

                if not watch_history_json_path:
                    return JsonResponse({'status': 'error', 'message': 'watch-history.json not found in the uploaded zip file.'}, status=400)

                # Read the content of watch-history.json
                with open(watch_history_json_path, 'r', encoding='utf-8') as json_file:
                    file_content = json_file.read()
                
                from .services.history_analyzer import process_takeout_data
                analysis_results = process_takeout_data(file_content)
                
                context = {'analysis_results': analysis_results}
                return render(request, 'metrics/viewing_evolution.html', context)

            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            finally:
                # Clean up temporary files and directory
                if os.path.exists(temp_zip_path):
                    os.remove(temp_zip_path)
                if os.path.exists(extracted_path):
                    shutil.rmtree(extracted_path)
        
        return render(request, 'metrics/viewing_evolution.html')
    except RefreshError:
        logout(request)
        return redirect('login')