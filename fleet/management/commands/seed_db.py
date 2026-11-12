"""
Komenda wypełniająca bazę danymi testowymi.

Użycie:
    python manage.py migrate
    python manage.py seed_db

Tworzy (lub aktualizuje, jeśli już istnieją):
  - 1 konto administratora  (admin / admin123)      -> dostęp do /admin/
  - 1 konto pracownika      (pracownik / pracownik123) -> zwykły użytkownik
  - 5 przykładowych samochodów

Komendę można uruchamiać wielokrotnie – nie tworzy duplikatów,
a dane wracają do stanu początkowego.
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from fleet.models import Vehicle

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


class Command(BaseCommand):
    help = 'Tworzy konto administratora, konto pracownika i 5 przykładowych samochodów.'

    @transaction.atomic
    def handle(self, *args, **options):
        self._create_user(ADMIN, is_admin=True)
        self._create_user(EMPLOYEE, is_admin=False)

        for data in VEHICLES:
            vehicle, created = Vehicle.objects.update_or_create(
                registration_number=data['registration_number'],
                defaults=data,
            )
            self._log(created, f'Pojazd: {vehicle}')

        self.stdout.write(self.style.SUCCESS('\nBaza testowa gotowa. Konta do logowania:'))
        self.stdout.write(f"  administrator: {ADMIN['username']} / {ADMIN['password']}")
        self.stdout.write(f"  pracownik:     {EMPLOYEE['username']} / {EMPLOYEE['password']}")

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
