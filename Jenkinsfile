# Создайте файл Jenkinsfile
@"
pipeline {
    agent any
    
    environment {
        IMAGE_NAME = 'visits-counter'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo '📦 Код получен'
            }
        }
        
        stage('Test') {
            steps {
                sh '''
                    echo "🧪 Запуск тестов..."
                    python -m pytest app/tests/ -v
                '''
            }
        }
        
        stage('Build') {
            steps {
                sh '''
                    echo "🐳 Сборка Docker образа..."
                    docker build -t \${IMAGE_NAME}:\${BUILD_ID} .
                    echo "✅ Образ собран"
                '''
            }
        }
    }
    
    post {
        always {
            echo '📊 Pipeline завершён'
        }
    }
}
"@ | Out-File -FilePath Jenkinsfile -Encoding UTF8