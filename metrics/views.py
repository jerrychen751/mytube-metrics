from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from .utils.auth_helper import OAuth
from .models import UserCredential
from .utils.api_client import YouTubeClient

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
from django.contrib.auth import login
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
@login_required
def subscriptions_list(request):
    user_credentials = request.user.usercredential
    client = YouTubeClient(credentials=user_credentials)
    
    page_num = int(request.GET.get('page', 1))
    subscription_generator = client.subscriptions.list_all_user_subscriptions()
    if not subscription_generator:
        print("none")

    # Get the paginated data from the analyzer
    from .services.subscription_analyzer import get_paginated_subscriptions
    pagination_data = get_paginated_subscriptions(
        subscription_generator, 
        page_num=page_num,
    )

    return render(request, 'metrics/subscriptions_list.html', pagination_data)

# --- Logout Page (logout/) ---
from django.contrib.auth import logout

def user_logout(request):
    logout(request)
    return redirect('login')