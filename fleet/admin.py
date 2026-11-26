from django.contrib import admin
from .models import Vehicle, Reservation, ServiceLog


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'registration_number', 'production_year', 'mileage', 'status')
    list_filter = ('status', 'brand', 'production_year')
    search_fields = ('brand', 'model', 'registration_number')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'user', 'purpose', 'customer_name', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'user', 'start_date', 'end_date')
    search_fields = ('customer_name', 'customer_email', 'purpose', 'user__username', 'vehicle__registration_number', 'vehicle__brand')


@admin.register(ServiceLog)
class ServiceLogAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'service_date', 'cost', 'description')
    list_filter = ('service_date', 'vehicle')
    search_fields = ('vehicle__registration_number', 'vehicle__brand', 'description')