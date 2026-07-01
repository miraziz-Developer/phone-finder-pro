.PHONY: help install test lint format migrate seed seed-reset bot api up down

help:
	@echo "Targets:"
	@echo "  install     - poetry install"
	@echo "  test        - run pytest"
	@echo "  lint        - ruff check"
	@echo "  format      - ruff format"
	@echo "  migrate     - alembic upgrade head"
	@echo "  seed        - seed catalog (skips if data exists)"
	@echo "  seed-reset  - clear catalog and reseed"
	@echo "  bot         - run Telegram bot"
	@echo "  api         - run FastAPI server"
	@echo "  up          - docker-compose up --build"
	@echo "  down        - docker-compose down"

install:
	poetry install

test:
	poetry run pytest tests/ -v

lint:
	poetry run ruff check app tests scripts

format:
	poetry run ruff format app tests scripts

migrate:
	poetry run alembic upgrade head

seed:
	poetry run python scripts/seed.py

seed-reset:
	poetry run python scripts/seed.py --reset

bot:
	poetry run python -m app.main

api:
	poetry run python -m app.api_main

up:
	docker-compose up --build

down:
	docker-compose down
