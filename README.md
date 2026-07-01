# Phone Finder Pro

Telegram bot and REST API for smartphone recommendations, catalog management, and marketplace analytics.

**Repository:** [github.com/miraziz-Developer/phone-finder-pro](https://github.com/miraziz-Developer/phone-finder-pro)

[![CI](https://github.com/miraziz-Developer/phone-finder-pro/actions/workflows/ci.yml/badge.svg)](https://github.com/miraziz-Developer/phone-finder-pro/actions/workflows/ci.yml)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.13 |
| Bot | Aiogram 3 (FSM, Redis storage) |
| API | FastAPI + JWT |
| Database | PostgreSQL 16, SQLAlchemy 2.0 async, Alembic |
| Cache / sessions | Redis 7 |
| Testing | pytest, pytest-asyncio |
| Tooling | Poetry, Ruff, Docker |

## Features

| Area | Capabilities |
|------|--------------|
| User bot | 11-step recommendation flow, search, filters, compare, favorites, history |
| Admin bot | CRUD, import CSV/Excel/JSON, export, dashboard stats |
| Engine | Config-driven weighted scoring (budget, performance, camera, battery, …) |
| API | JWT-protected admin endpoints, Swagger at `/docs` |
| Data | 15 seeded phones, images, price history, discounts |

## Architecture

Clean Architecture with explicit layers:

```
app/
├── core/           # config, logging, database, security
├── domain/         # entities, value objects, scoring engine, repository ports
├── application/    # commands, queries, handlers, services, validators
├── infrastructure/ # PostgreSQL models/repos, Redis client
├── presentation/   # Telegram routers, FastAPI app
└── shared/         # enums, constants, exceptions
```

Dependency rule: `presentation → application → domain ← infrastructure`.

## Quick Start (Docker)

```bash
git clone https://github.com/miraziz-Developer/phone-finder-pro.git
cd phone-finder-pro
cp .env.example .env
```

Edit `.env`:

```env
BOT_TOKEN=<from @BotFather>
ADMIN_IDS=<your Telegram user ID from @userinfobot>
```

```bash
docker-compose up --build
```

| Service | URL / role |
|---------|------------|
| Bot | Telegram polling |
| API | http://localhost:8000/docs |
| PostgreSQL | port 5432 |
| Redis | port 6379 |
| migrate | Alembic + seed (15 phones) |

## Local Development

```bash
poetry install
docker-compose up postgres redis -d   # or local Postgres + Redis
cp .env.example .env
# set POSTGRES_HOST=localhost, REDIS_HOST=localhost

poetry run alembic upgrade head
poetry run python scripts/seed.py
poetry run python -m app.main       # bot
poetry run python -m app.api_main   # API
```

Use `make help` for common commands.

## For Reviewers (5-minute demo)

1. **Clone & run** — `docker-compose up --build` (set `BOT_TOKEN` + `ADMIN_IDS` in `.env`).
2. **User flow** — `/start` → `/recommend` → complete wizard → see top 5 with scores and photos.
3. **Search** — `/filter brand:samsung price:400-900` or `/compare`.
4. **Admin** — `/stats`, `/phones`, `/export_json` (requires your ID in `ADMIN_IDS`).
5. **API** — open `/docs`, authenticate with `admin` / value from `API_ADMIN_PASSWORD`, call `GET /api/v1/stats`.
6. **Tests** — `make test` (29 tests: engine, validators, import/export, compare, API).

### Seed catalog

Pre-loaded data: **7 brands**, **3 categories**, **15 phones** with specs, images, and price history.

```bash
poetry run python scripts/seed.py          # first run only
poetry run python scripts/seed.py --reset  # wipe catalog & reseed
```

## Bot Commands

**User:** `/start` `/recommend` `/search` `/filter` `/compare` `/favorites` `/popular` `/newest` `/history`

**Admin** (Telegram ID in `ADMIN_IDS`): `/admin` `/stats` `/phones` `/add_phone` `/delete_phone` `/update_price` `/import_json` `/import_csv` `/import_excel` `/export_json` `/export_csv`

## REST API

```bash
curl -X POST http://localhost:8000/api/v1/auth/token \
  -d "username=admin&password=admin_secret_change_me"

curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/phones
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/stats
```

## Recommendation Weights

Configured via `.env` (defaults sum to 1.0):

| Criterion | Weight |
|-----------|--------|
| Budget | 30% |
| Performance | 20% |
| Camera | 15% |
| Battery | 10% |
| Display | 10% |
| Storage | 5% |
| Brand | 5% |
| Features | 5% |

## Configuration

All settings are environment-driven — see [`.env.example`](.env.example).

**Never commit `.env`** — it contains secrets (`BOT_TOKEN`, `JWT_SECRET_KEY`, DB passwords).

## License

MIT — see [LICENSE](LICENSE).
