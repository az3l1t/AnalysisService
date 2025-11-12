# Инструкция по установке

## Решение проблемы "command not found: pip"

На macOS команда `pip` может быть недоступна. Используйте следующие команды:

### 1. Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Установка зависимостей

```bash
# Обновите pip, setuptools и wheel
python3 -m pip install --upgrade pip setuptools wheel

# Установите зависимости
pip install -r requirements.txt
```

### 3. Альтернативные команды

Если `pip` не работает, используйте:
- `python3 -m pip` вместо `pip`
- `python3` вместо `python`

### 4. Проверка установки

```bash
# Проверьте версию Python
python3 --version

# Проверьте установленные пакеты
pip list

# Запустите тесты
pytest
```

## Запуск приложения

### Локально (требуется PostgreSQL)

1. Установите и запустите PostgreSQL
2. Создайте файл `.env`:
```bash
cp env.example .env
# Отредактируйте .env с вашими настройками БД
```

3. Запустите приложение:
```bash
uvicorn app.main:app --reload
```

### Через Docker Compose

```bash
docker-compose up -d
```

Приложение будет доступно на http://localhost:8000

## Устранение проблем

### Проблема: "ModuleNotFoundError: No module named 'bcrypt'"

Решение: Убедитесь, что виртуальное окружение активировано и зависимости установлены:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Проблема: "Connection refused" при запуске тестов

Решение: Тесты используют SQLite и не требуют PostgreSQL. Убедитесь, что вы запускаете тесты в виртуальном окружении.

### Проблема: Ошибки компиляции при установке зависимостей

Решение: Обновите pip и setuptools:
```bash
python3 -m pip install --upgrade pip setuptools wheel
```

