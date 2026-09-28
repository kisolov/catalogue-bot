.PHONY: install test lint format up down logs pgadmin

install:
	uv venv --python 3.12 .venv
	uv pip install --python .venv/bin/python -e ".[dev]"

test:
	.venv/bin/pytest -q

lint:
	.venv/bin/flake8 src/
	.venv/bin/black --check src/

format:
	.venv/bin/black src/ tests/

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f backend

pgadmin:
	docker compose --profile tools up -d pgadmin
