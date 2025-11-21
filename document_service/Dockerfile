# Официальный лёгкий образ Python
FROM python:3.11-slim

# Не создаём .pyc-файлы, лог сразу в stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Рабочая директория внутри контейнера
WORKDIR /app

# Ставим системные зависимости (на всякий случай для reportlab)
RUN apt-get update && apt-get install -y \
    build-essential \
    libfreetype6-dev \
    libjpeg-dev \
    zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

# Сначала зависимости — для кеша
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Затем весь код приложения
COPY . .

# Порт, на котором слушает uvicorn внутри контейнера
EXPOSE 8000

# Команда запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
