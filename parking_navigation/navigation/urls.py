from django.urls import path
from . import views

urlpatterns = [
    path('parking/', views.parking_map, name='parking_map'),
]