# HiTalent — Сервис управления иерархической структурой подразделений

REST API сервис для управления организационной структурой компании (департаменты и сотрудники) — простой CRUD Web API, который придерживается принципов Clean Architecture, использует некоторые тактические паттерны DDD и следует подходу CQRS.
## 🛠️ Запуск проекта

Вы можете запускать проект любым удобным для вас способом: через Docker Compose, утилиту `just` или классический `make`.

### 1. Быстрый запуск через Docker Compose (Рекомендуемый)

Приложении автоматически поднимет базу данных, накатит миграции Alembic и запустит веб-сервер.

```bash
# Клонировать репозиторий
git clone https://github.com/your-username/hitalent.git
cd hitalent

# Запустить контейнеры
docker compose up -d --build

# Применить миграции
docker compose exec api alembic upgrade head
```


### 2. Локальный запуск (разработка)

Через `just`:

```bash
just infra
just dev
```

или через `make`:

```bash
make infra
make dev
```

---

## 🚀 Технологический стек

* **Язык:** Python 3.11+
* **Фреймворк:** FastAPI
* **База данных:** PostgreSQL
* **ORM:** SQLAlchemy 2.0 (Asyncio)
* **Миграции:** Alembic
* **Валидация данных:** Pydantic v2
* **Тестирование:** Pytest (Asyncio)
* **Контейнеризация:** Docker, Docker Compose

---

## 📂 Структура проекта

```text
src/
├── api/                  # Слой адаптеров инфраструктуры (FastAPI Роутеры, Схемы Pydantic)
├── application/          # Слой бизнес-сценариев (Use Cases, Команды, Хендлеры, DTO)
│   ├── department/       # Логика управления подразделениями (Commands/Queries)
│   ├── employee/         # Логика управления сотрудниками
│   └── common/           # Общие интерфейсы (UoW, Mediator base)
├── domain/               # Чистый домен (Сущности, Бизнес-исключения, Инварианты)
└── infrastructure/       # Детали реализации (PostgreSQL ORM модели, Репозитории, Мапперы)

```
