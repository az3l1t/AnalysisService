#!/bin/bash

# Скрипт для запуска PostgreSQL через Docker

echo "🚀 Запуск PostgreSQL через Docker..."

docker run -d \
  --name auth_db \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=auth_db \
  -p 5432:5432 \
  -v auth_db_data:/var/lib/postgresql/data \
  postgres:15-alpine

echo "✅ PostgreSQL запущен!"
echo "📊 База данных: auth_db"
echo "👤 Пользователь: user"
echo "🔑 Пароль: password"
echo "🔌 Порт: 5432"
echo ""
echo "Для остановки используйте: docker stop auth_db"
echo "Для удаления используйте: docker rm -v auth_db"

