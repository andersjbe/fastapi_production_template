default:
  just --list

run *args:
  uv run uvicorn src.main:app --reload {{args}}

mm *args:
  uv run alembic revision --autogenerate -m "{{args}}"

migrate:
  uv run alembic upgrade head

downgrade *args:
  uv run alembic downgrade {{args}}

ruff *args:
  uv run ruff check {{args}} src

lint:
  uv run ruff format src
  just ruff --fix

# docker
up:
  docker-compose up -d

kill *args:
  docker-compose kill {{args}}

build:
  docker-compose build

ps:
  docker-compose ps