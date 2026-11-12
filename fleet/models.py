from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class Vehicle(models.Model):
    STATUS_CHOICES = [
        ('available', 'Dostępny'),
        ('rented', 'Wypożyczony'),
        ('service', 'W serwisie'),
    ]

    brand = models.CharField(max_length=100, verbose_name="Marka")
    model = models.CharField(max_length=100, verbose_name="Model")
    registration_number = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Numer rejestracyjny"
    )
    production_year = models.PositiveIntegerField(verbose_name="Rok produkcji")
    mileage = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="Przebieg (km)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name="Status"
    )

    class Meta:
        verbose_name = "Pojazd"
        verbose_name_plural = "Pojazdy"

    def __str__(self):
        return f"{self.brand} {self.model} ({self.registration_number})"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Oczekująca'),
        ('active', 'Aktywna'),
        ('completed', 'Zakończona'),
        ('cancelled', 'Anulowana'),
    ]

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name="Pojazd"
    )
    customer_name = models.CharField(max_length=150, verbose_name="Imię i nazwisko klienta")
    customer_email = models.EmailField(verbose_name="E-mail klienta")
    start_date = models.DateField(verbose_name="Data wypożyczenia")
    end_date = models.DateField(verbose_name="Data zwrotu")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status rezerwacji"
    )

    class Meta:
        verbose_name = "Rezerwacja"
        verbose_name_plural = "Rezerwacje"

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({
                'end_date': 'Data zwrotu nie może być wcześniejsza niż data wypożyczenia.'
            })

    def __str__(self):
        return f"Rezerwacja: {self.vehicle} ({self.start_date} - {self.end_date})"


class ServiceLog(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='service_logs',
        verbose_name="Pojazd"
    )
    service_date = models.DateField(verbose_name="Data serwisu")
    description = models.TextField(verbose_name="Opis wykonanych prac")
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Koszt (PLN)"
    )

    class Meta:
        verbose_name = "Wpis serwisowy"
        verbose_name_plural = "Historia serwisowa"

    def __str__(self):
        return f"Serwis {self.vehicle.registration_number} z dnia {self.service_date} ({self.cost} PLN)"