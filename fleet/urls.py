from django.urls import path
from . import views

urlpatterns = [
    path('vehicles/<int:id>/', views.vehicle_detail, name='vehicle_detail'),
]