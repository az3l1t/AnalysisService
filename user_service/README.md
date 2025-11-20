# User Service

Микросервис управления пользователями для системы хранения медицинских анализов.

## 🎯 Назначение

User Service отвечает за:
- Управление профилями пользователей
- Управление ролями (PATIENT, DOCTOR, ADMIN)
- Связь пациент-врач
- Блокировка/восстановление доступа пользователей
- Интеграцию с Auth Service

## 🏗️ Архитектура

Сервис следует модульной архитектуре с явным разделением на слои:

```
user_service/
├── domain/              # Доменный слой
│   ├── models/         # Доменные модели (User, Role)
│   └── events/         # Доменные события
├── application/        # Слой приложения
│   ├── use_cases/     # Use cases (бизнес-логика)
│   └── services/      # Сервисы приложения
├── infrastructure/     # Инфраструктурный слой
│   ├── database/      # Настройки БД
│   ├── repositories/ # Репозитории
│   └── http_clients/  # HTTP клиенты для межсервисного взаимодействия
└── api/               # API слой
    ├── routes/        # REST endpoints
    ├── middleware/    # Middleware (auth, validation)
    └── schemas.py     # Pydantic схемы
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Создайте файл `.env`:

```env
USER_SERVICE_DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/user_db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
AUTH_SERVICE_URL=http://localhost:8000
```

### 3. Запуск базы данных

```bash
# Через Docker
docker run -d \
  --name user_db \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=user_db \
  -p 5433:5432 \
  postgres:15-alpine
```

### 4. Запуск сервиса

```bash
uvicorn user_service.main:app --reload --port 8001
```

Сервис будет доступен по адресу: http://localhost:8001

## 📚 API Endpoints

### Создание пользователя (Admin)

```http
POST /users
Authorization: Bearer <token>
Content-Type: application/json

{
  "auth_user_id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "middle_name": "Middle",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "roles": ["PATIENT"]
}
```

### Получение пользователя

```http
GET /users/{id}
Authorization: Bearer <token>
```

### Список пользователей (Admin)

```http
GET /users?page=1&page_size=100&role=PATIENT&is_blocked=false&search=john
Authorization: Bearer <token>
```

### Обновление пользователя

```http
PATCH /users/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "first_name": "Jane",
  "phone": "+9876543210"
}
```

### Изменение ролей (Admin)

```http
POST /users/{id}/roles
Authorization: Bearer <token>
Content-Type: application/json

{
  "roles": ["DOCTOR", "ADMIN"]
}
```

### Назначение врача пациенту

```http
POST /users/{patient_id}/assign-doctor
Authorization: Bearer <token>
Content-Type: application/json

{
  "doctor_id": 5
}
```

### Блокировка пользователя (Admin)

```http
POST /users/{id}/block
Authorization: Bearer <token>
Content-Type: application/json

{
  "reason": "Violation of terms"
}
```

### Восстановление доступа (Admin)

```http
POST /users/{id}/restore
Authorization: Bearer <token>
```

### Health Check

```http
GET /health
```

## 🔐 Авторизация

Все endpoints (кроме `/health` и `/`) требуют JWT токен в заголовке:

```
Authorization: Bearer <token>
```

Токен должен быть получен из Auth Service.

### Роли

- **PATIENT** - Пациент
- **DOCTOR** - Врач
- **ADMIN** - Администратор

## 🔗 Интеграция с Auth Service

### Входящие события

User Service подписывается на события от Auth Service:

- **AuthUserRegistered** - создание пользователя в User Service при регистрации в Auth Service

### Исходящие вызовы

User Service вызывает Auth Service при:

- Изменении ролей пользователя - обновление прав/claims
- Блокировке пользователя - отключение входа, инвалидация токенов
- Восстановлении доступа - включение входа

## 📊 Доменные события

User Service эмитирует следующие доменные события:

- **UserCreated** - пользователь создан
- **UserUpdated** - данные пользователя обновлены
- **UserRoleChanged** - роли пользователя изменены
- **DoctorAssignedToPatient** - врач назначен пациенту
- **UserBlocked** - пользователь заблокирован
- **UserAccessRestored** - доступ пользователя восстановлен

## 🧪 Тестирование

### Запуск тестов

```bash
# Все тесты
pytest tests/user_service/ -v

# С покрытием
pytest tests/user_service/ --cov=user_service --cov-report=html
```

### Структура тестов

- `test_user_repository.py` - unit тесты для репозиториев
- `test_integration.py` - integration тесты для API

## 📝 Миграции БД

Таблицы создаются автоматически при запуске приложения через `Base.metadata.create_all()`.

Для production рекомендуется использовать Alembic:

```bash
# Создание миграции
alembic revision --autogenerate -m "Initial migration"

# Применение миграций
alembic upgrade head
```

## 🗄️ Структура базы данных

### Таблица `users`

- `id` - Primary key
- `auth_user_id` - ID пользователя в Auth Service (unique)
- `first_name`, `last_name`, `middle_name` - ФИО
- `email` - Email (unique)
- `phone` - Телефон
- `is_blocked` - Флаг блокировки
- `assigned_doctor_id` - ID назначенного врача
- Аудиторные поля: `created_at`, `updated_at`, `blocked_at`, `blocked_by`

### Таблица `roles`

- `id` - Primary key
- `name` - Название роли (PATIENT, DOCTOR, ADMIN)
- `description` - Описание

### Таблица `user_roles`

- `user_id` - Foreign key to users
- `role_id` - Foreign key to roles
- Many-to-many связь

## 🔧 Переменные окружения

- `USER_SERVICE_DATABASE_URL` - URL подключения к PostgreSQL
- `SECRET_KEY` - Секретный ключ для JWT (должен совпадать с Auth Service)
- `ALGORITHM` - Алгоритм JWT (по умолчанию HS256)
- `AUTH_SERVICE_URL` - URL Auth Service для интеграции

## 📖 Документация API

После запуска сервиса документация доступна по адресам:

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## 🚀 Деплой

Сервис может быть развернут аналогично Auth Service:

- Docker контейнер
- Kubernetes
- Cloud Run / Serverless

См. документацию Auth Service для примеров CI/CD конфигурации.

