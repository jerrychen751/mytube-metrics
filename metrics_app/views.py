from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import json

from .utils.auth_helper import OAuth
from .models import UserCredential

def google_login(request):
    if 'next' in request.GET:
        request.session['next'] = request.GET['next']
        
    if request.method == 'POST':
        oauth = OAuth()
        authorization_url, state = oauth.get_authorization_url()

        request.session['oauth_state'] = state

        return redirect(authorization_url)
    return render(request, 'metrics_app/login.html')

from django.contrib.auth import login
from django.contrib.auth.models import User
import requests

def google_callback(request):
    state = request.session.pop('oauth_state', None)
    if not state:
        return redirect('login')

    oauth = OAuth()
    authorization_response = request.build_absolute_uri()
    credentials = oauth.fetch_and_store_credentials(state, authorization_response)

    # Use the credentials to get user info
    user_info_response = requests.get(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f'Bearer {credentials.token}'}
    )
    user_info = user_info_response.json()

    # Create or get the user
    user, created = User.objects.get_or_create(
        email=user_info['email'],
        defaults={'username': user_info['email']}
    )

    # Log the user in
    login(request, user)

    # Save the credentials
    user_credential, created = UserCredential.objects.get_or_create(user=user)
    user_credential.access_token = credentials.token
    if credentials.refresh_token:
        user_credential.refresh_token = credentials.refresh_token
    user_credential.save()

    next_url = request.session.pop('next', 'dashboard')
    return redirect(next_url)

@login_required
def dashboard(request):
    return render(request, 'metrics_app/dashboard.html')

from django.contrib.auth import logout

def user_logout(request):
    logout(request)
    return redirect('login')
