#!/bin/bash

# Скрипт для завершения настройки и загрузки кода в GitHub

set -e

echo "🚀 Завершение настройки и загрузка кода в GitHub"
echo "================================================"
echo ""

# Проверка, что мы в правильной директории
if [ ! -f "requirements.txt" ]; then
    echo "❌ Файл requirements.txt не найден. Убедитесь, что вы в правильной директории."
    exit 1
fi

# Инициализация Git (если еще не инициализирован)
if [ ! -d ".git" ]; then
    echo "📦 Инициализация Git репозитория..."
    git init
    echo "✅ Git репозиторий инициализирован"
    echo ""
else
    echo "✅ Git репозиторий уже инициализирован"
    echo ""
fi

# Проверка remote
if git remote get-url origin &> /dev/null; then
    echo "✅ Remote origin уже настроен"
    git remote -v
    echo ""
    read -p "Перезаписать remote origin? (y/n): " OVERWRITE
    if [ "$OVERWRITE" = "y" ] || [ "$OVERWRITE" = "Y" ]; then
        git remote set-url origin https://github.com/Vardges1/medical-analysis-auth.git
        echo "✅ Remote origin обновлен"
    fi
else
    echo "🔗 Настройка remote origin..."
    git remote add origin https://github.com/Vardges1/medical-analysis-auth.git
    echo "✅ Remote origin настроен"
    echo ""
fi

# Проверка workflow файла
if [ -f ".github/workflows/ci-cd.yml" ]; then
    if grep -q "ghcr.io" .github/workflows/ci-cd.yml; then
        echo "✅ Workflow файл использует GitHub Container Registry"
    else
        echo "⚠️  Workflow файл не использует GitHub Container Registry"
        echo "Копирую ci-cd-ghcr.yml в ci-cd.yml..."
        cp .github/workflows/ci-cd-ghcr.yml .github/workflows/ci-cd.yml
        echo "✅ Workflow файл обновлен"
    fi
else
    echo "⚠️  Workflow файл не найден. Копирую ci-cd-ghcr.yml..."
    mkdir -p .github/workflows
    if [ -f ".github/workflows/ci-cd-ghcr.yml" ]; then
        cp .github/workflows/ci-cd-ghcr.yml .github/workflows/ci-cd.yml
        echo "✅ Workflow файл создан"
    else
        echo "❌ Файл ci-cd-ghcr.yml не найден!"
        exit 1
    fi
fi
echo ""

# Добавление файлов
echo "📝 Добавление файлов..."
git add .
echo "✅ Файлы добавлены"
echo ""

# Проверка изменений
if git diff --cached --quiet && [ -z "$(git status -s)" ]; then
    echo "⚠️  Нет изменений для коммита"
    echo "Проверьте статус: git status"
    echo ""
    read -p "Продолжить и сделать push? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
        echo "Отменено."
        exit 0
    fi
else
    echo "💾 Создание commit..."
    git commit -m "Setup CI/CD with GitHub Container Registry

- Added authentication microservice
- Configured CI/CD pipeline with GitHub Container Registry
- Added tests and Docker configuration
- Setup Yandex Cloud deployment"
    echo "✅ Commit создан"
    echo ""
fi

# Переключение на main branch
echo "🌿 Переключение на main branch..."
git branch -M main
echo "✅ Переключено на main"
echo ""

# Push в GitHub
echo "📤 Загрузка кода в GitHub..."
echo ""
read -p "Загрузить код в GitHub? (y/n): " PUSH
if [ "$PUSH" = "y" ] || [ "$PUSH" = "Y" ]; then
    echo "Загрузка..."
    git push -u origin main --force
    echo ""
    echo "✅ Код загружен в GitHub!"
    echo ""
    echo "🎉 Готово! CI/CD автоматически запустится."
    echo ""
    echo "📋 Проверьте:"
    echo "   - GitHub Actions: https://github.com/Vardges1/medical-analysis-auth/actions"
    echo "   - GitHub Packages: https://github.com/Vardges1/medical-analysis-auth/pkgs/container/medical-analysis-auth"
else
    echo ""
    echo "⚠️  Код не загружен. Загрузите вручную:"
    echo "   git push -u origin main --force"
fi

echo ""
echo "================================================"
echo "✅ Настройка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "   1. Настройте Managed PostgreSQL в Yandex Cloud"
echo "   2. Добавьте DATABASE_URL:"
echo "      gh secret set DATABASE_URL --repo Vardges1/medical-analysis-auth --body 'postgresql+psycopg://user:password@host:6432/dbname'"
echo "   3. Проверьте CI/CD в GitHub Actions"
echo ""

