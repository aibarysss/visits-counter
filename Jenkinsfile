pipeline {
    agent any
    
    environment {
        // VirtualBox IP адреса
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
                script {
                    TAG = "build-${BUILD_ID}"
                    env.FULL_IMAGE = "${REGISTRY}/${IMAGE_NAME}:${TAG}"
                    
                    sh """
                        echo "🐳 Сборка Docker образа..."
                        docker build -t ${env.FULL_IMAGE} .
                        echo "✅ Образ: ${env.FULL_IMAGE}"
                    """
                }
            }
        }
        
        stage('Push') {
            steps {
                sh """
                    echo "📤 Отправка в registry..."
                    docker push ${env.FULL_IMAGE}
                    echo "✅ Образ отправлен"
                '''
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    withCredentials([sshUserPrivateKey(
                        credentialsId: SSH_CREDENTIALS,
                        keyFileVariable: 'SSH_KEY'
                    )]) {
                        sh """
                            echo "🚀 Деплой на App VM..."
                            ssh -o StrictHostKeyChecking=no -i ${SSH_KEY} ubuntu@${APP_IP} "
                                echo '=== Начало деплоя ==='
                                
                                # Останавливаем старый контейнер
                                docker stop visits-app 2>/dev/null || true
                                docker rm visits-app 2>/dev/null || true
                                
                                # Скачиваем новый образ
                                docker pull ${env.FULL_IMAGE}
                                
                                # Запускаем приложение
                                docker run -d \\
                                  --name visits-app \\
                                  -p 8080:5000 \\
                                  -e REDIS_HOST=redis \\
                                  --network visits-network \\
                                  ${env.FULL_IMAGE}
                                  
                                echo '✅ Приложение запущено'
                                echo 'Проверка: curl http://localhost:8080/health'
                            "
                        """
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo "📊 Pipeline завершён"
            echo "🌐 Приложение: http://${APP_IP}:8080"
            echo "🏥 Health check: http://${APP_IP}:8080/health"
        }
    }
}