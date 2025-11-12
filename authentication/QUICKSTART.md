# Быстрый старт

## Запуск через Docker Compose (рекомендуется)

### Современный синтаксис Docker Compose

Используйте `docker compose` (без дефиса) для новых версий Docker:

```bash
# Запуск всех сервисов
docker compose up -d

# Просмотр логов
docker compose logs -f

# Остановка сервисов
docker compose down

# Пересборка и запуск
docker compose up -d --build
```

**Примечание**: Если вы получаете ошибку "project name must not be empty", убедитесь, что в `docker-compose.yml` указано имя проекта (это уже сделано в проекте).

### Старый синтаксис (если установлен docker-compose отдельно)

```bash
docker-compose up -d
```

## Локальный запуск без Docker

### 1. Запуск PostgreSQL

#### Вариант A: Через Docker (только БД)

```bash
docker run -d \
  --name auth_db \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=auth_db \
  -p 5432:5432 \
  postgres:15-alpine
```

#### Вариант B: Локальная установка PostgreSQL

Установите PostgreSQL локально и создайте базу данных:

```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Создание базы данных
createdb auth_db
```

### 2. Настройка переменных окружения

Создайте файл `.env`:

```bash
cp env.example .env
```

Отредактируйте `.env`:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/auth_db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Запуск приложения

```bash
# Активируйте виртуальное окружение
source venv/bin/activate

# Запустите приложение
uvicorn app.main:app --reload
```

Приложение будет доступно на http://127.0.0.1:8000

## Проверка работы

### Health check

```bash
curl http://localhost:8000/health
```

### Документация API

Откройте в браузере:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Устранение проблем

### Ошибка: "Connection refused"

**Проблема**: PostgreSQL не запущен или недоступен.

**Решение**:
1. Проверьте, запущен ли PostgreSQL:
   ```bash
   # Docker
   docker ps | grep postgres
   
   # Локально (macOS)
   brew services list | grep postgresql
   ```

2. Запустите PostgreSQL:
   ```bash
   # Docker
   docker compose up -d db
   
   # Локально
   brew services start postgresql@15
   ```

3. Проверьте подключение:
   ```bash
   psql -h localhost -U user -d auth_db
   ```

### Ошибка: "docker-compose: command not found"

**Проблема**: Старая версия Docker Compose не установлена.

**Решение**: Используйте новый синтаксис `docker compose` (без дефиса).

### Ошибка: "project name must not be empty"

**Проблема**: Команда указана неправильно или сервис не существует.

**Решение**: 
- Используйте `docker compose up -d` для запуска всех сервисов
- Или `docker compose build auth-service` для сборки конкретного сервиса
- Проверьте, что вы находитесь в директории с `docker-compose.yml`

### Приложение запускается, но таблицы не созданы

**Решение**: Таблицы создаются автоматически при первом запуске. Если они не созданы:

1. Проверьте логи приложения
2. Убедитесь, что БД доступна
3. Создайте таблицы вручную через Alembic:
   ```bash
   alembic upgrade head
   ```

## Полезные команды

### Docker Compose

```bash
# Просмотр статуса
docker compose ps

# Просмотр логов
docker compose logs -f auth-service
docker compose logs -f db

# Остановка
docker compose stop

# Удаление контейнеров и volumes
docker compose down -v

# Пересборка
docker compose build --no-cache
```

### Работа с БД

```bash
# Подключение к БД через Docker
docker exec -it auth_db psql -U user -d auth_db

# Создание миграций (если используете Alembic)
alembic revision --autogenerate -m "Initial migration"

# Применение миграций
alembic upgrade head
```

