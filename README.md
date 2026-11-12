# System Zarządzania Flotą

Projekt Django do zarządzania flotą pojazdów.

## Uruchomienie lokalne

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate          # utworzenie tabel w db.sqlite3
python manage.py seed_db          # dane testowe (konta + 5 samochodów)
python manage.py runserver
```

Plik `db.sqlite3` jest w `.gitignore` – każdy generuje identyczną bazę testową
komendą `seed_db`. Komendę można uruchamiać wielokrotnie (nie tworzy duplikatów,
przywraca dane do stanu początkowego).

## Konta testowe

| Rola           | Login       | Hasło          | Uprawnienia                         |
|----------------|-------------|----------------|-------------------------------------|
| Administrator  | `admin`     | `admin123`     | pełny dostęp, panel `/admin/`       |
| Pracownik      | `pracownik` | `pracownik123` | zwykły użytkownik, bez panelu admina |

## Logowanie

- logowanie: `/accounts/login/`
- wylogowanie: `/accounts/logout/` (tylko żądanie **POST**, np. formularz z `{% csrf_token %}`)
- po zalogowaniu i wylogowaniu użytkownik trafia na `/`

Widoki chronione dla zalogowanych: dekorator `@login_required` lub `LoginRequiredMixin`.
