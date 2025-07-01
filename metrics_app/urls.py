from django.urls import path
from . import views

urlpatterns = [
    path('', views.google_login, name='login'),
    path('callback/', views.google_callback, name='callback'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
]