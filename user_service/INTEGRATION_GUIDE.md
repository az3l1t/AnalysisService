# Руководство по интеграции User Service с Auth Service

## Обзор

User Service интегрируется с Auth Service для:
- Аутентификации пользователей через JWT токены
- Синхронизации данных о пользователях
- Управления ролями и правами доступа

## Архитектура интеграции

### 1. Аутентификация

User Service использует JWT токены, выданные Auth Service:

1. Пользователь получает токен из Auth Service через `/token`
2. Токен содержит:
   - `sub` - username
   - `user_id` - ID пользователя в Auth Service
   - `email` - email пользователя
   - `exp` - время истечения
3. User Service проверяет токен и получает пользователя по `user_id`

### 2. Синхронизация данных

#### Создание пользователя

Когда пользователь регистрируется в Auth Service:
- Auth Service создает запись в своей БД
- User Service должен создать соответствующую запись

**Варианты реализации:**

**Вариант A: HTTP вызов (синхронный)**
```python
# В Auth Service после регистрации
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = auth.create_user(db=db, user=user)
    
    # Вызов User Service для создания профиля
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{USER_SERVICE_URL}/users",
            json={
                "auth_user_id": db_user.id,
                "email": db_user.email,
                "first_name": "",
                "last_name": "",
                "roles": ["PATIENT"]
            },
            headers={"Authorization": f"Bearer {internal_service_token}"}
        )
    
    return db_user
```

**Вариант B: События через Message Queue (асинхронный)**
```python
# В Auth Service после регистрации
event_bus.publish(AuthUserRegistered(
    user_id=db_user.id,
    username=db_user.username,
    email=db_user.email,
    created_at=datetime.utcnow()
))

# В User Service
@event_handler(AuthUserRegistered)
async def handle_auth_user_registered(event: AuthUserRegistered):
    # Создать пользователя в User Service
    ...
```

### 3. Управление ролями

Когда роли пользователя изменяются в User Service:
- User Service обновляет роли в своей БД
- User Service вызывает Auth Service для обновления claims в токене

```python
# В User Service
await auth_client.update_user_roles(
    auth_user_id=user.auth_user_id,
    roles=["PATIENT", "DOCTOR"]
)
```

### 4. Блокировка пользователя

Когда пользователь блокируется в User Service:
- User Service помечает пользователя как заблокированного
- User Service вызывает Auth Service для отключения входа

```python
# В User Service
await auth_client.block_user(
    auth_user_id=user.auth_user_id,
    reason="Violation of terms"
)
```

## Настройка

### Переменные окружения

**Auth Service:**
```env
SECRET_KEY=your-secret-key
ALGORITHM=HS256
DATABASE_URL=postgresql+psycopg://...
```

**User Service:**
```env
SECRET_KEY=your-secret-key  # Должен совпадать с Auth Service
ALGORITHM=HS256
USER_SERVICE_DATABASE_URL=postgresql+psycopg://...
AUTH_SERVICE_URL=http://localhost:8000
```

### Важно

1. **SECRET_KEY должен совпадать** в обоих сервисах для проверки JWT токенов
2. **AUTH_SERVICE_URL** должен указывать на работающий Auth Service
3. Для production используйте HTTPS и правильную настройку CORS

## Endpoints для интеграции

### Auth Service должен предоставить:

1. **GET /users/{id}** - получение пользователя по ID
2. **POST /users/{id}/roles** - обновление ролей (для синхронизации)
3. **POST /users/{id}/block** - блокировка пользователя
4. **POST /users/{id}/restore** - восстановление доступа

Эти endpoints могут быть внутренними (только для межсервисного взаимодействия).

## Тестирование интеграции

### Локальное тестирование

1. Запустите Auth Service:
```bash
cd /path/to/auth-service
uvicorn app.main:app --reload --port 8000
```

2. Запустите User Service:
```bash
cd /path/to/user-service
uvicorn user_service.main:app --reload --port 8001
```

3. Зарегистрируйте пользователя в Auth Service:
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

4. Получите токен:
```bash
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass123"
```

5. Создайте пользователя в User Service:
```bash
curl -X POST http://localhost:8001/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "auth_user_id": 1,
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "roles": ["PATIENT"]
  }'
```

## Troubleshooting

### Проблема: "Could not validate credentials"

**Причина:** JWT токен невалиден или SECRET_KEY не совпадает

**Решение:**
1. Проверьте, что SECRET_KEY одинаковый в обоих сервисах
2. Убедитесь, что токен не истек
3. Проверьте формат токена (должен быть "Bearer <token>")

### Проблема: "User not found"

**Причина:** Пользователь не создан в User Service

**Решение:**
1. Создайте пользователя в User Service после регистрации в Auth Service
2. Проверьте, что `auth_user_id` правильный

### Проблема: "Connection refused" при вызове Auth Service

**Причина:** Auth Service недоступен

**Решение:**
1. Проверьте, что Auth Service запущен
2. Проверьте AUTH_SERVICE_URL в переменных окружения
3. Проверьте сетевые настройки (firewall, порты)

## Production рекомендации

1. **Используйте Message Queue** (RabbitMQ, Kafka) для асинхронных событий
2. **Настройте retry механизм** для HTTP вызовов между сервисами
3. **Используйте circuit breaker** для предотвращения каскадных сбоев
4. **Мониторинг и логирование** всех межсервисных вызовов
5. **Rate limiting** для защиты от перегрузки
6. **Service mesh** (Istio, Linkerd) для управления трафиком между сервисами


