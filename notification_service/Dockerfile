# Лёгкий образ Python
FROM python:3.11-slim

# Не создаём .pyc, лог в stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Рабочая директория внутри контейнера
WORKDIR /app

# Ставим зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код сервиса
COPY . .

# Порт внутри контейнера
EXPOSE 8100

# Запуск FastAPI через uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8100"]
