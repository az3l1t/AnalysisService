#!/bin/bash

# Скрипт для тестирования API

BASE_URL="http://localhost:8000"

echo "🧪 Тестирование API микросервиса аутентификации"
echo "================================================"
echo ""

# 1. Health check
echo "1️⃣  Health Check:"
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""
echo ""

# 2. Регистрация пользователя
echo "2️⃣  Регистрация пользователя:"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
  }')

echo "$REGISTER_RESPONSE" | python3 -m json.tool
echo ""

# 3. Получение токена
echo "3️⃣  Получение токена:"
TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpassword123")

echo "$TOKEN_RESPONSE" | python3 -m json.tool
TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo ""

# 4. Получение информации о текущем пользователе
echo "4️⃣  Получение информации о текущем пользователе:"
curl -s -X GET "$BASE_URL/users/me" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "✅ Тестирование завершено!"

