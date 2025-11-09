#!/bin/bash

# Скрипт для автоматической настройки Yandex Cloud для CI/CD

set -e

echo "🚀 Настройка Yandex Cloud для CI/CD"
echo "===================================="
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Проверка установки YC CLI
# Проверяем несколько возможных путей
if ! command -v yc &> /dev/null; then
    # Пробуем добавить путь вручную
    if [ -f "$HOME/yandex-cloud/bin/yc" ]; then
        export PATH="$HOME/yandex-cloud/bin:$PATH"
    else
        echo -e "${RED}❌ Yandex Cloud CLI не установлен${NC}"
        echo "Установите его: https://cloud.yandex.ru/docs/cli/quickstart"
        echo "Или выполните: source ~/.zshrc"
        exit 1
    fi
fi

# Проверка инициализации
if ! yc config list &> /dev/null; then
    echo -e "${YELLOW}⚠️  YC CLI не инициализирован${NC}"
    echo "Выполните инициализацию:"
    echo "  1. source ~/.zshrc  (если еще не сделали)"
    echo "  2. yc init"
    echo ""
    echo "После инициализации запустите этот скрипт снова."
    exit 1
fi

echo -e "${GREEN}✅ Yandex Cloud CLI установлен и настроен${NC}"
echo ""

# Запрос параметров
read -p "Введите имя сервисного аккаунта [github-actions-deploy]: " SA_NAME
SA_NAME=${SA_NAME:-github-actions-deploy}

read -p "Введите имя Container Registry [medical-analysis-registry]: " REGISTRY_NAME
REGISTRY_NAME=${REGISTRY_NAME:-medical-analysis-registry}

# Попытка получить ID папки из конфигурации
CURRENT_FOLDER_ID=$(yc config get folder-id 2>/dev/null || echo "")

if [ -n "$CURRENT_FOLDER_ID" ]; then
    read -p "Введите ID папки [$CURRENT_FOLDER_ID]: " FOLDER_ID
    FOLDER_ID=${FOLDER_ID:-$CURRENT_FOLDER_ID}
else
    echo "Доступные папки:"
    yc resource-manager folder list --format json | jq -r '.[] | "  \(.id) - \(.name)"' || echo "  (не удалось получить список)"
    echo ""
    read -p "Введите ID папки (folder-id): " FOLDER_ID
fi

if [ -z "$FOLDER_ID" ]; then
    echo -e "${RED}❌ ID папки обязателен${NC}"
    echo "Получите ID папки командой: yc resource-manager folder list"
    exit 1
fi

echo ""
echo "📋 Создание сервисного аккаунта..."
SA_ID=$(yc iam service-account create --name "$SA_NAME" --folder-id "$FOLDER_ID" --format json 2>/dev/null | jq -r '.id' || yc iam service-account get --name "$SA_NAME" --folder-id "$FOLDER_ID" --format json | jq -r '.id')

if [ -z "$SA_ID" ]; then
    echo -e "${RED}❌ Ошибка создания сервисного аккаунта${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Сервисный аккаунт создан: $SA_ID${NC}"

echo ""
echo "🔐 Назначение ролей..."
yc resource-manager folder add-access-binding "$FOLDER_ID" \
  --role container-registry.images.pusher \
  --subject serviceAccount:$SA_ID 2>/dev/null || echo "Роль уже назначена"

yc resource-manager folder add-access-binding "$FOLDER_ID" \
  --role container-registry.images.puller \
  --subject serviceAccount:$SA_ID 2>/dev/null || echo "Роль уже назначена"

yc resource-manager folder add-access-binding "$FOLDER_ID" \
  --role serverless.containers.deployer \
  --subject serviceAccount:$SA_ID 2>/dev/null || echo "Роль уже назначена"

yc resource-manager folder add-access-binding "$FOLDER_ID" \
  --role serverless.containers.editor \
  --subject serviceAccount:$SA_ID 2>/dev/null || echo "Роль уже назначена"

yc resource-manager folder add-access-binding "$FOLDER_ID" \
  --role serverless.containers.admin \
  --subject serviceAccount:$SA_ID 2>/dev/null || echo "Роль уже назначена"

echo -e "${GREEN}✅ Роли назначены${NC}"

echo ""
echo "🔑 Создание ключа..."
yc iam key create --service-account-id "$SA_ID" --output key.json --format json
echo -e "${GREEN}✅ Ключ создан и сохранен в key.json${NC}"

echo ""
echo "📦 Создание Container Registry..."
# Попытка создать реестр или получить существующий
REGISTRY_OUTPUT=$(yc container registry create --name "$REGISTRY_NAME" --folder-id "$FOLDER_ID" --format json 2>&1)
REGISTRY_ID=$(echo "$REGISTRY_OUTPUT" | jq -r '.id' 2>/dev/null || echo "")

# Если не удалось создать, попробуем получить существующий
if [ -z "$REGISTRY_ID" ] || [ "$REGISTRY_ID" == "null" ]; then
    echo "Попытка найти существующий реестр..."
    REGISTRY_ID=$(yc container registry list --folder-id "$FOLDER_ID" --format json 2>/dev/null | jq -r ".[] | select(.name == \"$REGISTRY_NAME\") | .id" | head -1)
    
    if [ -z "$REGISTRY_ID" ]; then
        echo -e "${YELLOW}⚠️  Не удалось создать реестр автоматически${NC}"
        echo "Попробуйте создать реестр вручную через консоль:"
        echo "  https://console.cloud.yandex.ru/folders/$FOLDER_ID/cloud/registry"
        echo ""
        echo "Или выполните команду:"
        echo "  yc container registry create --name $REGISTRY_NAME --folder-id $FOLDER_ID"
        echo ""
        read -p "Введите ID существующего реестра (или оставьте пустым для пропуска): " REGISTRY_ID
        if [ -z "$REGISTRY_ID" ]; then
            echo -e "${YELLOW}⚠️  Пропускаем создание реестра. Вы сможете создать его позже.${NC}"
            REGISTRY_ID="<REGISTRY_ID>"
        fi
    else
        echo -e "${GREEN}✅ Найден существующий реестр: $REGISTRY_ID${NC}"
    fi
else
    echo -e "${GREEN}✅ Container Registry создан: $REGISTRY_ID${NC}"
fi

echo ""
echo "===================================="
if [ "$REGISTRY_ID" == "<REGISTRY_ID>" ]; then
    echo -e "${YELLOW}⚠️  Настройка почти завершена!${NC}"
    echo ""
    echo "❌ Container Registry не был создан автоматически."
    echo "📋 Следуйте инструкциям в файле REGISTRY_SETUP.md"
    echo ""
    echo "Или создайте реестр вручную:"
    echo "  1. Откройте: https://console.cloud.yandex.ru/folders/$FOLDER_ID/cloud/registry"
    echo "  2. Создайте реестр с именем: $REGISTRY_NAME"
    echo "  3. Получите ID реестра и добавьте его в GitHub Secrets как YC_REGISTRY_ID"
    echo ""
else
    echo -e "${GREEN}✅ Настройка завершена!${NC}"
    echo ""
fi

echo "📋 Добавьте следующие секреты в GitHub:"
echo "   Settings → Secrets and variables → Actions → New repository secret"
echo ""
echo "1. YC_SA_JSON_CREDENTIALS"
echo "   Значение: содержимое файла key.json"
echo "   Команда: cat key.json"
echo ""
if [ "$REGISTRY_ID" != "<REGISTRY_ID>" ]; then
    echo "2. YC_REGISTRY_ID"
    echo "   Значение: $REGISTRY_ID"
    echo ""
else
    echo "2. YC_REGISTRY_ID"
    echo "   Значение: (создайте реестр и получите ID из консоли)"
    echo "   Команда: yc container registry list --folder-id $FOLDER_ID"
    echo ""
fi
echo "3. YC_FOLDER_ID"
echo "   Значение: $FOLDER_ID"
echo ""
echo "4. YC_SERVICE_ACCOUNT_ID"
echo "   Значение: $SA_ID"
echo ""
echo "5. DATABASE_URL"
echo "   Значение: postgresql+psycopg://user:password@host:5432/db"
echo "   (настройте PostgreSQL в Yandex Cloud или используйте внешний)"
echo ""
echo "6. SECRET_KEY"
echo "   Значение: (сгенерируйте случайный ключ)"
echo "   Команда: openssl rand -hex 32"
echo ""
echo -e "${YELLOW}⚠️  Важно: Сохраните файл key.json в безопасном месте!${NC}"
echo ""
echo "📚 Дополнительная информация:"
echo "   - REGISTRY_SETUP.md - инструкция по созданию реестра"
echo "   - CI_CD_QUICKSTART.md - настройка CI/CD"
echo ""

