from django.urls import path
from . import views

urlpatterns = [
    path('', views.parking_map, name='parking_map'),
    path('parking/', views.parking_map, name='parking_map'),
    path('register/', views.register, name='register'),
    path('settings/', views.user_settings, name='user_settings'),
]