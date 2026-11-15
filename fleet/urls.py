from django.urls import path
from . import views

urlpatterns = [
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
]