# Polish Kettlebell Championship 2025

A full-stack web platform for organizing, scoring and broadcasting the **2025 Polish Kettlebell Championship** (Mistrzostwa Polski Kettlebell 2025). The system manages athletes, sports clubs, competition categories and individual disciplines, computes rankings in real time and exposes results through a public live-results website.

## Overview

The project consists of three main parts:

- **Backend** — a Django + Django REST Framework application that stores competition data in PostgreSQL, provides an administrative panel for judges and organizers, and serves a REST API for the frontend.
- **Live-results frontend** — a React 19 + TypeScript + Vite single-page application (using Ant Design) that displays start lists, live scores and category rankings for spectators.
- **Static pages / calculator** — auxiliary static HTML pages (landing page, contact, kettlebell weight-class calculator) served alongside the main app.

## Features

- Registration and management of players, sports clubs and competition categories.
- Support for multiple disciplines: **Snatch**, **See-Saw Press**, **TGU (Turkish Get-Up)**, **Pistol Squat**, **Squat**, **Pull-Up**.
- Configurable per-category rules (e.g. maximum number of counted disciplines contributing to the overall score).
- Automatic scoring, tie-break resolution and computation of overall category placement.
- Import / export of participants via CSV (using `django-import-export`).
- Public REST API for categories, players and clubs.
- Live-results UI with start lists per category, real-time updates and mobile-friendly layout.
- Custom admin theme (`django-jazzmin`) and scheduled database backups (`django-dbbackup`).

## Tech stack

**Backend**
- Python 3.12+
- Django 5.2
- Django REST Framework 3.16
- PostgreSQL (via `psycopg2`)
- `django-import-export`, `django-cors-headers`, `django-jazzmin`, `django-dbbackup`
- `gunicorn` for production
- `ruff` + `mypy` + `pre-commit` for code quality

**Frontend (live-results)**
- React 19 + TypeScript 5.7
- Vite 6
- Ant Design 5 + `@ant-design/icons`
- TanStack Query 5 (server-state management)
- React Router 7
- Axios, Day.js

## Repository structure

```
polish_kettlebell_championship_2025/
├── backend/
│   └── mp_kb_2025/              # Django project
│       ├── manage.py
│       ├── pyproject.toml       # ruff / mypy configuration
│       ├── requirements.txt
│       ├── kb_live/             # main Django app
│       │   ├── models/          # Player, Category, Club, discipline results…
│       │   ├── services/        # scoring & ranking business logic
│       │   ├── serializers.py
│       │   ├── views.py
│       │   ├── urls.py          # REST API routes
│       │   ├── admin.py
│       │   ├── resources.py     # import/export definitions
│       │   ├── management/commands/
│       │   └── migrations/
│       └── mp_kb_2025/settings/ # base / dev / prod settings
├── frontend/
│   ├── live-results/            # React + Vite SPA
│   │   ├── src/
│   │   │   ├── pages/           # HomePage, CategoryPage, LivePage, StartLists…
│   │   │   ├── components/
│   │   │   ├── services/api.ts
│   │   │   └── theme/
│   │   └── vite.config.ts
│   └── mpkb/build/              # legacy prebuilt static assets
├── kalkulator/                  # standalone weight-class calculator (HTML/JS)
├── css/                         # shared styles for static pages
├── index_temp.html              # landing page prototype
└── README.md
```

## Getting started

### Prerequisites

- Python 3.12 or newer
- Node.js 20+ and npm
- PostgreSQL 14+
- (Recommended) `virtualenv` or the built-in `venv` module

### Backend setup

```bash
# From the repository root
python3 -m venv .venv
source .venv/bin/activate

cd backend/mp_kb_2025
pip install -r requirements.txt
```

Create an `.env` file in `backend/mp_kb_2025/` (next to `manage.py`'s parent) with at least:

```env
DEBUG=True
SECRET_KEY=change-me
ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=mpkb_2025_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

Then run migrations, create an admin user and start the development server:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/` and the Django admin panel at `http://127.0.0.1:8000/admin/`.

### Frontend setup (live results)

```bash
cd frontend/live-results
npm install
npm run dev
```

The Vite dev server will start (by default on `http://localhost:5173/`) and consume the Django REST API. Configure the API base URL in `frontend/live-results/src/services/api.ts` if needed.

To create a production build:

```bash
npm run build
npm run preview
```

## REST API

The API is exposed by `kb_live` under the project's URL configuration. Main endpoints (registered via DRF's `DefaultRouter`):

- `GET /categories/` — list of competition categories with results
- `GET /players/` — participants
- `GET /clubs/` — sports clubs

Individual detail routes (`/categories/{id}/`, etc.) return nested discipline scores and overall placements.

## Development

Backend code quality tools are configured in [backend/mp_kb_2025/pyproject.toml](backend/mp_kb_2025/pyproject.toml):

```bash
# From backend/mp_kb_2025/
ruff check .
ruff format .
mypy .
pre-commit run --all-files
```

Frontend linting:

```bash
cd frontend/live-results
npm run lint
```

## Deployment

The backend is designed to run behind `gunicorn` with production settings in `mp_kb_2025/settings/prod.py`. Configure environment variables (`DEBUG=False`, real `SECRET_KEY`, `ALLOWED_HOSTS`, database credentials) and run:

```bash
python manage.py collectstatic --noinput
gunicorn mp_kb_2025.wsgi:application
```

The built frontend (`npm run build` output in `frontend/live-results/dist/`) can be served by any static file host or reverse-proxied together with the API.

## License

All rights reserved © 2025. Intended for use by the organizers of the Polish Kettlebell Championship 2025.

