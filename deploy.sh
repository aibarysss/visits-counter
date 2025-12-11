#!/bin/bash
# deploy.sh - ручной деплой на ВМ

VM_IP=$1
BRANCH=$2
IMAGE_TAG=$3

if [ -z "$VM_IP" ] || [ -z "$BRANCH" ]; then
    echo "Использование: ./deploy.sh <VM_IP> <branch> [tag]"
    echo "Пример: ./deploy.sh 192.168.1.20 main prod-v1"
    exit 1
fi

# Порт в зависимости от ветки
if [ "$BRANCH" == "main" ]; then
    PORT=80
    ENV="production"
else
    PORT=8080
    ENV="development"
fi

echo "Деплой на $VM_IP ($ENV)..."

ssh ubuntu@$VM_IP "
    # Останавливаем старый контейнер
    docker stop visits-$BRANCH 2>/dev/null || true
    docker rm visits-$BRANCH 2>/dev/null || true

    # Запускаем новый
    docker run -d \\
      --name visits-$BRANCH \\
      -p $PORT:5000 \\
      -e APP_ENV=$ENV \\
      -e REDIS_HOST=redis \\
      --network visits-network \\
      localhost:5000/visits-counter:${IMAGE_TAG:-latest}

    echo 'Контейнер запущен!'
    echo 'Проверка: curl http://localhost:$PORT/health'
"