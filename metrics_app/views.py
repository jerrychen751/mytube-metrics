from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import json

from .utils.auth_helper import OAuth
from .models import UserCredential

def google_login(request):
    if request.method == 'POST':
        oauth = OAuth()
        authorization_url, state = oauth.get_authorization_url()

        request.session['oauth_state'] = state

        return redirect(authorization_url)
    return render(request, 'metrics_app/login.html')

def google_callback(request):
    state = request.session.pop('oauth_state', None)
    if not state:
        return redirect('login')

    oauth = OAuth()
    authorization_response = request.build_absolute_uri()
    credentials = oauth.fetch_and_store_credentials(state, authorization_response)

    # If the user is authenticated with Django, save their credentials
    if request.user.is_authenticated:
        UserCredential.objects.update_or_create(
            user=request.user,
            defaults={
                'access_token': credentials.token,
                'refresh_token': credentials.refresh_token,
            }
        )

    return redirect('dashboard')

@login_required
def dashboard(request):
    return render(request, 'metrics_app/dashboard.html')

from django.contrib.auth import logout

def user_logout(request):
    logout(request)
    return redirect('login')
