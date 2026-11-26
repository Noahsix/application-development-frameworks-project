from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/<int:id>/', views.vehicle_detail, name='vehicle_detail'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
]
