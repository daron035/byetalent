package_dir := "src"


# Show help message
help:
  just -l

# Install package with dependencies
install:
  uv sync --all-extras --all-groups

# Run pre-commit
lint:
	just _py pre-commit run --all-files

# Run tests
test *args:
  just _py pytest {{args}}

# Run app
dev:
  just _py python watcher.py

infra:
  docker compose up -d postgres

# Alembic migrations
alembic command message="":
    #!/usr/bin/env bash
    set -euo pipefail

    MIGRATIONS_DIR="src/infrastructure/persistence/postgres/migrations"

    case "{{command}}" in
      "init")
        if [ -d "$MIGRATIONS_DIR" ]; then
          echo
          echo -e "\033[32mDirectory already exists, skipping init.\033[0m"
        else
          echo
          echo -e "\033[33mInitializing Alembic (async template)...\033[0m"
          echo -e "\033[1malembic init --template async '$MIGRATIONS_DIR'\033[0m"
          echo
          alembic init --template async "$MIGRATIONS_DIR"
          echo
          echo -e "\033[33mCreating initial revision (UUID generation)...\033[0m"
          echo -e "\033[1malembic revision -m 'UUID generation.'\033[0m"
          echo
          alembic revision -m "UUID generation."
        fi
        ;;

      "mm")
        if [ -z "{{message}}" ]; then
          echo
          echo -e "\033[31mError: migration message cannot be empty.\033[0m"
          exit 1
        fi
        echo
        echo -e "\033[33mCreating new migration: '{{message}}'\033[0m"
        echo -e "\033[1malembic revision --autogenerate -m '{{message}}'\033[0m"
        echo
        alembic revision --autogenerate -m "{{message}}"
        ;;

      "um")
        echo
        echo -e "\033[33mUpgrading to head...\033[0m"
        echo -e "\033[1malembic upgrade head\033[0m"
        echo
        alembic upgrade head
        ;;

      "dm")
        echo
        echo -e "\033[33mDowngrading one step...\033[0m"
        echo -e "\033[1malembic downgrade -1\033[0m"
        echo
        alembic downgrade -1
        ;;

      "history")
        echo
        echo -e "\033[33mShowing migration history...\033[0m"
        echo -e "\033[1malembic history --verbose\033[0m"
        echo
        alembic history --verbose
        ;;

      "current")
        echo
        echo -e "\033[33mShowing current revision in the database...\033[0m"
        echo -e "\033[1malembic current\033[0m"
        echo
        alembic current
        ;;

      *)
        echo
        echo -e "\033[31mUnknown command:\033[0m {{command}}"
        echo -e "\033[33mAvailable: init, mm (make migration), um (upgrade), dm (downgrade), history, current\033[0m"
        exit 1
        ;;
    esac

_py *args:
  uv run {{args}}
