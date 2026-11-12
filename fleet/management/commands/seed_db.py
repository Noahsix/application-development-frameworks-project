"""
Komenda wypełniająca bazę danymi testowymi.

Użycie:
    python manage.py migrate
    python manage.py seed_db            # utwórz / zaktualizuj dane testowe
    python manage.py seed_db --reset    # najpierw usuń wszystkie pojazdy,
                                        # rezerwacje i wpisy serwisowe

Tworzy (lub aktualizuje, jeśli już istnieją):
  - 1 konto administratora  (admin / admin123)         -> dostęp do /admin/
  - 1 konto pracownika      (pracownik / pracownik123) -> zwykły użytkownik
  - 5 przykładowych samochodów
  - 3 rezerwacje (zakończoną, aktywną i oczekującą)
  - 2 wpisy serwisowe

Daty rezerwacji i serwisów liczone są względem dzisiejszej daty, więc
„aktywna” rezerwacja zawsze obejmuje dzisiaj, a „oczekująca” jest w przyszłości.

Komendę można uruchamiać wielokrotnie – nie tworzy duplikatów,
a dane wracają do stanu początkowego.
"""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from fleet.models import Reservation, ServiceLog, Vehicle

ADMIN = {
    'username': 'admin',
    'password': 'admin123',
    'email': 'admin@flota.local',
    'first_name': 'Adam',
    'last_name': 'Administrator',
}

EMPLOYEE = {
    'username': 'pracownik',
    'password': 'pracownik123',
    'email': 'pracownik@flota.local',
    'first_name': 'Jan',
    'last_name': 'Kowalski',
}

VEHICLES = [
    {'registration_number': 'SC 12345', 'brand': 'Toyota', 'model': 'Corolla',
     'production_year': 2021, 'mileage': 45200, 'status': 'available'},
    {'registration_number': 'SC 23456', 'brand': 'Skoda', 'model': 'Octavia',
     'production_year': 2020, 'mileage': 78900, 'status': 'available'},
    {'registration_number': 'SC 34567', 'brand': 'Volkswagen', 'model': 'Golf',
     'production_year': 2019, 'mileage': 102300, 'status': 'rented'},
    {'registration_number': 'SC 45678', 'brand': 'Ford', 'model': 'Focus',
     'production_year': 2018, 'mileage': 131750, 'status': 'service'},
    {'registration_number': 'SC 56789', 'brand': 'Kia', 'model': 'Ceed',
     'production_year': 2023, 'mileage': 12400, 'status': 'available'},
]

# Daty podane jako przesunięcie w dniach względem dzisiaj.
# Statusy są spójne ze statusami pojazdów powyżej
# (Golf jest „Wypożyczony” -> ma aktywną rezerwację).
RESERVATIONS = [
    {'vehicle': 'SC 12345', 'customer_name': 'Anna Nowak',
     'customer_email': 'anna.nowak@example.com',
     'start': -20, 'end': -15, 'status': 'completed'},
    {'vehicle': 'SC 34567', 'customer_name': 'Piotr Wiśniewski',
     'customer_email': 'piotr.wisniewski@example.com',
     'start': -2, 'end': 5, 'status': 'active'},
    {'vehicle': 'SC 56789', 'customer_name': 'Katarzyna Zielińska',
     'customer_email': 'katarzyna.zielinska@example.com',
     'start': 7, 'end': 10, 'status': 'pending'},
]

# Ford jest „W serwisie” -> ma bieżący wpis serwisowy.
SERVICE_LOGS = [
    {'vehicle': 'SC 23456', 'days_ago': 45,
     'description': 'Przegląd okresowy, wymiana oleju i filtrów.',
     'cost': Decimal('650.00')},
    {'vehicle': 'SC 45678', 'days_ago': 1,
     'description': 'Wymiana sprzęgła i koła dwumasowego.',
     'cost': Decimal('3200.00')},
]


class Command(BaseCommand):
    help = ('Tworzy konto administratora, konto pracownika, 5 przykładowych '
            'samochodów, rezerwacje i wpisy serwisowe.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Przed wstawieniem danych usuwa WSZYSTKIE pojazdy, rezerwacje '
                 'i wpisy serwisowe (konta użytkowników zostają).',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['reset']:
            self._reset()

        self._create_user(ADMIN, is_admin=True)
        self._create_user(EMPLOYEE, is_admin=False)

        vehicles = {}
        for data in VEHICLES:
            vehicle, created = self._upsert(
                Vehicle,
                lookup={'registration_number': data['registration_number']},
                values=data,
            )
            vehicles[vehicle.registration_number] = vehicle
            self._log(created, f'Pojazd: {vehicle}')

        today = timezone.localdate()

        for data in RESERVATIONS:
            reservation, created = self._upsert(
                Reservation,
                lookup={
                    'vehicle': vehicles[data['vehicle']],
                    'customer_email': data['customer_email'],
                },
                values={
                    'customer_name': data['customer_name'],
                    'start_date': today + timedelta(days=data['start']),
                    'end_date': today + timedelta(days=data['end']),
                    'status': data['status'],
                },
            )
            self._log(created, f'{reservation} [{reservation.get_status_display()}]')

        for data in SERVICE_LOGS:
            log, created = self._upsert(
                ServiceLog,
                lookup={
                    'vehicle': vehicles[data['vehicle']],
                    'description': data['description'],
                },
                values={
                    'service_date': today - timedelta(days=data['days_ago']),
                    'cost': data['cost'],
                },
            )
            self._log(created, str(log))

        self.stdout.write(self.style.SUCCESS('\nBaza testowa gotowa. Konta do logowania:'))
        self.stdout.write(f"  administrator: {ADMIN['username']} / {ADMIN['password']}")
        self.stdout.write(f"  pracownik:     {EMPLOYEE['username']} / {EMPLOYEE['password']}")

    def _reset(self):
        # Kolejność: najpierw obiekty zależne, potem pojazdy.
        service_count, _ = ServiceLog.objects.all().delete()
        reservation_count, _ = Reservation.objects.all().delete()
        vehicle_count, _ = Vehicle.objects.all().delete()
        self.stdout.write(self.style.WARNING(
            f'Usunięto: {vehicle_count} pojazdów, {reservation_count} rezerwacji, '
            f'{service_count} wpisów serwisowych.'
        ))

    def _upsert(self, model, lookup, values):
        """Pobiera obiekt po `lookup` albo tworzy nowy, ustawia `values`,
        uruchamia walidację modelu (full_clean -> m.in. Reservation.clean)
        i zapisuje. Zwraca (obiekt, czy_utworzono)."""
        obj = model.objects.filter(**lookup).first()
        created = obj is None
        if created:
            obj = model(**lookup)
        for field, value in values.items():
            setattr(obj, field, value)
        obj.full_clean()
        obj.save()
        return obj, created

    def _create_user(self, data, is_admin):
        User = get_user_model()
        user, created = User.objects.get_or_create(username=data['username'])
        user.email = data['email']
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.is_active = True
        user.is_staff = is_admin
        user.is_superuser = is_admin
        user.set_password(data['password'])
        user.save()
        role = 'administrator' if is_admin else 'pracownik'
        self._log(created, f'Użytkownik ({role}): {user.username}')

    def _log(self, created, text):
        prefix = 'Utworzono' if created else 'Zaktualizowano'
        self.stdout.write(f'  {prefix} – {text}')
