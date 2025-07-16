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