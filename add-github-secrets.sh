#!/bin/bash

# Скрипт для добавления секретов в GitHub через CLI

set -e

echo "🔐 Добавление секретов в GitHub через CLI"
echo "=========================================="
echo ""

# Проверка установки GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI не установлен"
    echo ""
    echo "Установите GitHub CLI:"
    echo "  macOS: brew install gh"
    echo "  Linux: https://cli.github.com/manual/installation"
    echo ""
    exit 1
fi

# Проверка авторизации
if ! gh auth status &> /dev/null; then
    echo "⚠️  GitHub CLI не авторизован"
    echo "Выполните: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI установлен и авторизован"
echo ""

# Запрос имени репозитория
read -p "Введите имя репозитория (формат: username/repo): " REPO
if [ -z "$REPO" ]; then
    echo "❌ Имя репозитория обязательно"
    exit 1
fi

echo ""
echo "📋 Добавление секретов в репозиторий: $REPO"
echo ""

# Проверка существования key.json
if [ ! -f "key.json" ]; then
    echo "⚠️  Файл key.json не найден"
    read -p "Продолжить без YC_SA_JSON_CREDENTIALS? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        exit 1
    fi
    SKIP_KEY=true
else
    SKIP_KEY=false
fi

# Добавление секретов
if [ "$SKIP_KEY" = false ]; then
    echo "1. Добавление YC_SA_JSON_CREDENTIALS..."
    gh secret set YC_SA_JSON_CREDENTIALS --repo "$REPO" < key.json
    echo "   ✅ YC_SA_JSON_CREDENTIALS добавлен"
    echo ""
fi

echo "2. Добавление YC_FOLDER_ID..."
gh secret set YC_FOLDER_ID --repo "$REPO" --body "b1gdveljmc97oub5k85p"
echo "   ✅ YC_FOLDER_ID добавлен"
echo ""

echo "3. Добавление YC_SERVICE_ACCOUNT_ID..."
gh secret set YC_SERVICE_ACCOUNT_ID --repo "$REPO" --body "ajeinr36efvfutjutjo1"
echo "   ✅ YC_SERVICE_ACCOUNT_ID добавлен"
echo ""

echo "4. Добавление DATABASE_URL..."
read -p "Введите DATABASE_URL (или нажмите Enter для пропуска): " DB_URL
if [ -n "$DB_URL" ]; then
    gh secret set DATABASE_URL --repo "$REPO" --body "$DB_URL"
    echo "   ✅ DATABASE_URL добавлен"
else
    echo "   ⚠️  DATABASE_URL пропущен (добавьте вручную позже)"
fi
echo ""

echo "5. Добавление SECRET_KEY..."
SECRET_KEY=$(openssl rand -hex 32)
gh secret set SECRET_KEY --repo "$REPO" --body "$SECRET_KEY"
echo "   ✅ SECRET_KEY добавлен (сгенерирован автоматически)"
echo ""

echo "=========================================="
echo "✅ Секреты успешно добавлены!"
echo ""
echo "📋 Добавленные секреты:"
if [ "$SKIP_KEY" = false ]; then
    echo "   - YC_SA_JSON_CREDENTIALS"
fi
echo "   - YC_FOLDER_ID"
echo "   - YC_SERVICE_ACCOUNT_ID"
if [ -n "$DB_URL" ]; then
    echo "   - DATABASE_URL"
fi
echo "   - SECRET_KEY"
echo ""
echo "⚠️  Если DATABASE_URL не был добавлен, добавьте его вручную:"
echo "   gh secret set DATABASE_URL --repo $REPO --body 'postgresql+psycopg://user:password@host:5432/dbname'"
echo ""

