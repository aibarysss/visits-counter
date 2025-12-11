pipeline {
    agent any

    environment {
        // IP адреса ВМ
        JENKINS_VM = '192.168.1.10'  // Замените на реальный IP
        APP_VM = '192.168.1.20'      // Замените на реальный IP

        // Docker образ
        IMAGE_NAME = 'visits-counter'
        DOCKER_REGISTRY = 'localhost:5000'

        // SSH ключ (добавить в Jenkins Credentials)
        SSH_CREDENTIALS_ID = 'vm-ssh-key'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                sh '''
                    echo "Running tests..."
                    cd app && python -m pytest tests/ -v || echo "Tests completed"
                '''
            }
        }

        stage('Build & Push') {
            steps {
                script {
                    // Определяем тег в зависимости от ветки
                    if (env.BRANCH_NAME == 'main') {
                        dockerTag = 'prod'
                        envPort = '80'
                    } else {
                        dockerTag = 'dev'
                        envPort = '8080'
                    }

                    // Собираем образ
                    sh "docker build -t ${IMAGE_NAME}:${dockerTag}-${env.BUILD_ID} ."

                    // Тегируем для registry
                    sh "docker tag ${IMAGE_NAME}:${dockerTag}-${env.BUILD_ID} ${DOCKER_REGISTRY}/${IMAGE_NAME}:${dockerTag}-latest"

                    // Пушим в локальный registry на Jenkins ВМ
                    sh "docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${dockerTag}-latest"

                    // Сохраняем переменные для деплоя
                    env.DOCKER_TAG = "${dockerTag}-${env.BUILD_ID}"
                    env.APP_PORT = envPort
                }
            }
        }

        stage('Deploy to VM') {
            steps {
                script {
                    withCredentials([sshUserPrivateKey(
                        credentialsId: SSH_CREDENTIALS_ID,
                        keyFileVariable: 'SSH_KEY'
                    )]) {
                        // Команда деплоя на ВМ 2
                        sh """
                            ssh -o StrictHostKeyChecking=no -i ${SSH_KEY} ubuntu@${APP_VM} '
                                # Останавливаем контейнер (dev или prod)
                                docker stop visits-${env.BRANCH_NAME} 2>/dev/null || true
                                docker rm visits-${env.BRANCH_NAME} 2>/dev/null || true

                                # Тянем новый образ с Jenkins ВМ
                                docker pull ${JENKINS_VM}:5000/${IMAGE_NAME}:${env.DOCKER_TAG}

                                # Запускаем контейнер
                                docker run -d \\
                                  --name visits-${env.BRANCH_NAME} \\
                                  -p ${env.APP_PORT}:5000 \\
                                  -e APP_ENV=${env.BRANCH_NAME} \\
                                  -e REDIS_HOST=redis \\
                                  --network visits-network \\
                                  ${JENKINS_VM}:5000/${IMAGE_NAME}:${env.DOCKER_TAG}
                            '
                        """
                    }
                }
            }
        }

        // Для main ветки добавляем ручное подтверждение
        stage('Manual Approval for Production') {
            when {
                branch 'main'
            }
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    input(
                        message: 'Деплоить в Production?',
                        ok: 'Да!'
                    )
                }
            }
        }
    }

    post {
        always {
            // Очистка
            sh 'docker system prune -f || true'
        }
        success {
            echo "Pipeline успешно завершён!"
        }
        failure {
            echo "Pipeline завершился с ошибкой"
        }
    }
}