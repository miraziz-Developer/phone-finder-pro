# Phone Finder Pro — Mini Marketplace Backend

Production-ready Telegram bot + REST API for smartphone recommendations, catalog management, and marketplace analytics.

[![CI](https://github.com/your-org/phone-marketplace-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/phone-marketplace-bot/actions/workflows/ci.yml)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

A full **mini marketplace backend** delivered via Telegram and REST API:

| Module | Features |
|--------|----------|
| 👤 **User Panel** | Recommendations, search, compare, favorites, history |
| 🛠 **Admin Panel** | CRUD, import CSV/Excel/JSON, export, analytics — all in Telegram |
| 🤖 **Recommendation Engine** | Config-driven weighted scoring (not random, not OpenAI) |
| ⚖️ **Compare** | Side-by-side with category winners |
| 📂 **Import/Export** | CSV, Excel, JSON with validation & duplicate detection |
| 💵 **Pricing** | USD only (`$199`, `$799`, `$999`) |
| 📷 **Images** | Multiple image URLs, auto-display primary image |
| 💲 **Price History** | Track every price change |
| 🏷 **Discounts** | Original price + discount percent |
| 🐳 **Docker** | Bot + API + Postgres + Redis |
| 📚 **Swagger API** | FastAPI admin API with JWT auth |

## Architecture

```
app/
├── core/              # Config, logging, DB, security
├── domain/            # Entities, scoring engine, repository ports
├── application/       # CQRS handlers, import/export, analytics, compare
├── infrastructure/    # PostgreSQL, Redis, repositories
├── presentation/
│   ├── bot/           # Telegram UX (user + admin panels)
│   └── api/           # FastAPI admin REST API
└── shared/            # Enums, constants, exceptions
```

## Recommendation Engine

Config-driven weights (via `.env`):

| Criterion | Default Weight |
|-----------|---------------|
| Budget | 30% |
| Performance | 20% |
| Camera | 15% |
| Battery | 10% |
| Display | 10% |
| Storage | 5% |
| Brand | 5% |
| Features | 5% |

Returns **Top 5** with match score (e.g. `96%`) and explanation.

## Quick Start

```bash
cp .env.example .env
# Set BOT_TOKEN and ADMIN_IDS

docker compose up --build
```

Services started:
- **bot** — Telegram bot (polling)
- **api** — FastAPI on `http://localhost:8000` (Swagger at `/docs`)
- **postgres** — PostgreSQL 16
- **redis** — Redis 7
- **migrate** — Alembic + seed data

## Admin Panel (Telegram)

| Command | Action |
|---------|--------|
| `/admin` | Full admin menu |
| `/stats` | Dashboard analytics |
| `/phones` | List catalog |
| `/add_phone` | Add phone wizard |
| `/delete_phone <id>` | Soft-delete |
| `/update_price` | Update USD price |
| `/add_image` | Add image URL |
| `/import_json` | Import JSON file |
| `/import_csv` | Import CSV file |
| `/import_excel` | Import Excel file |
| `/export_json` | Export JSON |
| `/export_csv` | Export CSV |

## User Commands

| Command | Action |
|---------|--------|
| `/start` | Main menu |
| `/recommend` | 11-step recommendation flow |
| `/search` | Text search |
| `/filter` | Advanced filters (`brand:samsung price:300-600`) |
| `/compare` | Compare 2 phones |
| `/favorites` | Saved phones |
| `/popular` | Most recommended |
| `/newest` | New arrivals |
| `/history` | Past recommendations |

## REST API

```bash
# Get JWT token
curl -X POST http://localhost:8000/api/v1/auth/token \
  -d "username=admin&password=admin_secret_change_me"

# List phones
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/phones

# Dashboard stats
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/stats
```

Swagger UI: `http://localhost:8000/docs`

## Phone Data Fields

Every phone supports: Model, Brand, Price (USD), Processor, GPU, RAM, Storage, Battery, Charging, Wireless Charging, Display, Refresh Rate, Resolution, Camera, Front Camera, OS Version, Release Date, Waterproof, 5G, NFC, eSIM, Fingerprint, Weight, Dimensions, SIM, Bluetooth, WiFi, USB, Stereo Speakers, Colors, Images, Description, Advantages, Disadvantages.

## Configuration

All settings via environment variables — see [`.env.example`](.env.example).

Key groups: Telegram, PostgreSQL, Redis, JWT, scoring weights, pagination, import limits, budget range.

## Development

```bash
poetry install
docker compose up postgres redis -d
poetry run alembic upgrade head
poetry run python scripts/seed.py
poetry run python -m app.main      # Bot
poetry run python -m app.api_main  # API
poetry run pytest
```

## License

MIT — see [LICENSE](LICENSE).
