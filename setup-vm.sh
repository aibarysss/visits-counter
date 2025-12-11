#!/bin/bash
# setup-vm.sh - настройка виртуальной машины

echo "=== Настройка ВМ для Visits Counter ==="

# 1. Обновление системы
echo "1. Обновление системы..."
sudo apt update
sudo apt upgrade -y

# 2. Установка Docker
echo "2. Установка Docker..."
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker

# 3. Добавление пользователя в группу docker
echo "3. Добавление пользователя в docker группу..."
sudo usermod -aG docker $USER

# 4. Настройка Docker (только для ВМ 2 - App Server)
if [ "$1" == "app" ]; then
    echo "4. Настройка Docker для App Server..."

    # Создаём сеть
    sudo docker network create visits-network

    # Запускаем Redis
    sudo docker run -d \
      --name redis \
      --network visits-network \
      -v redis_data:/data \
      redis:alpine

    # Разрешаем insecure registry (для образа с Jenkins ВМ)
    echo '{
      "insecure-registries": ["'${JENKINS_IP}':5000"]
    }' | sudo tee /etc/docker/daemon.json

    sudo systemctl restart docker

    echo "App Server настроен!"
else
    echo "4. Настройка Docker для Jenkins Server..."

    # Запускаем Jenkins
    sudo docker run -d \
      --name jenkins \
      -p 8080:8080 -p 50000:50000 \
      -v jenkins_home:/var/jenkins_home \
      -v /var/run/docker.sock:/var/run/docker.sock \
      jenkins/jenkins:lts-jdk17

    # Запускаем локальный Docker Registry
    sudo docker run -d \
      --name registry \
      -p 5000:5000 \
      -v registry_data:/var/lib/registry \
      registry:2

    echo "Jenkins Server настроен!"
    echo "Jenkins доступен по: http://$(curl -s ifconfig.me):8080"
fi

echo "=== Настройка завершена ==="