from django.shortcuts import get_object_or_404, render
from .models import Vehicle

# Create your views here.

def vehicle_detail(request, id):
    vehicle = get_object_or_404(Vehicle, id=id)
    reservations = vehicle.reservations.all().order_by('-start_date')
    service_logs = vehicle.service_logs.all().order_by('-service_date')

    context = {
        'vehicle': vehicle,
        'reservations': reservations,
        'service_logs': service_logs,
    }
    return render(request, 'fleet/vehicle_detail.html', context)