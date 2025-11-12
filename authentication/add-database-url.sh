#!/bin/bash

# Скрипт для добавления DATABASE_URL в GitHub Secrets

set -e

echo "🔐 Добавление DATABASE_URL в GitHub Secrets"
echo "============================================"
echo ""

# Проверка GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI не установлен"
    echo "Установите: brew install gh"
    exit 1
fi

# Проверка авторизации
if ! gh auth status &> /dev/null; then
    echo "❌ GitHub CLI не авторизован"
    echo "Выполните: gh auth login"
    exit 1
fi

REPO="Vardges1/medical-analysis-auth"

echo "Подключение к Supabase:"
echo "  Host: db.rxqynjbxaebrhhrewixb.supabase.co"
echo "  Port: 5432"
echo "  Database: postgres"
echo "  User: postgres"
echo ""

# Запрос пароля
read -sp "Введите пароль из Supabase (или нажмите Enter для пропуска): " DB_PASSWORD
echo ""

if [ -z "$DB_PASSWORD" ]; then
    echo "⚠️  Пароль не введен. Пропускаем."
    echo ""
    echo "Чтобы добавить позже, выполните:"
    echo "  gh secret set DATABASE_URL --repo $REPO --body 'postgresql+psycopg://postgres:YOUR_PASSWORD@db.rxqynjbxaebrhhrewixb.supabase.co:5432/postgres'"
    exit 0
fi

# Формируем DATABASE_URL
DATABASE_URL="postgresql+psycopg://postgres:${DB_PASSWORD}@db.rxqynjbxaebrhhrewixb.supabase.co:5432/postgres"

echo ""
echo "📋 Добавление DATABASE_URL в GitHub Secrets..."
gh secret set DATABASE_URL --repo "$REPO" --body "$DATABASE_URL"

echo ""
echo "✅ DATABASE_URL успешно добавлен!"
echo ""
echo "📋 Что дальше:"
echo "   1. Деплой запустится автоматически при следующем push"
echo "   2. Или сделайте пустой коммит:"
echo "      git commit --allow-empty -m 'Trigger deployment'" 
echo "      git push origin main"
echo "   3. Проверьте статус в GitHub Actions"
echo ""

