# System Zarządzania Flotą

Aplikacja webowa w Django do zarządzania firmową flotą samochodów. Pozwala
przeglądać i wyszukiwać pojazdy, sprawdzać historię ich rezerwacji i serwisów,
a zalogowanym pracownikom przeglądać własne rezerwacje. Administrator widzi
rezerwacje wszystkich pracowników i zarządza danymi w panelu `/admin/`.

## Spis treści

1. [Technologie](#technologie)
2. [Wymagania](#wymagania)
3. [Pierwsze uruchomienie](#pierwsze-uruchomienie)
4. [Kolejne uruchomienia](#kolejne-uruchomienia)
5. [Dane testowe – `seed_db`](#dane-testowe--seed_db)
6. [Role i konta testowe](#role-i-konta-testowe)
7. [Funkcje i adresy stron](#funkcje-i-adresy-stron)
8. [Model danych](#model-danych)
9. [Struktura projektu](#struktura-projektu)
10. [Praca zespołowa z Gitem](#praca-zespołowa-z-gitem)
11. [Najczęstsze problemy](#najczęstsze-problemy)

## Technologie

- **Python 3.12+**
- **Django 6.1** – backend, ORM, system szablonów, uwierzytelnianie, panel admina
- **SQLite** – lokalna baza danych (plik `db.sqlite3`, tworzony automatycznie)
- **Bootstrap 5.3** – wygląd stron (ładowany z CDN, nic nie trzeba instalować)

## Wymagania

- Python w wersji **3.12 lub nowszej** (Django 6.1 nie działa na starszych).
  Sprawdzenie wersji:
  ```bash
  python3 --version          # macOS / Linux
  python --version           # Windows
  ```
  Instalacja: [python.org/downloads](https://www.python.org/downloads/) lub na macOS `brew install python`.
- Git

## Pierwsze uruchomienie

```bash
# 1. Pobranie repozytorium
git clone https://github.com/Noahsix/application-development-frameworks-project.git
cd application-development-frameworks-project

# 2. Wirtualne środowisko (osobny Python tylko dla tego projektu)
python3 -m venv venv               # Windows: python -m venv venv

# 3. Aktywacja środowiska – na początku linii pojawi się (venv)
source venv/bin/activate           # Windows (PowerShell): venv\Scripts\Activate.ps1
                                   # Windows (cmd):        venv\Scripts\activate.bat

# 4. Instalacja zależności (Django itd.)
pip install -r requirements.txt

# 5. Utworzenie tabel w bazie db.sqlite3
python manage.py migrate

# 6. Wypełnienie bazy danymi testowymi
python manage.py seed_db

# 7. Uruchomienie serwera deweloperskiego
python manage.py runserver
```

Strona działa pod adresem **http://127.0.0.1:8000/**. Serwer zatrzymuje się
skrótem **Ctrl+C**.

## Kolejne uruchomienia

```bash
cd application-development-frameworks-project
source venv/bin/activate           # Windows: venv\Scripts\activate
python manage.py runserver
```

Po pobraniu zmian od zespołu (`git pull`) warto dodatkowo wykonać:

```bash
pip install -r requirements.txt    # jeśli zmieniły się zależności
python manage.py migrate           # jeśli doszły nowe migracje
python manage.py seed_db           # odświeżenie danych testowych
```

## Dane testowe – `seed_db`

Plik `db.sqlite3` jest w `.gitignore` i **nie trafia do repozytorium**. Zamiast
przesyłać bazę, każdy członek zespołu generuje identyczne dane jedną komendą:

```bash
python manage.py seed_db           # tworzy lub aktualizuje dane testowe
python manage.py seed_db --reset   # najpierw usuwa wszystkie pojazdy, rezerwacje
                                   # i wpisy serwisowe, potem wstawia dane od nowa
```

Komendę można uruchamiać wielokrotnie – nie tworzy duplikatów, tylko przywraca
rekordy do stanu początkowego. Opcja `--reset` przydaje się, gdy w panelu
admina dodano ręcznie dodatkowe dane i chcesz wrócić do czystej floty
(konta użytkowników zostają).

### Co tworzy komenda

**Pojazdy (5):**

| Nr rej.    | Marka i model       | Rok  | Przebieg   | Status       |
|------------|---------------------|------|------------|--------------|
| SC 12345   | Toyota Corolla      | 2021 | 45 200 km  | Dostępny     |
| SC 23456   | Skoda Octavia       | 2020 | 78 900 km  | Dostępny     |
| SC 34567   | Volkswagen Golf     | 2019 | 102 300 km | Wypożyczony  |
| SC 45678   | Ford Focus          | 2018 | 131 750 km | W serwisie   |
| SC 56789   | Kia Ceed            | 2023 | 12 400 km  | Dostępny     |

**Rezerwacje (3):**

| Pojazd          | Konto       | Cel wyjazdu                         | Termin                    | Status      |
|-----------------|-------------|-------------------------------------|---------------------------|-------------|
| Toyota Corolla  | `pracownik` | Spotkanie z klientem w Katowicach   | 20–15 dni temu            | Zakończona  |
| Volkswagen Golf | `pracownik` | Delegacja do Warszawy               | od 2 dni temu do za 5 dni | Aktywna     |
| Kia Ceed        | `admin`     | Szkolenie w Krakowie                | za 7–10 dni               | Oczekująca  |

**Wpisy serwisowe (2):**

| Pojazd        | Kiedy          | Opis                                        | Koszt       |
|---------------|----------------|---------------------------------------------|-------------|
| Skoda Octavia | 45 dni temu    | Przegląd okresowy, wymiana oleju i filtrów  | 650,00 PLN  |
| Ford Focus    | wczoraj        | Wymiana sprzęgła i koła dwumasowego         | 3200,00 PLN |

Daty rezerwacji i serwisów są liczone **względem dnia uruchomienia komendy**,
dzięki czemu „aktywna” rezerwacja zawsze obejmuje dzisiejszy dzień,
a „oczekująca” jest w przyszłości. Każdy rekord przechodzi walidację modelu
(`full_clean()`), więc błędne dane (np. data zwrotu przed datą wypożyczenia)
zatrzymają komendę z komunikatem błędu.

## Role i konta testowe

| Rola           | Login       | Hasło          | Uprawnienia                                                     |
|----------------|-------------|----------------|-----------------------------------------------------------------|
| Administrator  | `admin`     | `admin123`     | superużytkownik: panel `/admin/`, rezerwacje wszystkich pracowników |
| Pracownik      | `pracownik` | `pracownik123` | zwykły użytkownik: tylko własne rezerwacje, bez panelu admina   |

Role rozróżniane są flagą `is_staff` użytkownika Django:

- `request.user.is_staff == True` – administrator,
- zalogowany użytkownik bez `is_staff` – pracownik,
- niezalogowany gość widzi stronę główną i listę pojazdów, ale nie rezerwacje.

> Hasła testowe służą wyłącznie do pracy lokalnej – nie używać ich na serwerze produkcyjnym.

### Logowanie i wylogowanie

Wykorzystany jest wbudowany system uwierzytelniania Django
(`django.contrib.auth.urls` podpięty pod `/accounts/`):

- logowanie: `/accounts/login/` (szablon `registration/login.html`),
- wylogowanie: przycisk „Wyloguj” w menu – od Django 5 wylogowanie działa tylko
  żądaniem **POST** (formularz z `{% csrf_token %}`), zwykły link nie zadziała,
- po zalogowaniu i wylogowaniu użytkownik trafia na stronę główną
  (`LOGIN_REDIRECT_URL = '/'`, `LOGOUT_REDIRECT_URL = '/'` w `config/settings.py`).

Widoki wymagające zalogowania chroni dekorator `@login_required`
(lub `LoginRequiredMixin` w widokach klasowych). Niezalogowany użytkownik
zostanie przekierowany na stronę logowania, a po zalogowaniu wróci na stronę,
którą chciał otworzyć.

## Funkcje i adresy stron

| Adres                | Widok                      | Dostęp            | Opis |
|----------------------|----------------------------|-------------------|------|
| `/`                  | `HomeView`                 | wszyscy           | strona główna z licznikami: wszystkie / dostępne / wypożyczone / w serwisie (kliknięcie licznika otwiera przefiltrowaną listę) |
| `/vehicles/`         | `vehicle_list`             | wszyscy           | lista pojazdów; wyszukiwanie po marce, modelu lub nr rejestracyjnym i filtr statusu (formularz `VehicleSearchForm`, metoda GET) |
| `/vehicles/<id>/`    | `vehicle_detail`           | wszyscy           | specyfikacja pojazdu, kolorowy status, historia rezerwacji i historia serwisowa |
| `/my-reservations/`  | `my_reservations`          | zalogowani        | pracownik: własne rezerwacje; administrator: rezerwacje wszystkich z kolumną „Pracownik”; filtr po celu wyjazdu / pojeździe i statusie (`ReservationFilterForm`) |
| `/accounts/login/`   | `LoginView` (Django)       | wszyscy           | formularz logowania |
| `/admin/`            | panel Django               | administrator     | dodawanie, edycja i usuwanie pojazdów, rezerwacji, serwisów i użytkowników |

Filtry działają przez parametry w adresie, np.
`/vehicles/?query=toyota&status=available` albo `/my-reservations/?status=active`,
więc wynik wyszukiwania można skopiować i wysłać jako link.

Menu górne dostosowuje się do użytkownika: gość widzi „Zaloguj”, pracownik
„Moje rezerwacje” i „Wyloguj”, a administrator dodatkowo „Panel admina”.

## Model danych

Modele znajdują się w `fleet/models.py`.

**`Vehicle` – pojazd**

| Pole                  | Typ                 | Opis |
|-----------------------|---------------------|------|
| `brand`, `model`      | tekst               | marka i model |
| `registration_number` | tekst, unikalny     | numer rejestracyjny |
| `production_year`     | liczba              | rok produkcji |
| `mileage`             | liczba ≥ 0          | przebieg w km |
| `status`              | wybór               | `available` (Dostępny), `rented` (Wypożyczony), `service` (W serwisie) |

**`Reservation` – rezerwacja** (`vehicle.reservations`, `user.reservations`)

| Pole                                | Typ                     | Opis |
|-------------------------------------|-------------------------|------|
| `vehicle`                           | klucz obcy → `Vehicle`  | rezerwowany pojazd |
| `user`                              | klucz obcy → `User`, opcjonalny | pracownik, do którego należy rezerwacja |
| `purpose`                           | tekst, opcjonalny       | cel wyjazdu |
| `customer_name`, `customer_email`   | tekst, e-mail           | dane osoby korzystającej z auta |
| `start_date`, `end_date`            | data                    | termin; walidacja: zwrot nie wcześniej niż wypożyczenie |
| `status`                            | wybór                   | `pending`, `active`, `completed`, `cancelled` |

**`ServiceLog` – wpis serwisowy** (`vehicle.service_logs`)

| Pole            | Typ                    | Opis |
|-----------------|------------------------|------|
| `vehicle`       | klucz obcy → `Vehicle` | serwisowany pojazd |
| `service_date`  | data                   | data serwisu |
| `description`   | tekst                  | opis wykonanych prac |
| `cost`          | kwota ≥ 0              | koszt w PLN |

Usunięcie pojazdu usuwa też jego rezerwacje i wpisy serwisowe. Usunięcie
użytkownika nie usuwa jego rezerwacji – pole `user` zostaje puste.

## Struktura projektu

```
application-development-frameworks-project/
├── config/                     # konfiguracja projektu Django
│   ├── settings.py             # ustawienia (aplikacje, baza, logowanie)
│   └── urls.py                 # główne adresy: /admin/, /accounts/, adresy aplikacji fleet
├── fleet/                      # aplikacja „flota”
│   ├── models.py               # Vehicle, Reservation, ServiceLog
│   ├── views.py                # HomeView, vehicle_list, vehicle_detail, my_reservations
│   ├── forms.py                # VehicleSearchForm, ReservationFilterForm
│   ├── urls.py                 # adresy aplikacji: /, /vehicles/, /my-reservations/
│   ├── admin.py                # konfiguracja panelu administratora
│   ├── migrations/             # migracje bazy danych
│   ├── management/commands/
│   │   └── seed_db.py          # komenda z danymi testowymi
│   ├── static/fleet/           # pliki statyczne (logo)
│   └── templates/
│       ├── base.html           # szablon bazowy: menu, komunikaty, stopka
│       ├── registration/login.html
│       └── fleet/              # home, vehicle_list, vehicle_detail, my_reservations
├── manage.py
├── requirements.txt
└── README.md
```

## Praca zespołowa z Gitem

Każde zadanie realizowane jest na osobnej gałęzi `feature/...`, a do `main`
trafia przez Pull Request na GitHubie.

| Gałąź                                  | Zakres |
|----------------------------------------|--------|
| `feature/models-and-admin`             | modele i panel administratora |
| `feature/base-ui-bootstrap`            | szablon bazowy, Bootstrap, logo |
| `feature/auth-and-seed`                | logowanie, role, komenda `seed_db` |
| `feature/vehicle-list-search`          | lista pojazdów i wyszukiwarka |
| `feature/vehicle-detail`               | szczegóły pojazdu, historia rezerwacji i serwisu |
| `feature/user-reservations-dashboard`  | „Moje rezerwacje”, strona główna z licznikami, menu |

Typowy przebieg pracy:

```bash
git checkout main
git pull origin main                       # najnowszy kod z GitHuba
git checkout -b feature/nazwa-zadania      # nowa gałąź na zadanie

# ... praca nad kodem ...

git status                                 # co się zmieniło
git add .
git commit -m "Krótki opis zmian"
git push -u origin feature/nazwa-zadania   # wysłanie gałęzi na GitHuba
```

Następnie na GitHubie: **Compare & pull request** → opis zmian → **Create pull request**.
Po zmergowaniu wszyscy robią `git pull origin main`.

Do repozytorium **nie dodajemy**: `db.sqlite3`, `venv/`, `__pycache__/`, `.env`
(są w `.gitignore`).

## Najczęstsze problemy

| Problem | Rozwiązanie |
|---------|-------------|
| `ModuleNotFoundError: No module named 'django'` | nie aktywowano środowiska – `source venv/bin/activate`, potem ewentualnie `pip install -r requirements.txt` |
| `pip` nie znajduje Django 6.1 | za stary Python – zainstaluj 3.12+ i utwórz `venv` od nowa |
| `no such table` / `no such column` | brakuje migracji – `python manage.py migrate` |
| `You have unapplied migration(s)` przy `runserver` | `python manage.py migrate` |
| Nie da się zalogować na `admin` / `pracownik` | konta jeszcze nie istnieją – `python manage.py seed_db` |
| Lista pojazdów jest pusta | `python manage.py seed_db` |
| `Error: That port is already in use` | serwer działa w innym oknie terminala – zamknij go albo uruchom na innym porcie: `python manage.py runserver 8001` |
| Wylogowanie zwraca błąd 405 | wylogowanie wymaga POST – użyj przycisku „Wyloguj” w menu |
| Zmiany w CSS / szablonie nie są widoczne | odśwież stronę bez cache: **Cmd+Shift+R** (macOS) / **Ctrl+F5** (Windows) |
| `CONFLICT` przy `git pull` | otwórz wskazany plik, zostaw właściwą wersję między `<<<<<<<` i `>>>>>>>`, potem `git add .` i `git commit` |
| Chcę zacząć z czystą bazą | usuń plik `db.sqlite3`, potem `python manage.py migrate` i `python manage.py seed_db` |
