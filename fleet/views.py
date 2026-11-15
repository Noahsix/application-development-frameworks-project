from django.shortcuts import render
from django.db.models import Q
from .models import Vehicle
from .forms import VehicleSearchForm


def vehicle_list(request):
    vehicles = Vehicle.objects.all()
    form = VehicleSearchForm(request.GET)

    if form.is_valid():
        query = form.cleaned_data.get('query')
        status = form.cleaned_data.get('status')

        if query:
            vehicles = vehicles.filter(
                Q(brand__icontains=query) |
                Q(model__icontains=query) |
                Q(registration_number__icontains=query)
            )

        if status:
            vehicles = vehicles.filter(status=status)

    context = {
        'vehicles': vehicles,
        'form': form,
    }
    return render(request, 'fleet/vehicle_list.html', context)