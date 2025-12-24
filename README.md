# NexCell CRM (Beginner Friendly)

This is a small multi-tenant CRM built with:

- Django (HTML pages)
- Django REST Framework (API)
- SimpleJWT (JWT login for API)
- drf-spectacular (OpenAPI schema + Swagger UI)
- django-filter (optional filtering)
- SQLite (local database)

It is written to be easy to read and run by beginners.

---

## 1) Setup (Windows / macOS / Linux)

Open a terminal in the folder **that contains** `manage.py`.

```bash
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
python manage.py verify_plugins
python manage.py runserver
```

Open:

- Home: `http://127.0.0.1:8000/`
- Swagger: `http://127.0.0.1:8000/api/docs/`
- Schema: `http://127.0.0.1:8000/api/schema/`

---

## 2) Demo users (created by `seed_demo`)

Tenant 1 (Demo Organisation):

- `admin` / `admin123` (admin)
- `manager` / `manager123` (manager)
- `agent` / `agent123` (agent)
- `doctor` / `doctor123` (practitioner)

Tenant 2 (Other Organisation):

- `otheradmin` / `other123` (admin)

---

## 3) HTML pages

- Dashboard: `/dashboard/`

- Contacts: `/contacts/`
- Deals: `/deals/`
- Patients: `/patients/`
- Appointments: `/appointments/`
- Properties: `/properties/`
- Viewings: `/viewings/`

All forms work **with or without HTMX**:

- If HTMX loads, forms add new rows without a full page refresh.
- If HTMX does not load, forms still submit normally.

---

## 4) API endpoints

### Using Swagger "Authorize" (JWT)

1. Open Swagger UI: `/api/docs/`
2. Call `POST /api/auth/` with:
   - username: `admin`
   - password: `admin123`
3. Copy the `access` token from the response.
4. Click the **Authorize** button in Swagger UI and paste the token.

Swagger will then send requests with:

`Authorization: Bearer <YOUR_TOKEN>`

JWT auth:

- `POST /api/auth/` (get access + refresh token)
- `POST /api/auth/refresh/`
- `POST /api/auth/verify/`

Main resources:

- `/api/contacts/`
- `/api/deals/`
- `/api/activities/`
- `/api/patients/`
- `/api/appointments/`
- `/api/properties/`
- `/api/viewings/`

---

## 5) Role-based access (simple rules)

- Contacts + Deals + Properties + Viewings: **admin, manager, agent** can create/update.
- Patients + Appointments: **admin, manager, practitioner** can create/update.
- Everyone else gets read-only access.

---

## 6) Email

Appointment creation sends an email using Django's **in-memory** email backend
(`mail.outbox` in tests). To print emails to the console instead, change this
in `config/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

---

## Troubleshooting

### "no such table: accounts_user"

You forgot migrations. Run:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Redirect to `/accounts/profile/`

This project sets `LOGIN_REDIRECT_URL = '/'` so you should not see that.
If you do, make sure you are running the code from this folder (the one with `manage.py`).
