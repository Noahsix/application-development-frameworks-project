from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView

from .forms import ReservationFilterForm, VehicleSearchForm
from .models import Reservation, Vehicle


class HomeView(TemplateView):
    template_name = 'fleet/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vehicle_count'] = Vehicle.objects.count()
        context['available_count'] = Vehicle.objects.filter(status='available').count()
        context['rented_count'] = Vehicle.objects.filter(status='rented').count()
        context['service_count'] = Vehicle.objects.filter(status='service').count()
        user = self.request.user
        if user.is_authenticated:
            reservations = Reservation.objects.all() if user.is_staff else user.reservations.all()
            context['my_active_count'] = reservations.filter(status__in=['pending', 'active']).count()
        return context


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


@login_required
def my_reservations(request):
    # Administrator widzi rezerwacje wszystkich pracowników, zwykły użytkownik tylko swoje.
    if request.user.is_staff:
        reservations = Reservation.objects.all()
    else:
        reservations = Reservation.objects.filter(user=request.user)

    reservations = reservations.select_related('vehicle', 'user').order_by('-start_date')
    form = ReservationFilterForm(request.GET)

    if form.is_valid():
        query = form.cleaned_data.get('query')
        status = form.cleaned_data.get('status')

        if query:
            reservations = reservations.filter(
                Q(purpose__icontains=query) |
                Q(vehicle__brand__icontains=query) |
                Q(vehicle__model__icontains=query) |
                Q(vehicle__registration_number__icontains=query)
            )

        if status:
            reservations = reservations.filter(status=status)

    context = {
        'reservations': reservations,
        'form': form,
        'show_all': request.user.is_staff,
    }
    return render(request, 'fleet/my_reservations.html', context)
