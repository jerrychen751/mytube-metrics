# Third-Party Imports
from django.urls import path

# Local App Imports
from . import views

urlpatterns = [
    path('', views.google_login, name='login'),
    path('callback/', views.google_callback, name='callback'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('subscriptions/', views.subscriptions_list, name='subscriptions_list'),
    path('content_affinity/', views.content_affinity, name='content_affinity'),
    path('recommended-videos/', views.recommended_videos, name='recommended_videos'),
    path('recommended-videos/ajax/', views.get_recommended_videos_ajax, name='get_recommended_videos_ajax'),
    path('viewing-evolution/', views.viewing_evolution, name='viewing_evolution'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
]

# use `name` argument to avoid hardcoding (change URL path w/o changing references throughout code)