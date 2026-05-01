# Library Management System

A production-grade Django-based Library Management System with modern UI/UX.

## Features

- **User Management**: Role-based access (Admin, Librarian, Staff, Member)
- **Book Catalog**: Full CRUD, search, filtering, ISBN import via Google Books API
- **Member Management**: Patron profiles, categories with configurable privileges
- **Circulation**: Issue, return, renew books with automatic availability tracking
- **Holds/Reservations**: Queue management, notifications, freeze holds
- **Fine System**: Automatic calculation, payment tracking, waiver system
- **Notifications**: Email alerts for due dates, overdue, hold availability
- **Reports**: Circulation stats, popular books, financial reports, CSV export
- **Patron Portal**: Self-service dashboard, loans, holds, fines management
- **Purchase Suggestions**: Patrons can suggest books for acquisition
- **Audit Logging**: Track important actions

## Tech Stack

- **Backend**: Django 5.x, SQLite (dev)
- **Frontend**: Django Templates, Tailwind CSS, HTMX, Alpine.js
- **Forms**: Crispy Forms + Tailwind
- **Tables**: django-tables2, django-filter
- **Background Tasks**: Celery + Redis (optional)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Seed Sample Data

```bash
python manage.py seed_data
```

### 5. Start Development Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

## Login Credentials (After Seeding)

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Librarian | librarian | lib123 |
| Member | member1 | member123 |
| Member | member2 | member123 |

## Project Structure

```
library/
├── config/                    # Django settings
│   └── settings/
│       ├── base.py
│       ├── development.py
│       └── production.py
├── apps/
│   ├── users/                 # Custom user model, authentication
│   ├── catalog/               # Books, authors, genres, search
│   ├── members/               # Member profiles, patron categories
│   ├── circulation/           # Issue, return, renew, holds
│   ├── fines/                 # Fine calculation, payments
│   ├── notifications/         # Email/SMS notifications
│   ├── reports/               # Analytics, charts, exports
│   └── acquisitions/          # Purchase suggestions
├── services/                  # Business logic layer
│   └── search_service.py      # Google Books API integration
├── tasks/                     # Celery background tasks
├── templates/                 # HTML templates
├── static/                    # CSS, JS, images
└── media/                     # Uploaded files
```

## URL Structure

### Public
- `/` - Home / Book catalog
- `/book/<slug>/` - Book detail
- `/authors/` - Author listing
- `/genres/` - Genre browsing

### Authentication
- `/accounts/login/` - Login
- `/accounts/logout/` - Logout
- `/accounts/register/` - Register

### Patron Portal
- `/members/dashboard/` - Patron dashboard
- `/circulation/my-holds/` - My holds
- `/fines/my-fines/` - My fines

### Staff (Protected)
- `/reports/dashboard/` - Staff dashboard
- `/circulation/issue/` - Issue book
- `/circulation/return/` - Return book
- `/circulation/active-loans/` - Active loans
- `/circulation/overdue/` - Overdue books
- `/members/` - Member management
- `/catalog/book/add/` - Add book
- `/catalog/isbn-import/` - ISBN import
- `/fines/` - Fine management
- `/reports/` - Reports & analytics
- `/acquisitions/` - Purchase suggestions

## Management Commands

```bash
python manage.py seed_data          # Populate with sample data
python manage.py createsuperuser    # Create admin user
```

## Configuration

### Environment Variables (.env)

```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
GOOGLE_BOOKS_API_KEY=your-api-key
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Email Setup (Production)

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## API (Future)

The project includes Django REST Framework for future API development:

```python
# Example: GET /api/books/
# Example: GET /api/books/?search=harry+potter
# Example: POST /api/circulation/issue/
```

## Production Deployment

1. Set `DEBUG=False`
2. Configure `ALLOWED_HOSTS`
3. Use PostgreSQL instead of SQLite
4. Set up Gunicorn + Nginx
5. Configure static files with WhiteNoise or S3
6. Set up Celery + Redis for background tasks
7. Enable HTTPS with Let's Encrypt

## License

MIT License
