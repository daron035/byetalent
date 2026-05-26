.PHONY: help install lint test dev infra

.DEFAULT_GOAL := help

help: ## Показать это справочное сообщение
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Установить пакет и все зависимости через uv
	uv sync --all-extras --all-groups

lint: ## Запустить проверки pre-commit
	uv run pre-commit run --all-files

test: ## Запустить тесты (можно передать аргументы, например: make test ARGS="-v")
	uv run pytest $(ARGS)

dev: ## Запустить приложение в режиме разработки (watcher)
	uv run python watcher.py

infra: ## Поднять локальную инфраструктуру (PostgreSQL) в Docker
	docker compose up -d postgres
