pipeline {
    agent any
    
    environment {
        JENKINS_IP = '192.168.56.10'
        APP_IP = '192.168.56.20'
        REGISTRY = "${JENKINS_IP}:5000"
        IMAGE_NAME = 'visits-counter'
        SSH_CREDENTIALS = 'vm-ssh-key'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo "🚀 CI/CD Pipeline запущен"
            }
        }

        stage('Test') {
            steps {
                sh '''
                    echo "🧪 Запуск тестов..."
                    python -m pytest app/tests/ -v
                    echo "✅ Тесты пройдены"
                '''
            }
        }

        stage('Build') {
            steps {
                sh '''
                    echo "🐳 Сборка Docker образа..."
                    # Используем переменные окружения напрямую
                    docker build -t ${JENKINS_IP}:5000/${IMAGE_NAME}:latest .
                    echo "✅ Docker образ собран"
                '''
            }
        }

        stage('Push') {
            steps {
                sh '''
                    echo "📤 Отправка в registry..."
                    docker push ${JENKINS_IP}:5000/${IMAGE_NAME}:latest
                    echo "✅ Образ отправлен в registry"
                '''
            }
        }

        stage('Deploy Instructions') {
            steps {
                sh """
                    echo "🚀 ИНСТРУКЦИЯ ДЛЯ ДЕПЛОЯ:"
                    echo ""
                    echo "1. Для запуска приложения на ВМ2:"
                    echo "   docker pull ${JENKINS_IP}:5000/${IMAGE_NAME}:latest"
                    echo "   docker run -d -p 8080:5000 --name visits-app ${JENKINS_IP}:5000/${IMAGE_NAME}:latest"
                    echo ""
                    echo "2. Проверка:"
                    echo "   curl http://${APP_IP}:8080/health"
                    echo ""
                    echo "🎉 ПАЙПЛАЙН УСПЕШНО ЗАВЕРШЁН!"
                """
            }
        }
    }

    post {
        always {
            echo "📊 Pipeline завершён"
            echo "🌐 Jenkins: http://${JENKINS_IP}:8080"
            echo "🌐 Приложение: http://${APP_IP}:8080"
        }
        success {
            echo "✅ ВСЕ ЭТАПЫ ВЫПОЛНЕНЫ УСПЕШНО!"
        }
    }
}